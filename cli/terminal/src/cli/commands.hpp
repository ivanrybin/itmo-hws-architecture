/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * cli - класс-агрегатор всех доступных в терминале команд, реализующих интерфейс класса command.
 *
 * Для добавления команды в terminal необходимо реализовать команду, подключить ее заголовочный файл к данному,
 * добавить в конструкторе cli() в storage пару: имя команды, через которое она будет вызывать в terminal,
 *                                                    умный указатель на объект класса команды.
 *
 * После этого команда становится доступной для использования в terminal.
 *
 */
#pragma once

#include <memory>
#include <utility>
#include <unordered_map>

#include "commands/echo_cmd.hpp"
#include "commands/cat_cmd.hpp"
#include "commands/pwd_cmd.hpp"
#include "commands/exit_cmd.hpp"
#include "commands/wc_cmd.hpp"
#include "commands/grep_cmd.hpp"

/*
 * commands - класс агрегатор команд, поддерживаемых CLI.
 */
class commands {
public:
    commands();
    std::unordered_map<std::string, std::unique_ptr<command*>> storage;
}; // cli
