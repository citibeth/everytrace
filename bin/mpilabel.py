#!/usr/bin/env python
#
# Runs a command, massaging the output in two ways:
#	a) Each line of STDOUT is prefixed with the MPI rank (eg: [o17])
#	b) Each line of STDERR is prefixed with the MPI rank and sent to STDOUT (eg: [e17])
#
# The resulting log file can later be grepped, for example:
#	 * All output from MPI Rank 2:
#		   grep '^\[.2' log
#	 * STDERR from all MPI ranks:
#		   grep '^\[e' log
#
# Usage: mpilabel command...
# Usage with MPI: mpirun -np 17 mpilabel command...
#
# See: http://stackoverflow.com/questions/12270645/can-you-make-a-python-subprocess-output-stdout-and-stderr-as-usual-but-also-cap

import os
import subprocess
import sys
import select

rank = int(os.environ['OMPI_COMM_WORLD_RANK'])

out_prefix = '[o%d]' % rank
err_prefix = '[e%d]' % rank

p = subprocess.Popen(sys.argv[1:],
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)

exit_me = False
while True:
	reads = [p.stdout.fileno(), p.stderr.fileno()]
	ret = select.select(reads, [], [])

	input_detected = False
	for fd in ret[0]:
		if fd == p.stdout.fileno():
			read = p.stdout.readline().decode()
			if len(read) > 0:
				input_detected = True
				sys.stdout.write(out_prefix)
				sys.stdout.write(read)
		if fd == p.stderr.fileno():
			read = p.stderr.readline().decode()
			if len(read) > 0:
				input_detected = True
				sys.stdout.write(err_prefix)
				sys.stdout.write(read)

	if exit_me and not input_detected:
		break

	if p.poll() != None:
		exit_me = True
