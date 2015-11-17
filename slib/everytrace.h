#ifndef EVERYTRACE_H
#define EVERYTRACE_H

#ifdef __cplusplus
extern "C" {
#endif

	void everytrace_exit(int retcode);
	void everytrace_init();
	void everytrace_dump();

#ifdef __cplusplus
}
#endif

#endif
