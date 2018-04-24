#ifndef EVERYTRACE_H
#define EVERYTRACE_H

// Default handler for reporting errors by Everytrace-enabled binaries.
// This extra bit of indirection allows us to change how ALL everytrace
// enabled libraries work.
// http://www.thecodingforums.com/threads/function-pointers-to-printf.317925/
typedef void (*everytrace_error_ptr) (int retcode, char const *str, ...);

// Back-end exit handler
typedef void (*everytrace_exit_ptr) (int retcode, char *buf);

#ifdef __cplusplus
extern "C" {
#endif

    // ---------- Functions called by user
    /** main() program calls this at startup. */
	void everytrace_init();

    /* User libraries typically have:
          everytrace_error_ptr mylib_error = everytrace_error_default;
       This is the standard top-level user-callable Everytrace function.
       It does printf() formatting, then passes the formatted message to
       the "back end" (below)
    */

    // ---------- Back End Components of an error handler

    /** The main back end handles the formatted user message appropriately.  Options:

    -) everytrace_exit_default():
         Calls dump(), handles the formatted user message (from above),
         cleans up MPI (if present), and exits.

    -) everytrace_exit_exception(): [everytrace_cxx.cpp]  (C++ only)
         Calls dump(), then throws an exception.  Useful when running
         inside Python extensions (as long as all Cython functions are
         declared 'except +').  This allows the Python interpreter to
         finish cleaning up and print a Python stacktrace as well.
         Python extensions should set in their init():
             everytrace_exit = &everytrace_exit_exception

    -) everytrace_exit_silent_exception:  (C++ only)
         Just throws an exception, prints nothing.  Useful for unit tests.
    */
    extern everytrace_exit_ptr everytrace_exit;

    /** Set to 1 when a signal is encountered; avoids recursive exits. */
    extern int everytrace_signal_encountered;

    /** Dumps stacktrace to stderr.  Differs depending on compiler,
        language options, etc. */
	void everytrace_dump();


    // Set mylib_error to point here
    void everytrace_error_default(int retcode, const char *format, ...);

    // --------- Supporting implementations
    /** Default pure-C exit handler.  Convenience function. */
    void everytrace_exit_default(int retcode, char *msg);


    /* Programmatically set this to false if you DON'T wnat to dump with
       Fortran, even if Fortran is enabled. */
    extern int everytrace_dump_with_fortran;

#ifdef __cplusplus
}
#endif



#endif
