#include <stdarg.h>

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
