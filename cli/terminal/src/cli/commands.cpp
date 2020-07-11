/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "commands.hpp"

/*
 *  Конструктор агрегаторного класса commands.
 *  Инициализирует классы-реализации команд.
 */
commands::commands() {
    storage.insert(std::make_pair("echo", std::make_unique<command*>(new echo_cmd)));
    storage.insert(std::make_pair("exit", std::make_unique<command*>(new exit_cmd)));
    storage.insert(std::make_pair("pwd",  std::make_unique<command*>(new pwd_cmd)));
    storage.insert(std::make_pair("cat",  std::make_unique<command*>(new cat_cmd)));
    storage.insert(std::make_pair("wc",   std::make_unique<command*>(new wc_cmd)));
    storage.insert(std::make_pair("grep", std::make_unique<command*>(new grep_cmd)));
}
