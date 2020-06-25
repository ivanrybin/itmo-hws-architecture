/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * exit     - команда terminal, выход из терминала или sub-terminal
 * exit_cmd - класс, реализующий функциональность команды exit в terminal
 *
 * Пример использования exit в terminal:
 * terminal@user:~ exit
 */
#pragma once

#include "command.hpp"

class exit_cmd : public command {
public:
    ~exit_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // exit_cmd
