/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * cat     - команда terminal, вывод файла в консоль
 * cat_cmd - класс, реализующий функциональность команды cat в terminal
 *
 * Пример использования cat в terminal:
 * terminal@user:~ cat [FILEPATH]
 */
#pragma once

#include "command.hpp"

namespace fs = std::experimental::filesystem;

class cat_cmd : public command {
public:
    ~cat_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // cat_cmd
