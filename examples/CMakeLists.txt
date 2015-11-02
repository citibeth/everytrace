cmake_minimum_required(VERSION 3.1)
project (GLINT2)
enable_language(Fortran)
set(CMAKE_CXX_STANDARD 11)

list (APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include (setup_rpath)

find_package(Everytrace)

# --------------------------------------
