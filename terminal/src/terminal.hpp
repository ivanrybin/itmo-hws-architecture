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

#include "commands.hpp"

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

}; // terminal

terminal::terminal(std::istream& in, std::ostream& out, std::ostream& err, bool test_mode)
                                                  : in(in), out(out), err(err), in_buf(), out_buf(),
                                                    available_commands(), words(), env(), test_mode(test_mode) {
    for (const char& c : "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") {
        alphabet[c] = true;
    }
}

int terminal::run(bool quiet, bool once) {
    int return_val  = OK;
    bool is_var     = false;
    bool is_input   = true;
    std::string exception{};

    while (is_input) {
        words = {};
        in_buf.str("");  in_buf.clear();
        out_buf.str(""); out_buf.clear();

        if (!quiet and not test_mode) {
            out << "terminal@user:~$ ";
        }

        is_input = get_input_from_terminal();

        try {
            is_var = parse(in_buf.str() + " ");

            if (!is_var) {
                return_val = execute_commands();
                if (return_val == EXIT) {
                    return EXIT;
                }
            }
        } catch (std::invalid_argument& e) {
            err << e.what() << std::endl;
            continue;
        }

        if (once) {
            break;
        }
    }
    return EXIT;
}

void terminal::merge_env(const std::unordered_map<std::string, std::string>& other_env) {
    for (const auto& item : other_env) {
        env[item.first] = item.second;
    }
}

int terminal::execute_commands() {
    size_t pipes_cnt = 0;
    bool is_pipe = false;

    for (const auto& word : words) {
        if (word == "|") ++pipes_cnt;
    }

    int return_value = OK;
    for (size_t i = 0; i < words.size(); ++i) {
        if (available_commands.storage.find(words[i]) != available_commands.storage.end()) {
            is_pipe = pipes_cnt > 0;
            return_value = (*available_commands.storage[words[i]])->execute(out_buf, out, err, words, i, is_pipe);

            if (return_value == EXIT) {
                return EXIT;
            }

        } else if (words[i] == "|") {
            --pipes_cnt;

            if (i + 1 == words.size()) {
                out_buf.str("");
                out_buf.clear();

                terminal tmp_terminal(std::cin, out, err);

                tmp_terminal.merge_env(this->env);
                tmp_terminal.run(true, true);
                this->merge_env(tmp_terminal.env);
            }

        } else {
            std::system(words[i].c_str());
        }
    }
    return return_value;
}

bool terminal::get_input_from_terminal() {
    std::string buf{};

    if (!std::getline(in, buf)) {
        return false;
    }
    in_buf << buf;

    char quote_type{};
    bool flag = quote_handler(buf, 0, quote_type);

    if (flag) {
        if (!std::getline(in, buf)) return false;
        in_buf << '\n' << buf;
    }

    size_t pos = 0;
    while (flag) {
        pos = buf.find_first_of(quote_type);
        if (pos == std::string::npos) {

            if (!std::getline(in, buf)) {
                return false;
            }

            in_buf << '\n' << buf;
        } else {

            if (quote_handler(buf, pos + 1, quote_type)) {

                if (!std::getline(in, buf)) {
                    return false;
                }

                in_buf << '\n' << buf;
            } else {
                break;
            }
        }
    }
    return true;
}

bool terminal::parse(const std::string& input_str) {
    size_t w_begin = 0;
    size_t s_begin = 0;
    bool exc       = false;

    while (s_begin < input_str.length() and input_str[s_begin] == ' ') {
        ++s_begin;
        w_begin = s_begin;
    }

    bool is_var = parse_vars(input_str, s_begin);

    if (is_var) {
        return true;
    }

    parse_words(input_str, s_begin, w_begin);
    return false;
}

bool terminal::parse_vars(const std::string& input_str, size_t s_begin) {
    size_t pos   = input_str.find_first_of('=');
    size_t space = input_str.find_first_of(' ');

    if (pos == s_begin) {
        command_not_found_exc(std::string(input_str.begin() + s_begin, input_str.begin() + space));

    } else if (pos != std::string::npos && pos < input_str.find_first_of('\"') && pos < input_str.find_first_of('\'') && pos + 1 < input_str.length()) {
        std::string var(input_str.begin() + s_begin, input_str.begin() + pos);

        for (auto c : var) {
            if (!alphabet[c]) {
                command_not_found_exc(std::string(input_str.begin() + s_begin, input_str.begin() + space)); // exception
                return false;
            }
        }
        if (pos + 1 != space) {
            parse_words(input_str, pos + 1, pos + 1);

            if (words.size() != 1) {
                command_not_found_exc(words[1]);
                return false;
            }
            env[var] = words[0];

        } else {
            command_not_found_exc(var);
        }
        return true;
    }
    return false;
}

void terminal::parse_words(const std::string& input_str, size_t s_begin, size_t w_begin) {
    char    quot_type = {};
    size_t  quot_pos  = 0;

    std::string concat{};
    std::string tmp{};

    std::unordered_map<std::string, bool> double_quoted{};

    for (size_t i = s_begin; i < input_str.length(); ++i) {
        switch (input_str[i]) {
            case ' ': {
                tmp = std::string(input_str.begin() + w_begin, input_str.begin() + i);
                parse_dollars(tmp);

                if (!concat.empty()) {
                    concat += tmp;
                    words.emplace_back(concat);
                    concat = {};
                } else if (w_begin != std::string::npos and w_begin < i) {
                    words.emplace_back(tmp);
                }
                go_spaces(input_str, w_begin, i);
                break;
            }
            case '\"': {
                quot_type = '\"';
                quot_pos = input_str.find_first_of(quot_type, i + 1);
                if (quot_pos != i + 1) {
                    if (i > 0 && input_str[i-1] != ' ') {
                        tmp = std::string(input_str.begin() + w_begin, input_str.begin() + i);
                        parse_dollars(tmp);
                        concat += tmp;
                    }
                    tmp = std::string(input_str.begin() + i + 1, input_str.begin() + quot_pos);
                    parse_dollars(tmp);

                    concat += tmp;
                } else {
                    concat += std::string(input_str.begin() + w_begin, input_str.begin() + i);
                }

                i = quot_pos;
                w_begin = i + 1;

                if (w_begin < input_str.length() and input_str[w_begin] == ' ' and !concat.empty()) {
                    words.emplace_back(concat);
                    double_quoted[concat] = true;
                    concat = {};
                }
                go_spaces(input_str, w_begin, i);
                break;
            }
            case '\'': {
                quot_type = '\'';
                quot_pos = input_str.find_first_of(quot_type, i + 1);

                if (quot_pos != i + 1) {
                    if (i > 0 && input_str[i-1] != ' ') {
                        tmp = std::string(input_str.begin() + w_begin, input_str.begin() + i);
                        parse_dollars(tmp);
                        concat += tmp;
                    }
                    concat += std::string(input_str.begin() + i + 1, input_str.begin() + quot_pos);
                } else {
                    concat += std::string(input_str.begin() + w_begin, input_str.begin() + i);
                }

                i = quot_pos;
                w_begin = i + 1;
                if (w_begin < input_str.length() and input_str[w_begin] == ' ' and !concat.empty()) {
                    words.emplace_back(concat);
                    concat = {};
                }
                go_spaces(input_str, w_begin, i);
                break;
            }
            case '|' : {
                if (!concat.empty()) {
                    words.emplace_back(concat);
                    concat = {};
                } else if (w_begin < i){
                    words.emplace_back(std::string(input_str.begin() + w_begin, input_str.begin() + i));
                }

                words.emplace_back("|");
                w_begin = i + 1;
                go_spaces(input_str, w_begin, i);
                break;
            }
            default: {
                break;
            }
        }
    }
}

void terminal::parse_dollars(std::string& word) {
    size_t d_pos = 0;
    size_t s_pos = 0;
    std::string       var{};
    std::stringstream  ss{};

    for (size_t i = 0; i < word.length(); ++i) {
        if (word[i] != '$') {
            ss << word[i];
        } else {
            d_pos = word.find_first_of('$', i + 1);
            s_pos = word.find_first_of(' ', i + 1);

            if (d_pos == std::string::npos and s_pos == std::string::npos) {
                var = std::string(word.begin() + i + 1, word.end());
            } else if (d_pos < s_pos) {
                var = std::string(word.begin() + i + 1, word.begin() + d_pos);
            } else if (s_pos < d_pos) {
                var = std::string(word.begin() + i + 1, word.begin() + s_pos);
            }
            if (env.find(var) != env.end()) {
                ss << env[var];
                i += var.length();
            } else if (var.length() == 0) {
                ss << "$";
            } else if (var.length() != 0) {
                i += var.length();
                ss << ((i + 1 < word.length()) ? "" : " ");
            }
        }
    }
    word = ss.str();
}

void terminal::go_spaces(const std::string& input_str, size_t& begin, size_t& i) {
    while(i < input_str.length() and input_str[i] == ' ') {
        ++i;
        if (input_str[i] != ' ') {
            begin = i;
            --i;
            break;
        }
    }
}

bool terminal::quote_handler(std::string& input_str, size_t pos, char& quote_type) {

    if (pos == std::string::npos || pos > input_str.length()) {
        return false;
    }

    size_t single_pos = input_str.find_first_of('\'', pos);
    size_t double_pos = input_str.find_first_of('\"', pos);

    pos = (single_pos < double_pos) ? single_pos : double_pos;
    quote_type  = (single_pos < double_pos) ? '\'' : '\"';

    bool flag = pos != std::string::npos;

    if (!flag) {
        return false;
    }

    while (true) {
        pos = input_str.find_first_of(quote_type, pos + 1);

        if (pos != std::string::npos) {

            single_pos = input_str.find_first_of('\'', pos + 1);
            double_pos = input_str.find_first_of('\"', pos + 1);

            pos  = (single_pos < double_pos) ? single_pos : double_pos;
            quote_type  = (single_pos < double_pos) ? '\'' : '\"';

            flag = pos != std::string::npos;
            if (!flag) {
                return false;
            }
        } else {
            return true;
        }
    }
}

void terminal::command_not_found_exc(const std::string& command) {
    throw std::invalid_argument(command + ": команда не найдена");
}
