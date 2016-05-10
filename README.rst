Everytrace
===========

When a program crashes or otherwise terminates, the first thing one wishes to know is, where did it terminate?  Some systems (Java, Pytthon, etc.) almost always provide a useful and complete stacktrace.  Unfortunately, this is not the case when programming C/C++/Fortran.  Intel compilers provide good symbolic stacktraces, but GNU compilers generally do not.  Debuggers don't always work, especially with MPI; and they are slow bewides.

Everytrace is a simple solution that, when used by the developer and user of an application, provides simple, complete symbolic stacktraces.  Stacktraces are provided directly from STDERR, and do not require any special configuration, debuggers, etc.  Everytrace requires minimal changes to existing code to enable stacktraces.

Everytrace works best with GNU compilers and OpenMPI on Linux or Mac.

Installing Everytrace
=======================

Everytrace is built with CMake and has no dependencies.  Other than standard CMake arguments, the CMake build takes the following comamnd-line arguments::

      -DUSE_FORTRAN=[YES/NO]
      -DUSE_MPI=[YES/NO]

``USE_FORTRAN`` should be enabled if you plan on using Everytrace with Fortran libraries; ``USE_MPI`` should be enabled if you plan on using it with MPI code.  If they are turned on, you must have a Fortran compiler and an MPI library available to CMake.

Everytrace may also be installed via the Spack_ auto-installer::

    spack install everytrace+mpi+fortran

.. _Spack: http://github.com/llnl/spack

Building with Everytrace
==========================

The developer of a library needs to make the following modifications to enable Everytrace:

1. Initialize Everytrace upon program or library initialization::

    #include <everytrace.h>
    everytrace_init();
    
   or alternately in Fortran 90::
  
    use everytrace
    call everytrace_init
    
   Everytrace initialization must be run at least once; running it multiple times will have no further effect.  You can run it at program startup; or if you're making a library, at some convenient point during library initialization.  With GNU C, it is also possible to run it when your shared library is loaded.  See http://stackoverflow.com/questions/1681060/library-path-when-dynamically-loaded and http://stackoverflow.com/questions/2053029/how-exactly-does-attribute-constructor-work

2. If you use CMake, use the `FindEverytrace.cmake` file provided to find Everytrace in your CMake build.  Make sure to set up your build to use the same Fortran compiler, and link to the same MPI, that you used to build Everytrace.  This will happen automatically if you build with Spack.

3. Link your program or library with one of ``everytrace_c_refaddr.o``, ``everytrace_cf_refaddr.o``, ``everytrace_c_mpi_refaddr.o`` or ``everytrace_cf_mpi_refaddr.o``, provided in ``<EVERYTRACE_ROOT>/lib`` installation directory.  If your program or library has ANY Fortran code in it, you should use a ``_cf_`` variant; otherwise, the ``_c_`` variant.  Similarly, if your program or library usese MPI, you should use an ``_mpi`` variant.

   **NOTE**: It is important to add this `.o` file to *every* binary artifact you create (executable file or shared object).  Including it enables Everytrace to find symbols in that artifact.
  
4. Link your overall program or shared library with `libeverytrace.so`, as you would with any other shared library you depend upon.

Running with Everytrace
=========================

Once a program has been Everytrace-enabled, you can obtain stacktraces as follows:

1. Set the `EVERYTRACE` env var::
 
    export EVERYTRACE=

   This will cause Everytrace to write a few lines to STDERR in your program.

2. If your program uses MPI, use the `mpilabel` wrapper to run it.  That is... instead of running::

    mpirun -np 17 myprogram ... >log 2>&1 &
   
   you do:
   
    mpirun -np 17 mpilabel myprogram ... >log &

   This will send STDOUT and STDERR of all MPI processes to STDOUT, labeling each line according to the MPI rank from which it came.  Output from a single MPI rank can later be obtained via grep.

 3. When your program crashes, run `everytrace` on its STDOUT (presuming you've saved that to a log file)::
 
    everytrace log
    
That's it, now you have a stacktrace!

Exiting with Everytrace
=========================

The above procedure will give you a stacktrace whenever a signal occurs (segfault, etc).  However, it does not protect against programs that exit "gracefuly" in case of an error, or from C++ programs that terminate by throwing an Exception.  In such cases, it is necessary to modify the offending program/library to make it work with Everytrace.

Exit Calls
------------

Many libraries have an ``error()`` subroutine that is called when an error has been detected and the library is exiting.  Inside that routine is a calle to ``exit(int errno)``, which can be replaced with a call to ``everytrace_exit(int errno)``.  This introduces a library dependency on Everytrace; alternately, one can just throw a SEGFAULT, which Everytrace will catch.  For example::

    void my_exit()
    {
        fflush(stdout);
        fflush(stderr);
        int *p=0;
        *p=17;
    }

A cleaner approach is to provide a build flag to enable/disable Everytrace in your library, and use `#ifdef's or function pointers to control which exit function is called.

C++ Exceptions
----------------

Everytrace does not currently provide an easy way to get a stacktrace at the point a C++ exception is thrown.  This feature is coming soon...



Tools and code to get a stacktrace from your program on EVERY error.
