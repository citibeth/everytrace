module everytrace
	use iso_c_binding
	USE ISO_FORTRAN_ENV, ONLY : ERROR_UNIT ! access computing environment

INTERFACE
	subroutine everytrace_exit(retcode) bind(c)
		use iso_c_binding
		integer(c_int), value :: retcode
	end subroutine everytrace_exit

	subroutine everytrace_init() bind(c)
	end subroutine everytrace_init

END INTERFACE


CONTAINS

#ifdef __GNUC__
subroutine everytrace_dump_f() bind(c)
	! Unlike the GNU C backtrace(), this one will
	! trace past C/Fortran call interfaces.
	call backtrace
end subroutine everytrace_dump_f
#endif

end module everytrace
