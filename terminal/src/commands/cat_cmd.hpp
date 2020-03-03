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

int cat_cmd::execute(std::stringstream& out_buf,
            std::ostream& out,
            std::ostream& err,
            const std::vector<std::string>& args,
            size_t& pos,
            bool is_pipe) {

    out_buf.str("");
    out_buf.clear();

    if (pos + 1 == args.size()) {
        std::string input_str{};

        while(!getline(std::cin ,input_str).eof()) {
            if (input_str == "^C") {
                break;
            }

            if (!is_pipe) {
                out << input_str << std::endl;
            }
            out_buf << input_str << std::endl;
        }

    } else {
        for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
            fs::path p(args[pos]);

            if (fs::exists(p)) {

                if (fs::is_directory(p)) {

                    if (!is_pipe) {
                        error_message(err, "cat", args[pos], catalog_err);
                    }

                } else {
                    std::ifstream file(p, std::ios::out | std::ios::binary);

                    if (file.is_open()) {
                        if (!is_pipe) {
                            out << file.rdbuf() << std::endl;
                            file.seekg(0, std::istream::beg);
                        }
                        out_buf  << file.rdbuf();
                        file.close();
                    }
                }
            } else {
                if (!is_pipe) {
                    error_message(err, "cat", args[pos], file_catalog_not_exist);
                }
            }
        }
        --pos;
    }
    return OK;
}



