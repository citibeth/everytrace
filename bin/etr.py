#!/usr/bin/env python
#
from __future__ import print_function

import sys
import re
import subprocess
import io
import platform
import os
import collections
import StringIO

FrameInfo = collections.namedtuple('FrameInfo', ['saddr', 'addr', 'src_line', 'obj_file', 'symbol'])

# -------------------------------------------
def stderr_reader(fin):
    """Generator reads just the stderr from the output of OpenMPI when
    mpirun is called with -timestamp-output.  Lines look like:
        'Wed May 11 14:36:52 2016<stdout>: ARG I'
    """
    for line in fin:
        if line[28] == 'e':
            yield line[33:]
# -------------------------------------------
def log_file_list(log_dirs):
    """Returns a list of log files to open"""
    ret = list()
    for log_dir in log_dirs:
        if log_dir == '-':
            ret.append('-')
        elif os.path.isfile(log_dir):
            ret.append(log_dir)
        else:
            ret += [os.path.join(log_dir, x) for x in sorted(os.listdir(log_dir))]
    return ret

def open_files(fnames):
    """Generator opens all files in a directory, in sequence.
    Yields: (leafname, open filehandle)
    log_dir:
        Directory to open.
        If '-', then just open STDIN."""

    for fname in fnames:
        if fname == '-':
            yield fname,sys.stdin
        else:
            with open(fname, 'r') as fin:
                yield fname, fin

# -------------------------------------------
# Finite state machine as we parse through STDERR.
S_INITIAL=0
S_STACKTRACE=1

tag_vars = dict()
libs = set()            # Set of library names in use
ref_addrs_lib=dict()    # library name --> addr of everytrace_refaddr in the lib

# -------------------------------------------
nmRE = re.compile(r'([0-9a-fA-F]+)\s+[tT]\s+_everytrace_refaddr\s*')
def read_refaddr(exe_fname):
    """Given the name of an executable (or .so) file, determines the value
    of the reference address inside it.  This is used to produce an
    offset between symbols as loded in memory, and symbols on disk.
    """

    cmd = ['nm', exe_fname]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out,err = proc.communicate()

    for line in io.StringIO(out.decode()):
        match = nmRE.match(line)
        if match is None: continue
        addr = int(match.group(1), 16)
        return addr


log_dirs = sys.argv[1:]

# ------------ Parse the log
ref_addrRE = re.compile(r'^_EVERYTRACE_ REFERENCE\s+"(.*?)"\s*(0x[0-9a-fA-F]+)')
tracelineRE = re.compile(r'#\d*\s*(0x[0-9a-fA-F]+)\s*(.*)')
# Optional part of trace line, if C tracing used.
# Eg: #3 0x7f45b1b49d8a /home/me/ettest/build/libettestlib.so(_Z5main4Pci+0x4a)[0x7f45b1b49d8a]
ctraceRE = re.compile(r'(.*?)\((.*?)\+(.*?)\)\[(.*?)\]')

# ---------- Open the log(s)
log_files = log_file_list(log_dirs)
use_mpi = (len(log_files) > 1)
for fname,fin in open_files(log_files):
    tag = os.path.split(fname)[1]
    stacktraceRE=re.compile(r'^\s*(_EVERYTRACE_ DUMP:|Backtrace for this error:).*')

    if use_mpi:
        fin = stderr_reader(fin)

    for line in fin:
        # ---------- Add to our dict if we need to
        if tag in tag_vars:
            vars = tag_vars[tag]
        else:
            vars = dict( \
                state=S_INITIAL,        # Log parser state
                ref_addrs_log=dict(),    # library name --> address of everytrace_refaddr in the log
                raw_lines=list(),        # Raw lines from output to show with stacktrace
                stacktrace=list())    # FrameInfo: saddr, src_line, obj_file, symbol
            tag_vars[tag] = vars

        if line.startswith('_EVERYTRACE_'):
            colon = line.find(':')
            if colon >= 0:
                vars['raw_lines'].append(line[colon+1:].strip())

        state = vars['state']
        if state == S_INITIAL:
            match = ref_addrRE.match(line)
            if match is not None:
                lib_name = match.group(1)
                ref_addr_r = int(match.group(2), 0)
                libs.add(lib_name)
                vars['ref_addrs_log'][lib_name] = ref_addr_r
                continue

            match = stacktraceRE.match(line)
            if match is not None:
                vars['state'] = S_STACKTRACE

        elif state == S_STACKTRACE:
            match = tracelineRE.match(line)
            if match is not None:
                addr = match.group(1)

                # match optional stuff...
                object_file = None
                symbol = None
                ctrace = match.group(2)
                if ctrace is not None:
                    match2 = ctraceRE.match(ctrace)
                    if match2 is not None:
                        object_file = match2.group(1)
                        symbol = match2.group(2)


                vars['stacktrace'].append(FrameInfo(addr, int(addr,0), [], object_file, symbol))

#for tag in iter(tag_vars):
#    print(tag, tag_vars[tag]['ref_addrs_log'])
#    print(tag, tag_vars[tag]['stacktrace'])


print('======== Resolving Everytrace-enabled binaries:')
for lib in libs:
    print('  ', lib)

# ------------ Look up all stacktraces for each library
for lib in libs:
    # Get the location of refaddr in this library
    ref_addr_lib = read_refaddr(lib)
    print('ref_addr_lib', ref_addr_lib, lib)

    # Combine stacktraces from all tags for this one library.
    all_stacktrace_lines = list()        # Start with a newline
    for tag in sorted(list(iter(tag_vars))):
        vars = tag_vars[tag]
        ref_addrs_log = vars['ref_addrs_log']

        # Only do this (lib,tag) combo if we have a reference ID for
        # this lib in this tag.
        if lib in ref_addrs_log:
            ref_offset = ref_addr_lib - vars['ref_addrs_log'][lib]
            this_stacktrace_lines = ['%x' % (x.addr + ref_offset) for x in vars['stacktrace']]
            vars['stacktrace_lines'] = this_stacktrace_lines

            all_stacktrace_lines.append('tag:'+tag)
            all_stacktrace_lines += this_stacktrace_lines

    # Look up symbols
    if platform.system() == 'Linux':
        cmd = ['addr2line', '-e', lib]
        for line in all_stacktrace_lines:
            if line[0] == '-':
                cmd.append('0')
            else:
                cmd.append(line)
        print(' '.join(cmd))

        # Run the cmd and capture output
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ret = p.stdout.read().decode()
        p.wait()

    else:    # Macintosh
        cmd = ['xcrun', 'atos', '-o', lib]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        input = ('\n'.join(all_stacktrace_lines)).encode()
        ret = proc.communicate(input)[0].decode()

    ret_lines = ret.split('\n')

    for (i,src),src_line in zip(enumerate(all_stacktrace_lines), ret_lines):
        if src[0:4] == 'tag:':
            tag = src[4:]
            vars = tag_vars[tag]
            stacktrace = vars['stacktrace']
            i0=i+1
        else:
            ix = i-i0
            if (src_line[0] != '?') and (src_line != src):
                stacktrace[ix].src_line.append(src_line)

# Generate the final output
buf = StringIO.StringIO()

for tag in sorted(iter(list(tag_vars))):
    vars = tag_vars[tag]
    strace = []
    info_last = True
    for frame in vars['stacktrace']:
        sout = []
        if len(frame.src_line) > 0:
            sout.extend(frame.src_line)
        elif frame.obj_file is not None:
            sout.append(os.path.split(frame.obj_file)[1])

        if frame.symbol is not None:
            sout.append(frame.symbol)

        if len(sout) == 0:
            sout = [frame.saddr]

        strace.append(' '.join(sout))

    if len(vars['raw_lines']) + len(strace) > 0:
        buf.write('=============== {}\n'.format(tag))
        buf.write('\n'.join(vars['raw_lines']))
        buf.write('\n')
        for line in strace:
            buf.write('  ')
            buf.write(line)
            buf.write('\n')

# Pipe the final output through c++filt
filt = subprocess.Popen(['c++filt'], stdin=subprocess.PIPE)
filt.communicate(buf.getvalue())
filt.wait()

