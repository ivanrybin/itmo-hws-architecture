/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * echo     - команда terminal, вывод аргументов команды в консоль
 * echo_cmd - класс, реализующий функциональность команды echo в terminal
 *
 * Пример использования echo в terminal:
 * terminal@user:~ echo ABC
 */
#pragma once

#include "command.hpp"

/*
 * echo_cmd - реализация абстрактного класса command,
 *            обеспечивающая функциональность команды echo.
 */
class echo_cmd : public command {
public:
    ~echo_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // echo_cmd

