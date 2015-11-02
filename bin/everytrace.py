#!/usr/bin/env python
#

import sys
import re
import subprocess
import io

# -------------------------------------------

taggedRE = re.compile(r'\[((e)(\d+))\](.*)')
def tag_reader(fin):
	for line in fin:
		match = taggedRE.match(line)
		if match:
			yield match.group(1), match.group(4)	# tag, line
		else:
			# Assign everythign in unlabelled file to stderr on rank 0.
			# This allows us to work without MPI.
			yield 'e0',line


# -------------------------------------------
S_INITIAL=0
S_STACKTRACE=1

tag_vars = dict()
libs = set()			# Set of library names in use
ref_addrs_lib=dict()	# library name --> addr of everytrace_refaddr in the lib

# -------------------------------------------
nmRE = re.compile(r'([0-9a-fA-F]+)\s+t\s+_everytrace_refaddr\s*')
def read_refaddr(exe_fname):

	cmd = ['nm', exe_fname]
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	out,err = proc.communicate()

	for line in io.StringIO(out.decode()):
		match = nmRE.match(line)
		if match is None: continue
		addr = int(match.group(1), 16)
		return addr


log_fname = sys.argv[1]

# ------------ Parse the log
ref_addrRE = re.compile(r'^EVERYTRACE REFERENCE:\s*"(.*?)"\s*(0x[0-9a-fA-F]+)')
tracelineRE = re.compile(r'#\d*\s*(0x[0-9a-fA-F]+)')

# ---------- Open the log
if log_fname == '-':
	fin = sys.stdin
else:
	fin = open(log_fname, 'r')
fin = tag_reader(fin)



# ref_addrs = dict()	# ref_symbol --> ref_addr_r

#stacktraceRE=re.compile(r'^\s*((Backtrace for this error)|(Program aborted. Backtrace\:)|(User stacktrace\:)|(Exiting via PISMEnd))')
stacktraceRE=re.compile(r'^\s*(Everytrace Dump,).*')

for tag,line in fin:
	# ---------- Add to our dict if we need to
	if tag in tag_vars:
		vars = tag_vars[tag]
	else:
		vars = dict( \
			state=S_INITIAL,		# Log parser state
			ref_addrs_log=dict(),	# library name --> address of everytrace_refaddr in the log
			stacktrace_r=list(),	# Raw numeric stacktrace from log
			stacktrace_merged=list())	# Final stacktrace after lookups
		tag_vars[tag] = vars

	state = vars['state']
	if state == S_INITIAL:
		match = ref_addrRE.match(line)
		if match is not None:
			lib_name = match.group(1)
			ref_addr_r = int(match.group(2), 0)
			libs.add(lib_name)
			#print('Parsed refaddr', tag, lib_name, ref_addr_r)
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

if log_fname != '-': fin.close()

#for tag in iter(tag_vars):
#	print(tag, tag_vars[tag]['ref_addrs_log'])
#	print(tag, tag_vars[tag]['stacktrace_r'])

# ------------ Look up all stacktraces for each library
for lib in libs:
	# Get the location of refaddr in this library
	ref_addr_lib = read_refaddr(lib)

	# Combine stacktraces from all tags for this one library.
	all_stacktrace_lines = list()		# Start with a newline
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
	cmd = ['xcrun', 'atos', '-o', lib]
	proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	input = ('\n'.join(all_stacktrace_lines)).encode()
	ret = proc.communicate(input)[0].decode()
	ret_per_tag = ret.split('tag:')

	for chunk in ret_per_tag[1:]:
		lines = chunk.split('\n')
		tag = lines[0]
		vars = tag_vars[tag]
		stacktrace_merged = vars['stacktrace_merged']
		ret_lines = lines[1:]
		if (len(ret_lines[-1]) == 0):
			ret_lines = ret_lines[:-1]

		for (i,v0),v1 in zip(enumerate(vars['stacktrace_lines']),ret_lines):
			if v0 != v1:
				stacktrace_merged[i] = v1

for tag in sorted(iter(list(tag_vars))):
	stacktrace_merged = tag_vars[tag]['stacktrace_merged']
	print('------------ {}'.format(tag))
	print('\n'.join(stacktrace_merged))
