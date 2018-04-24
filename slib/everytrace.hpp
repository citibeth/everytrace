#ifndef EVERYTRACE_HPP
#define EVERYTRACE_HPP

#include <everytrace.h>
#include <exception>
#include <string>

namespace everytrace {

    /** @brief Excpetion thrown by the default IBMisc error handler. */
    class Exception : public std::exception
    {
        std::string msg;
    public:
        Exception(std::string const &&_msg) : msg(std::move(_msg)) {}
            
        virtual ~Exception()
            {}

        virtual const char* what() const noexcept
            { return msg.c_str(); }
    };

}    // namespace everytrace

extern "C"
void everytrace_exit_exception(int retcode, char *msg);

/** Handler used for unit tests. */
extern "C"
void everytrace_exit_silent_exception(int retcode, char *msg);

#endif
