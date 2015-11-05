# ------------ Header Files

install (FILES
	${CMAKE_CURRENT_SOURCE_DIR}/everytrace.h
	${CMAKE_CURRENT_BINARY_DIR}/everytrace.mod
         DESTINATION include)


# ----------- The file everytrace_refaddr.o to include in YOUR libraries
add_library(everytrace_refaddr STATIC everytrace_refaddr.c)
set_target_properties(everytrace_refaddr PROPERTIES RULE_LAUNCH_LINK
	"sh ${CMAKE_SOURCE_DIR}/cmake/scripts/cpo ${CMAKE_BINARY_DIR}/slib <OBJECTS> --")

install (FILES
	${CMAKE_CURRENT_BINARY_DIR}/everytrace_refaddr.c.o
		RENAME everytrace_refaddr.o
		DESTINATION lib)


# ----------- The main everytrace libraries

# ----------- everytrace_c
add_library(everytrace_c SHARED
	init.c dump.c exit.c)
install(TARGETS everytrace_c DESTINATION lib)


# ----------- everytrace_cf
if(${USE_FORTRAN})
	add_library(everytrace_cf SHARED
		init.c dump.c exit.c
		everytrace_cf_mod.f90)
	set_property(TARGET everytrace_cf APPEND PROPERTY COMPILE_FLAGS "-DFORTRAN_VERSION")
	install(TARGETS everytrace_cf DESTINATION lib)
endif()

if(${USE_MPI})
# ----------- everytrace_c_mpi
	add_library(everytrace_c_mpi SHARED
		init.c dump.c exit_mpi.c)
	target_link_libraries(everytrace_c_mpi ${MPI_C_LIBRARIES})
	install(TARGETS everytrace_c_mpi DESTINATION lib)

# ----------- everytrace_cf_mpi
	if (${USE_FORTRAN})
		add_library(everytrace_cf_mpi SHARED
			init.c dump.c exit_mpi.c
			everytrace_cf_mod.f90)
		set_property(TARGET everytrace_cf_mpi APPEND PROPERTY COMPILE_FLAGS "-DFORTRAN_VERSION")
		target_link_libraries(everytrace_cf_mpi ${MPI_C_LIBRARIES})
		install(TARGETS everytrace_cf_mpi DESTINATION lib)
	endif()
endif()


