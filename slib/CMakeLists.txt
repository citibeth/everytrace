# ------------ Header Files

install (FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/everytrace.h
        DESTINATION include)

if(${USE_FORTRAN})
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/everytrace.mod
        DESTINATION include)
endif()


# ----------- The file everytrace_refaddr.o to include in YOUR libraries
list(APPEND VARIANTS c)
if (${USE_FORTRAN})
    if (${USE_MPI})
        list(APPEND VARIANTS cf cf_mpi c_mpi)
    else()
        list(APPEND VARIANTS cf)
    endif()
else()
    if (${USE_MPI})
        list(APPEND VARIANTS c_mpi)
    endif()
endif()

foreach (VARIANT ${VARIANTS})
    message("Adding variant everytrace_" ${VARIANT} "_refaddr.o")
    add_library(everytrace_${VARIANT}_refaddr SHARED everytrace_${VARIANT}_refaddr.c)
    set_target_properties(everytrace_${VARIANT}_refaddr PROPERTIES RULE_LAUNCH_LINK
        "sh ${CMAKE_SOURCE_DIR}/cmake/scripts/cpo ${CMAKE_BINARY_DIR}/slib <OBJECTS> --")

    install (FILES
        ${CMAKE_CURRENT_BINARY_DIR}/everytrace_${VARIANT}_refaddr.c.o
            RENAME everytrace_${VARIANT}_refaddr.o
            DESTINATION lib)

endforeach()

# ----------- The main everytrace library

# ----------- everytrace_c
list(APPEND SOURCES everytrace.c)
if (${USE_FORTRAN})
    list(APPEND SOURCES everytrace_mod.F90)
endif()

add_library(everytrace SHARED ${SOURCES})
target_link_libraries(everytrace ${MPI_C_LIBRARIES})
install(TARGETS everytrace DESTINATION lib)
