/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * pwd     - команда terminal, вывод имени текущей/рабочей директории в консоль
 * pwd_cmd - класс, реализующий функциональность команды pwd в terminal
 *
 * Пример использования pwd в terminal:
 * terminal@user:~ pwd
 */
#pragma once

#include "command.hpp"

namespace fs = std::experimental::filesystem;

class pwd_cmd : public command {
public:
    ~pwd_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // pwd_cmd

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



