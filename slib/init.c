#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include "everytrace.h"
#include "config.h"

#ifdef USE_BACKTRACE
static initialized = 0;

static char *sig_names[] = {
	"", "SIGHUP", "SIGINT", "SIGQUIT", "SIGILL", "SIGTRAP", "SIGABRT", "SIGEMT",
	"SIGFPE", "SIGKILL", "SIGBUS", "SIGSEGV", "SIGSYS", "SIGPIPE", "SIGALRM", "SIGTERM",
	"SIGURG", "SIGSTOP", "SIGTSTP", "SIGCONT", "SIGCHLD", "SIGTTIN", "SIGTTOU", "SIGIO",
	"SIGXCPU", "SIGXFSZ", "SIGVTALRM", "SIGPROF", "SIGWINCH", "SIGINFO", "SIGUSR1", "SIGUSR2"};

static void sig_handler(int sig)
{
	char *name;
	if (sig >= 31) name = "<UNKNOWN>";
	else name = sig_names[sig];

	fprintf(stderr, "Caught signal %d (%s)\n", sig, name);
	everytrace_exit(sig);
}
#endif

// To be called by a main program upon startup
void everytrace_init()
{
#ifdef USE_BACKTRACE
#if 0
// These are Macintosh-only.  Use correct conditional compilation
// for Linux signals

	char *everytrace;

	everytrace = getenv("EVERYTRACE");	// Use getenv() for non-GNU compiler
	if (!everytrace) return;

	if (initialized) return;

	fprintf(stderr, "Everytrace installing signal handlers xxx.\n");

	// Install signal handlers, for stacktraces on segfaults and similar.
	signal(SIGKILL, &sig_handler);
	signal(SIGHUP, &sig_handler);
	signal(SIGINT, &sig_handler);
	signal(SIGQUIT, &sig_handler);
	signal(SIGILL, &sig_handler);
	signal(SIGTRAP, &sig_handler);
	signal(SIGABRT, &sig_handler);
	signal(SIGEMT, &sig_handler);
	signal(SIGFPE, &sig_handler);	// Fortran floating point "traps"
	signal(SIGKILL, &sig_handler);
	signal(SIGBUS, &sig_handler);
	signal(SIGSEGV, &sig_handler);
	signal(SIGSYS, &sig_handler);
	signal(SIGTERM, &sig_handler);

	initialized = 1;
#endif
#endif
}




