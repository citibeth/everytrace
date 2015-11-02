#include <inttypes.h>		// C-99

void everytrace_dump(void)
{
	const int MAX_TRACE = 200;
	void *trace[MAX_TRACE];
	size_t i;
	size_t ntrace = backtrace(trace, MAX_TRACE);

	for (i=1; i<ntrace; ++i) {	// Start at 1, don't print ourselves
		fprintf(stderr, "#%d 0x%lx\n", i-1, (uintptr_t)(trace[i]));
	}
}
