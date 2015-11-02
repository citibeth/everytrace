#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#include "dump.h"


void everytrace_exit(int retcode)
{
  fprintf(stderr, "Everytrace Dump, exit: %d\n", retcode);
#ifdef USE_BACKTRACE
	everytrace_dump();

	MPI_Abort(MPI_COMM_WORLD, retcode);
	MPI_Finalize();
	exit(retcode);		// In case all else failes
#else
	fflush(stderr);

	MPI_Finalize();

	// Non-GNU compilers, rely on a segfault to generate a stacktrace.
	int *ptr = 0;
	*ptr = 17;
#endif

}
