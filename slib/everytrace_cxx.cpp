#include "config.h"
#include <cstdio>
#include <cstdarg>
#include <everytrace.hpp>
#include <string>

everytrace_exit_ptr everytrace_exit = &everytrace_exit_default;

/** printf to a std::string */
static std::string vsprintf(const char* format, std::va_list args)
{
    va_list tmp_args; //unfortunately you cannot consume a va_list twice
    va_copy(tmp_args, args); //so we have to copy it
    const int required_len = vsnprintf(nullptr, 0, format, tmp_args) + 1;
    va_end(tmp_args);

    std::string buf(required_len, '\0');
    if (std::vsnprintf(&buf[0], buf.size(), format, args) < 0) {
        return "<vsprintf encoding error>";
    }
    return buf;
}


/** Exit handler that throws an exception.  Useful in Python extensions.
msg must be null-terminated*/
extern "C"
void everytrace_exit_exception(int retcode, char *msg)
{
    fprintf(stderr, "_EVERYTRACE_ DUMP: %s\n", msg);
    fflush(stdout);
    fflush(stderr);

#   ifdef USE_BACKTRACE
#pragma message("X1 USE_BACKTRACE")
        everytrace_dump();
        fflush(stderr);

#       ifdef USE_MPI
        if (_everytrace_use_mpi)
            MPI_Abort(MPI_COMM_WORLD, retcode);
            MPI_Finalize();
#       endif

        throw everytrace::Exception(std::string(msg));
#   else
#pragma message("X2 NO USE_BACKTRACE")
        fprintf(stderr, "%s\n", msg);
        fflush(stderr);

        // No backtrace capability (non-GNU compiler), rely on a segfault to generate a stacktrace.
#       ifdef USE_MPI
            MPI_Finalize();
#       endif

        int *ptr = 0;
        *ptr = 17;
#   endif

}

/** Handler used for unit tests. */
extern "C"
void everytrace_exit_silent_exception(int retcode, char *msg)
{
    throw everytrace::Exception(std::string(msg));
}
