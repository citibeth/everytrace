cmake_minimum_required(VERSION 3.1)
enable_language(Fortran)
set(CMAKE_CXX_STANDARD 11)

# Needed to get just a single .o file for everytrace_refaddr_gcc
# http://stackoverflow.com/questions/4765222/how-do-i-produce-only-an-object-file-o-from-a-cmake-build-target
PROJECT(CPO C)

list (APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include (setup_rpath)

# ------- Process Configure Options
if (NOT DEFINED USE_FORTRAN)
	set(USE_FORTRAN NO)
endif()

if (NOT DEFINED USE_MPI)
	set(USE_MPI NO)
endif()

if(${USE_MPI})
	find_package(MPI REQUIRED)
    include_directories(${MPI_C_INCLUDE_PATH})
endif()


## -------- Locate External Libraries
#find_package(Python REQUIRED)
#if(${THREAD_SAFE})
#	find_package(Boost COMPONENTS thread)
#endif()


# -------- Process subdirectories of the build
add_subdirectory(gcc)
add_subdirectory(bin)
