/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * terminal - эмуляция shell-подобного терминала
 * terminal - класс, реализующий функциональность terminal
 *
 * Вход: строка ->
 *       разбор строки на слова ->
 *       присваивание переменных, если они есть ->
 *       подстановка переменных, если они обнаружены в строке ->
 *       поиск команды в словах ->
 *       исполнение команды, если она существует ->
 *       если команда не существует, то передача аргументов в реальный терминал ->
 *       вывод результата или ошибки -> Вход: строка
 */
#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <experimental/filesystem>
#include <utility>
#include <fstream>
#include <algorithm>

#include "cli/commands.hpp"

class terminal {
public:
    explicit terminal   (std::istream& in = std::cin, std::ostream& out = std::cout,
                                                      std::ostream& err = std::cerr, bool test_mode = false);

    int run             (bool quiet = false, bool once = false);

    void merge_env      (const std::unordered_map<std::string, std::string>& other_env);

private:
    int execute_commands();

    bool get_input_from_terminal();

    bool parse          (const std::string& input_str);
    bool parse_vars     (const std::string& input_str, size_t s_begin);
    void parse_words    (const std::string& input_str, size_t s_begin, size_t w_begin);
    void parse_dollars  (std::string& word);

    void go_spaces      (const std::string& input_str, size_t& begin, size_t& i);
    bool quote_handler  (std::string& input_str, size_t pos, char& quote_type);

    void command_not_found_exc (const std::string& command);

    std::istream& in;
    std::ostream& out;
    std::ostream& err;

    std::stringstream in_buf;
    std::stringstream out_buf;

    commands available_commands;

    std::vector<std::string> words;
    std::unordered_map<std::string, std::string> env;

    std::unordered_map<char, bool> alphabet;
    bool test_mode;

};
