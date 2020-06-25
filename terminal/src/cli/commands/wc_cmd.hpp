/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * wc     - команда terminal, вывод числа строк, слов, байт в файле/строке
 * wc_cmd - класс, реализующий функциональность команды wc в terminal
 *
 * Пример использования wc в terminal:
 * terminal@user:~ wc [FILEPATH]
 */
#pragma once

#include "command.hpp"

namespace fs = std::experimental::filesystem;


/*
 * wc_cmd - реализация абстрактного класса command,
 *          обеспечивающая функциональность команды wc.
 */
class wc_cmd : public command {
public:
    ~wc_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
private:
    static void words_lines_counter(std::istream& stream, size_t& f_size,  size_t& l_cnt,   size_t& w_cnt,
                                                   size_t& f_total, size_t& l_total, size_t& w_total);
}; // wc_cmd
