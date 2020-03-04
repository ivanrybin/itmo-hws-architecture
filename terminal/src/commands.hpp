/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * commands - класс-агрегатор всех доступных в терминале команд, реализующих интерфейс класса command.
 *
 * Для добавления команды в terminal необходимо реализовать команду, подключить ее заголовочный файл к данному,
 * добавить в конструкторе commands() в storage пару: имя команды, через которое она будет вызывать в terminal,
 *                                                    умный указатель на объект класса команды.
 *
 * После этого команда становится доступной для использования в terminal.
 *
 */
#pragma once

#include <memory>
#include <utility>

#include "commands/echo_cmd.hpp"
#include "commands/cat_cmd.hpp"
#include "commands/pwd_cmd.hpp"
#include "commands/exit_cmd.hpp"
#include "commands/wc_cmd.hpp"

class commands {
public:
    commands();
    std::unordered_map<std::string, std::unique_ptr<command*>> storage;
}; // commands

commands::commands() {
    storage.insert(std::make_pair("echo", std::make_unique<command*>(new echo_cmd)));
    storage.insert(std::make_pair("exit", std::make_unique<command*>(new exit_cmd)));
    storage.insert(std::make_pair("pwd",  std::make_unique<command*>(new pwd_cmd)));
    storage.insert(std::make_pair("cat",  std::make_unique<command*>(new cat_cmd)));
    storage.insert(std::make_pair("wc",   std::make_unique<command*>(new wc_cmd )));
}