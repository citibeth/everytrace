module everytrace
	use iso_c_binding
	USE ISO_FORTRAN_ENV, ONLY : ERROR_UNIT ! access computing environment
CONTAINS

subroutine everytrace_dump bind(c)
	! Unlike the GNU C backtrace(), this one will
	! trace past C/Fortran call interfaces.
	call backtrace
end subroutine everytrace_dump

subroutine everytrace_exit(retcode) bind(c)
	integer(c_int), value :: retcode

	write (ERROR_UNIT,*) 'Everytrace Dump, exit:'
	call everytrace_dump

	! GNU extension: https://gcc.gnu.org/onlinedocs/gcc-4.4.4/gfortran/EXIT.html
	! Without GNU extension, we could write this in C and call our C function.
	call exit(retcode)
end subroutine everytrace_exit(retcode)

end module everytrace
