#ifndef EVERYTRACE_CONFIG_H
#define EVERYTRACE_CONFIG_H


// --------------------------------------------------------
// Define what is available, based on our compiler settings

#if defined(CMAKE_C_GNU)
#	define C_BACKTRACE_AVAILABLE
#endif

#if defined(CMAKE_FORTRAN_GNU)
#	define FORTRAN_BACKTRACE_AVAILABLE
#endif

// ----------------------------------------------------------
// Define what to actually use.

#if defined(FORTRAN_BACKTRACE_AVAILABLE)
#   pragma message("FORTRAN_BACKTRACE_AVAILABLE: define USE_FORTRAN_BACKTRACE")
#   define USE_FORTRAN_BACKTRACE
#else
#   pragma message("not FORTRAN_BACKTRACE_AVAILABLE")
#	if defined(CMAKE_FORTRAN_INTEL)
#      pragma message("    CMAKE_FORTRAN_INTEL: define USE_NO_BACKTRACE")
#		define USE_NO_BACKTRACE
#	elif defined(C_BACKTRACE_AVAILABLE)
#       pragma message("    C_BACKTRACE_AVAILABLE: define USE_C_BACKTRACE")
#		define USE_C_BACKTRACE
#	else
#       pragma message("    Unrecognized compiler: define USE_NO_BACKTRACE")
#		define USE_NO_BACKTRACE
#	endif
#endif

#ifndef USE_NO_BACKTRACE
#   pragma message("define USE_BACKTRACE")
#	define USE_BACKTRACE
#endif

#endif
