#include <stdio.h>
#include <stdlib.h>
#include "config.h"

#ifdef USE_C_BACKTRACE
#	ifdef __GNUC__

#	include <inttypes.h>		// C-99
	void everytrace_dump(void)
	{
		const int MAX_TRACE = 200;
		void *trace[MAX_TRACE];
		size_t i;
		size_t ntrace = backtrace(trace, MAX_TRACE);

		for (i=1; i<ntrace; ++i) {	// Start at 1, don't print ourselves
			fprintf(stderr, "#%d 0x%lx\n", i-1, (uintptr_t)(trace[i]));
		}
		fflush(stderr);
	}


#	else


	// This shouldn't happen, but just in case...
	void everytrace_dump(void)
	{
		fprintf(stderr, "[No C backtrace available...]\n");
		fflush(stderr);
	}

#	endif
#endif
