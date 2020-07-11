/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "exit_cmd.hpp"

/*
 *  Метод exit_cmd::execute реализует абстрактный метод command::execute,
 *  реализуя функциональность команды bash - exit.
 */
int exit_cmd::execute(std::stringstream& out_buf,
                      std::ostream& out,
                      std::ostream& err,
                      const std::vector<std::string>& args,
                      size_t& pos,
                      bool is_pipe) {

    out_buf.str("");
    out_buf.clear();

    if ((pos + 1 < args.size() and !is_pipe) || pos + 1 >= args.size()) {
        return EXIT;
    }

    return OK;
}
