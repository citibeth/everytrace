void everytrace_exit(int retcode)
{
	fprintf(stderr, "Everytrace Dump, exit:\n");
	everytrace_dump();


	MPI_Abort(MPI_COMM_WORLD, retcode);
	MPI_Finalize();
	exit(retcode);		// In case all else failes
}
