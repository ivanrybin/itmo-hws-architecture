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
