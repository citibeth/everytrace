
void everytrace_exit(int err)
{
	fprintf(stderr, "Everytrace Dump, exit:\n");
	everytrace_dump();
	exit(err);
}
