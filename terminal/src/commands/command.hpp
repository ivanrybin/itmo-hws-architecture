/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * command - класс, реализующий интерфейс для всех команд, поддерживаемых terminal.
 * Интерфейс состоит из виртуального конструктора и единственной функции execute().
 *
 */
#pragma once

#include <iostream>
#include <string>
#include <fstream>

enum EXIT_STATUS {
    EXIT,
    OK
}; // EXIT_STATUS

class command {
public:
    virtual     ~command() = default;
    virtual int execute(std::stringstream& out_buf,
                             std::ostream& out,
                             std::ostream& err,
                             const std::vector<std::string>& args,
                             size_t& pos,
                             bool is_pipe) = 0;

protected:
    static void error_message(std::ostream& err, const std::string& cmd_name,
                                                 const std::string& arg, const std::string& message);

    static const std::string catalog_err;
    static const std::string file_catalog_not_exist;
}; // command

void command::error_message(std::ostream& err, const std::string& cmd_name,
                                               const std::string& arg, const std::string& message) {
    err << cmd_name + ": " << arg << ": " + message << std::endl;
}

const std::string command::catalog_err = "Это каталог";
const std::string command::file_catalog_not_exist = "Нет такого файла или каталога";

