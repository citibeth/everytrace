// http://stackoverflow.com/questions/1681060/library-path-when-dynamically-loaded
// http://stackoverflow.com/questions/2053029/how-exactly-does-attribute-constructor-work

#ifdef __GNUC__
// Right now, only tested for GNU C

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

extern int _everytrace_use_fortran;
extern int _everytrace_use_mpi;


// At library load time:
// Determine the path of the library we were loaded from.  Print it,
// along with a reference address, on STDERR.  This allows later
// translation of relative library load addresses.
__attribute__((constructor))
static void _everytrace_refaddr(void) {
    Dl_info dl_info;
    char *everytrace;

    EVERYTRACE_SET_FLAGS;

    // Only do something if the user has defined the EVERYTRACE
    // variable.  That way, this can be included in libraries without
    // affecting STDOUT for people who don't want to use Everytrace.
    everytrace = getenv("EVERYTRACE");    // Use getenv() for non-GNU compiler
    if (!everytrace) return;

    dladdr((void *)_everytrace_refaddr, &dl_info);
    fprintf(stderr, "_EVERYTRACE_ REFERENCE \"%s\" %p\n", dl_info.dli_fname, &_everytrace_refaddr);
    fflush(stderr);
}

#endif
