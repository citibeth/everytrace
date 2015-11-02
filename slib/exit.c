#include <stdio.h>
#include <stdlib.h>

#include "dump.h"


void everytrace_exit(int retcode)
{
  fprintf(stderr, "Everytrace Dump, exit: %d\n", retcode);
#ifdef USE_BACKTRACE
	everytrace_dump();
	exit(retcode);
#else
	fflush(stderr);

	// Non-GNU compilers, rely on a segfault to generate a stacktrace.
	int *ptr = 0;
	*ptr = 17;
#endif

}
