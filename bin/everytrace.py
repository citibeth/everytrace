#!/usr/bin/env python
#
from __future__ import print_function

import sys
import re
import subprocess
import io
import platform
import os

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
def open_files_in_dir(log_dir):
    """Generator opens all files in a directory, in sequence.
    Yields: (leafname, open filehandle)
    log_dir:
        Directory to open.
        If '-', then just open STDIN."""

    if log_dir == '-':
        yield '<stdin>',sys.stdin
    elif os.path.isfile(log_dir):
        with open(log_dir, 'r') as fin:
            yield fname,fin
    else:
        for fname in sorted(os.listdir(log_dir)):
            with open(os.path.join(log_dir, fname), 'r') as fin:
                yield fname,fin

# -------------------------------------------
# Finite state machine as we parse through STDERR.
S_INITIAL=0
S_STACKTRACE=1

tag_vars = dict()
libs = set()            # Set of library names in use
ref_addrs_lib=dict()    # library name --> addr of everytrace_refaddr in the lib

# -------------------------------------------
nmRE = re.compile(r'([0-9a-fA-F]+)\s+t\s+_everytrace_refaddr\s*')
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


log_dir = sys.argv[1]

# ------------ Parse the log
ref_addrRE = re.compile(r'^_EVERYTRACE_ REFERENCE\s+"(.*?)"\s*(0x[0-9a-fA-F]+)')
tracelineRE = re.compile(r'#\d*\s*(0x[0-9a-fA-F]+)')

# ---------- Open the log(s)
for tag,fin in open_files_in_dir(log_dir):
    stacktraceRE=re.compile(r'^\s*(_EVERYTRACE_ DUMP:).*')

    for line in stderr_reader(fin):

        # ---------- Add to our dict if we need to
        if tag in tag_vars:
            vars = tag_vars[tag]
        else:
            vars = dict( \
                state=S_INITIAL,        # Log parser state
                ref_addrs_log=dict(),    # library name --> address of everytrace_refaddr in the log
                raw_lines=list(),        # Raw lines from output to show with stacktrace
                stacktrace_r=list(),    # Raw numeric stacktrace from log
                stacktrace_merged=list())    # Final stacktrace after lookups
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
                vars['stacktrace_r'].append(int(addr, 0))
                vars['stacktrace_merged'].append(addr)

#for tag in iter(tag_vars):
#    print(tag, tag_vars[tag]['ref_addrs_log'])
#    print(tag, tag_vars[tag]['stacktrace_r'])


print('======== Resolving Everytrace-enabled binaries:')
for lib in libs:
    print('  ', lib)

# ------------ Look up all stacktraces for each library
for lib in libs:
    # Get the location of refaddr in this library
    ref_addr_lib = read_refaddr(lib)

    # Combine stacktraces from all tags for this one library.
    all_stacktrace_lines = list()        # Start with a newline
    for tag in sorted(list(iter(tag_vars))):
        vars = tag_vars[tag]
        ref_addrs_log = vars['ref_addrs_log']

        # Only do this (lib,tag) combo if we have a reference ID for
        # this lib in this tag.
        if lib in ref_addrs_log:
            ref_offset = ref_addr_lib - vars['ref_addrs_log'][lib]
            this_stacktrace_lines = ['%x' % (x + ref_offset) for x in vars['stacktrace_r']]
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

    for (i,src),sym in zip(enumerate(all_stacktrace_lines), ret_lines):
        if src[0:4] == 'tag:':
            tag = src[4:]
            vars = tag_vars[tag]
            stacktrace_merged = vars['stacktrace_merged']
            i0=i+1
        else:
            if (sym[0] != '?') and (sym != src):
                if isinstance(stacktrace_merged[i-i0], str):
                    stacktrace_merged[i-i0] = [sym,]
                else:
                    stacktrace_merged[i-i0].append(sym)


for tag in sorted(iter(list(tag_vars))):
    vars = tag_vars[tag]
    strace = []
    last_type = None
    for syms in vars['stacktrace_merged']:
        if isinstance(syms, str):    # Hex address never converted
            if last_type != str:
                strace.append('...')
                last_type = str
        else:
            strace.append(' '.join(syms))
            last_type = tuple

    if len(vars['raw_lines']) + len(strace) > 0:
        print('=============== {}'.format(tag))
        print('\n'.join(vars['raw_lines']))
        for line in strace:
            print('  ', line)
