
add_library(everytrace_refaddr_gcc STATIC everytrace_refaddr_gcc.c)
set_target_properties(everytrace_refaddr_gcc PROPERTIES RULE_LAUNCH_LINK
	"sh ${CMAKE_SOURCE_DIR}/cmake/scripts/cpo ${CMAKE_BINARY_DIR}/gcc <OBJECTS> --")

add_library(everytrace_c SHARED
	init.c
	everytrace_c.c)

add_library(everytrace_cf SHARED
	init.c
	everytrace_cf.c
	everytrace_cf_mod.f90)

install(TARGETS
	everytrace_c
	everytrace_cf
DESTINATION lib)

if(${USE_MPI})
	add_library(everytrace_c_mpi SHARED
		init.c
		everytrace_c_mpi.c)
	target_link_libraries(everytrace_c_mpi ${MPI_C_LIBRARIES})

	add_library(everytrace_cf_mpi SHARED
		init.c
		everytrace_cf_mpi.c
		everytrace_cf_mod.f90 ${MPI_C_LIBRARIES})
	target_link_libraries(everytrace_cf_mpi ${MPI_C_LIBRARIES})

	install(TARGETS
		everytrace_c_mpi
		everytrace_cf_mpi
	DESTINATION lib)
endif()


install (FILES
	${CMAKE_CURRENT_SOURCE_DIR}/everytrace.h
	${CMAKE_CURRENT_BINARY_DIR}/everytrace.mod
         DESTINATION include)

install (FILES
	${CMAKE_CURRENT_BINARY_DIR}/everytrace_refaddr_gcc.c.o
		RENAME everytrace_refaddr_gcc.o
		DESTINATION lib)
