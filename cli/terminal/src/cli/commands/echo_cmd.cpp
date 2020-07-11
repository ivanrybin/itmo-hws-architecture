/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "echo_cmd.hpp"

/*
 *  Метод echo_cmd::execute реализует абстрактный метод command::execute,
 *  реализуя функциональность команды bash - echo.
 */
int echo_cmd::execute(std::stringstream& out_buf,
                      std::ostream& out,
                      std::ostream& err,
                      const std::vector<std::string>& args,
                      size_t& pos,
                      bool is_pipe) {

    out_buf.str("");
    out_buf.clear();

    bool first = true;

    for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
        if (!is_pipe) {
            out << ((first) ? "" : " ") << args[pos];
        }
        out_buf << ((first) ? "" : " ") << args[pos];
        first = false;
    }

    if (!is_pipe) {
        out << std::endl;
    }
    out_buf << std::endl;

    --pos;
    return OK;
}
