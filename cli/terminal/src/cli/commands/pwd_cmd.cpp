/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "pwd_cmd.hpp"

/*
 *  Метод pwd_cmd::execute реализует абстрактный метод command::execute,
 *  реализуя функциональность команды bash - pwd.
 */
int pwd_cmd::execute(std::stringstream& out_buf,
                     std::ostream& out,
                     std::ostream& err,
                     const std::vector<std::string>& args,
                     size_t& pos,
                     bool is_pipe) {

    out_buf.str("");
    out_buf.clear();

    if (!is_pipe) {
        out << std::string(fs::current_path()) << std::endl;
    }
    out_buf << std::string(fs::current_path()) << std::endl;

    for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {}

    if (pos < args.size() and args[pos] == "|") {
        --pos;
    }

    return OK;
}
