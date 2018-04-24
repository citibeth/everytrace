cmake_minimum_required(VERSION 3.1)
enable_language(Fortran)
enable_language(CXX)
set(CMAKE_CXX_STANDARD 11)

# Needed to get just a single .o file for everytrace_refaddr_gcc
# http://stackoverflow.com/questions/4765222/how-do-i-produce-only-an-object-file-o-from-a-cmake-build-target
PROJECT(CPO C)

list (APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include (setup_rpath)



# --------------------- Define our toolchain
if (NOT DEFINED USE_FORTRAN)
	set(USE_FORTRAN NO)
endif()

if (${USE_FORTRAN})
	if ("${CMAKE_Fortran_COMPILER_ID}" STREQUAL "GNU")
		add_definitions(-DCMAKE_FORTRAN_GNU)
	elseif("${CMAKE_Fortran_COMPILER_ID}" STREQUAL "Clang")
		add_definitions(-DCMAKE_FORTRAN_CLANG)
	elseif("${CMAKE_Fortran_COMPILER_ID}" STREQUAL "Intel")
		add_definitions(-DCMAKE_FORTRAN_INTEL)
	elseif("${CMAKE_Fortran_COMPILER_ID}" STREQUAL "MSVC")
		add_definitions(-DCMAKE_FORTRAN_MSVC)
	endif()
endif()

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
	add_definitions(-DCMAKE_CXX_GNU)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
	add_definitions(-DCMAKE_CXX_CLANG)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
	add_definitions(-DCMAKE_CXX_INTEL)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
	add_definitions(-DCMAKE_CXX_MSVC)
endif()

if ("${CMAKE_C_COMPILER_ID}" STREQUAL "GNU")
	add_definitions(-DCMAKE_C_GNU)
elseif("${CMAKE_C_COMPILER_ID}" STREQUAL "Clang")
	add_definitions(-DCMAKE_C_CLANG)
elseif("${CMAKE_C_COMPILER_ID}" STREQUAL "Intel")
	add_definitions(-DCMAKE_C_INTEL)
elseif("${CMAKE_C_COMPILER_ID}" STREQUAL "MSVC")
	add_definitions(-DCMAKE_C_MSVC)
endif()

include_directories(${PROJECT_SOURCE_DIR}/slib)

# ------- Process Configure Options

if (NOT DEFINED USE_MPI)
	set(USE_MPI NO)
endif()

if(${USE_MPI})
	find_package(MPI REQUIRED)
    include_directories(${MPI_C_INCLUDE_PATH})
endif()


if (NOT DEFINED USE_CXX)
    set(USE_CXX YES)
endif()
if (${USE_CXX})
    add_definitions(-DUSE_CXX)
endif()

## -------- Locate External Libraries
#find_package(Python REQUIRED)
#if(${THREAD_SAFE})
#	find_package(Boost COMPONENTS thread)
#endif()


# -------- Process subdirectories of the build
add_subdirectory(slib)
add_subdirectory(bin)
