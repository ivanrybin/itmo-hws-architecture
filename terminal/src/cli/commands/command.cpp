/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "command.hpp"

/*
 *  Метод command::error_message отвечает за вывод ошибок в консоль
 *  при исполнении команд, входящих в CLI.
 */
void command::error_message(std::ostream& err, const std::string& cmd_name,
                            const std::string& arg, const std::string& message) {

    err << cmd_name + ": " << arg << ": " + message << std::endl;
}

/*
 *  Шаблоны ошибок.
 */
const std::string command::catalog_err = "Это каталог";
const std::string command::file_catalog_not_exist = "Нет такого файла или каталога";
