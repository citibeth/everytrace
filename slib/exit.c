#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "everytrace.h"


void everytrace_exit(int retcode)
{
	fprintf(stderr, "Everytrace Dump, exit: %d\n", retcode);
	fflush(stdout);
	fflush(stderr);
#ifdef USE_BACKTRACE
	everytrace_dump();
	fflush(stderr);
	exit(retcode);
#else

	// Non-GNU compilers, rely on a segfault to generate a stacktrace.
	int *ptr = 0;
	*ptr = 17;
#endif

}
