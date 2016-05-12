#ifdef USE_MPI
#   include <mpi.h>
#endif


#include <execinfo.h>
#include <unistd.h>


#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "everytrace.h"
#include <stdarg.h>
#include <signal.h>


/* Tells us whether the currently loaded instance of Everytrace uses
Fortran and MPI.  Each flag will be set if ANY ONE of the
Everytrace-enabled libraries uses the feature. */
int _everytrace_use_fortran = 0;
int _everytrace_use_mpi = 0;

extern everytrace_dump_f();

// -------------------------------------------------------------
#ifdef USE_BACKTRACE
#define MAX_SIGNAL 32
static initialized = 0;

static char *signal_names[MAX_SIGNAL];

/** Initialize association between symbols and strings (user convenience) */
static void set_signal_name(int sig, char *name)
{
    if (sig >= MAX_SIGNAL) {
        fprintf(stderr, "Signal ID too large: %d %s\n", sig, name);
        exit(0);
    }
    signal_names[sig] = name;
}

static void sig_handler(int sig)
{
    char *name;
    if (sig < MAX_SIGNAL) name = signal_names[sig];
    if (name == NULL) name = "<UNKNOWN>";

    fprintf(stderr, "_EVERYTRACE_: Caught signal %d (%s)\n", sig, name);
    everytrace_exit(sig);
}
#endif

// To be called by a main program upon startup
void everytrace_init()
{
#ifdef USE_BACKTRACE

    set_signal_name(SIGKILL, "SIGKILL");
    set_signal_name(SIGHUP, "SIGHUP");
    set_signal_name(SIGINT, "SIGINT");
    set_signal_name(SIGQUIT, "SIGQUIT");
    set_signal_name(SIGILL, "SIGILL");
    set_signal_name(SIGTRAP, "SIGTRAP");
    set_signal_name(SIGABRT, "SIGABRT");
    set_signal_name(SIGFPE, "SIGFPE");
    set_signal_name(SIGKILL, "SIGKILL");
    set_signal_name(SIGBUS, "SIGBUS");
    set_signal_name(SIGSEGV, "SIGSEGV");
    set_signal_name(SIGSYS, "SIGSYS");
    set_signal_name(SIGTERM, "SIGTERM");
#ifdef __APPLE__
    set_signal_name(SIGEMT, "SIGEMT");
#endif

    char *everytrace;

    everytrace = getenv("EVERYTRACE");  // Use getenv() for non-GNU compiler
    if (!everytrace) return;
    if (initialized) return;

    // Install signal handlers, for stacktraces on segfaults and similar.
    signal(SIGKILL, &sig_handler);
    signal(SIGHUP, &sig_handler);
    signal(SIGINT, &sig_handler);
    signal(SIGQUIT, &sig_handler);
    signal(SIGILL, &sig_handler);
    signal(SIGTRAP, &sig_handler);
    signal(SIGABRT, &sig_handler);
    signal(SIGFPE, &sig_handler);   // Fortran floating point "traps"
    signal(SIGKILL, &sig_handler);
    signal(SIGBUS, &sig_handler);
    signal(SIGSEGV, &sig_handler);
    signal(SIGSYS, &sig_handler);
    signal(SIGTERM, &sig_handler);
#ifdef __APPLE__
    signal(SIGEMT, &sig_handler);
#endif

    initialized = 1;
#endif
}
// -------------------------------------------------------------
#ifdef USE_BACKTRACE
#   ifdef __GNUC__

#   include <inttypes.h>        // C-99
    void everytrace_dump(void)
    {
        // Defer to the Fortran backtrace if we're using Fortran
#       ifdef FORTRAN_BACKTRACE_AVAILABLE
        if (_everytrace_use_fortran) {
            everytrace_dump_f();
            return;
        }
#       endif
        const int MAX_TRACE = 200;
        void *trace[MAX_TRACE];
        size_t i;
        size_t ntrace = backtrace(trace, MAX_TRACE);

        for (i=0; i<ntrace; ++i) {
            fprintf(stderr, "#%d 0x%lx ", i, (uintptr_t)(trace[i]));
            // http://stackoverflow.com/questions/77005/how-to-generate-a-stacktrace-when-my-gcc-c-app-crashes
            backtrace_symbols_fd(&trace[i], 1, STDERR_FILENO);
        }
        fflush(stderr);
    }


#   else


    // This shouldn't happen, but just in case...
    void everytrace_dump(void)
    {
        fprintf(stderr, "_EVERYTRACE_: [No C backtrace available...]\n");
        fflush(stderr);
    }

#   endif
#endif
// -------------------------------------------------------------
void everytrace_exit(int retcode)
{
    fprintf(stderr, "_EVERYTRACE_ DUMP: Exiting with return code: %d\n", retcode);
    fflush(stdout);
    fflush(stderr);
#   ifdef USE_BACKTRACE
        everytrace_dump();
        fflush(stderr);

#       ifdef USE_MPI
        if (_everytrace_use_mpi)
            MPI_Abort(MPI_COMM_WORLD, retcode);
            MPI_Finalize();
#       endif

        exit(retcode);
#   else
        // No backtrace capability (non-GNU compiler), rely on a segfault to generate a stacktrace.
#       ifdef USE_MPI
            MPI_Finalize();
#       endif

        int *ptr = 0;
        *ptr = 17;
#   endif

}


// int vsnprintf (char * s, size_t n, const char * format, va_list arg );


// http://stackoverflow.com/questions/4785381/replacement-for-ms-vscprintf-on-macos-linux
// This was originally a Microsoft extension.  Here's how to do it in standard C.
// vscprintf() returns the length of the resulting string.

 
void exit_printf(int retcode, const char *format, ...)
{
    va_list arglist;

#if 0
    // How to create a string for inclusion in an exeption...
    va_start(arglist, format)
    size_t size = vsnprintf(NULL, 0, format, arglist);
    va_end(arglist);

    va_start(arglist, format)
    char buf[size+1];
    vsnprintf(buf, size+1, format, arglist);
    va_end(arglist);
#endif

    va_start(arglist, format);
    fprintf(stderr, format, arglist);
    va_end(arglist);

    everytrace_exit(retcode);
}
