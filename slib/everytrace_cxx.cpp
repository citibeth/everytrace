#include <cstdio>

extern "C" everytrace_dump();

namespace everytrace {

class Exception
{
	Exception() {
		fprintf(stderr, "Everytrace Dump, exception:\n");
		everytrace_dump();
	}

};

}
