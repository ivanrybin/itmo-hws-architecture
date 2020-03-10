/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * grep     - команда terminal, поиск подстроки в файле или stdout
 * grep_cmd - класс, реализующий функциональность команды grep в terminal
 *
 * Пример использования exit в terminal:
 * terminal@user:~ grep [-i] [-A n] [-w] pattern [FILE]
 */
#pragma once

#include "command.hpp"
#include <regex>

class grep_cmd : public command {
public:
    ~grep_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;

private:
    enum PARSE_GREP_RETURNS {
        NORMAL,
        BAD_KEY,
        BAD_CONTEXT_LENGTH
    };

    static void regex_handler(std::stringstream& out_buf, std::ostream& out, std::string& pattern,
                              const std::string& file_name,
                              bool is_i,
                              bool is_w,
                              size_t n,
                              bool is_pipe,
                              size_t files_cnt);

    static std::pair<int, std::string> parse_args(size_t& pos, const std::vector<std::string>& args,
                                               std::string& pattern, std::vector<std::string>& files,
                                               bool& is_i,
                                               bool& is_w,
                                               bool& is_A,
                                               size_t& n);
}; // grep_cmd

int grep_cmd::execute(std::stringstream& out_buf,
                      std::ostream& out,
                      std::ostream& err,
                      const std::vector<std::string>& args,
                      size_t& pos,
                      bool is_pipe) {

    bool is_i = false;
    bool is_w = false;
    bool is_A = false;
    size_t n = 0;

    std::string pattern{};
    std::vector<std::string> files{};

    std::pair<int, std::string> parse_info = grep_cmd::parse_args(pos, args, pattern, files, is_i, is_w, is_A, n);

    switch (parse_info.first) {
        case NORMAL: {
            if (!files.empty()) {
                for (const auto &file : files) {
                    fs::path p(file);

                    if (fs::exists(p)) {

                        if (fs::is_directory(p)) {

                            if (!is_pipe) {
                                error_message(err, "grep", file, catalog_err);
                            }

                        } else {
                            grep_cmd::regex_handler(out_buf, out, pattern, file, is_i, is_w, n, is_pipe,
                                                    files.size());
                        }

                    } else {
                        if (!is_pipe) {
                            error_message(err, "grep", file, file_catalog_not_exist);
                        }
                    }
                }
            } else {
                grep_cmd::regex_handler(out_buf, out, pattern, "", is_i, is_w, n, is_pipe, 0);
            }
            break;
        }
        case BAD_KEY: {
            if (!is_pipe) {
                error_message(err, "grep", parse_info.second, "Неверный ключ");
            }
            break;
        }
        case BAD_CONTEXT_LENGTH: {
            if (!is_pipe) {
                error_message(err, "grep", parse_info.second, "Неверный аргумент длины контекста");
            }
            break;
        }
        default: {
            break;
        }
    }
    return OK;
}

std::pair<int, std::string> grep_cmd::parse_args(size_t& pos, const std::vector<std::string>& args,
                                                 std::string& pattern, std::vector<std::string>& files,
                                                 bool& is_i,
                                                 bool& is_w,
                                                 bool& is_A,
                                                 size_t& n) {
    if (pos + 1 == args.size()) {
        return std::make_pair(BAD_KEY, "");
    }

    bool first = true;

    for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
        if (args[pos][0] == '-' && args[pos].length() != 1) {

            bool is_key = false;

            for (auto i = args[pos].begin(); i < args[pos].end(); ++i) {

                switch (*i) {
                    case '-':
                        if (!is_key) {
                            is_key = true;
                        } else {
                            return std::make_pair(BAD_KEY, args[pos]);
                        }
                        break;
                    case 'i':
                        is_i = true;
                        break;
                    case 'w':
                        is_w = true;
                        break;
                    case 'A':
                        if (i + 1 == args[pos].end()) {
                            ++pos;
                            if (pos == args.size()) {
                                return std::make_pair(BAD_CONTEXT_LENGTH, "");
                            }

                            for (i = args[pos].begin(); i < args[pos].end(); ++i) {
                                if (!isdigit(*i)) {
                                    return std::make_pair(BAD_CONTEXT_LENGTH, args[pos]);
                                }
                            }
                            if (!is_A) {
                                n = std::stoull(args[pos]);
                            }
                        } else {
                            ++i;
                            auto start = i;

                            for (; i < args[pos].end(); ++i) {
                                if (!isdigit(*i)) {
                                    return std::make_pair(BAD_CONTEXT_LENGTH, args[pos]);
                                }
                            }
                            if (!is_A) {
                                n = std::stoull(std::string(start, args[pos].end()));
                            }
                        }
                        is_A = true;
                        break;
                    default:
                        return std::make_pair(BAD_KEY, args[pos]);
                }
            }
        } else if (first) {
            pattern = args[pos];
            first = false;
        } else {
            files.emplace_back(args[pos]);
        }
    }

    --pos;

    if (pattern.empty() and files.empty()) {
        return std::make_pair(BAD_KEY, "");
    }

    return std::make_pair(NORMAL, "");
}

void grep_cmd::regex_handler(std::stringstream& out_buf,
                             std::ostream& out,
                             std::string& pattern,
                             const std::string& file_name,
                             bool is_i,
                             bool is_w,
                             size_t n,
                             bool is_pipe,
                             size_t files_cnt) {
    std::string line{};

    std::regex regx_pat((is_w) ? ("\\b" + pattern + "\\b") : pattern,
                           (is_i) ? (std::regex::icase | std::regex::ECMAScript) : std::regex::ECMAScript);

    if (files_cnt > 0) {
        std::fstream file(file_name, std::ios::in | std::ios::binary);

        while (getline(file, line)) {

            if (std::regex_search(line, regx_pat)) {

                if (!is_pipe) {
                    out << ((files_cnt > 1) ? (file_name + ":") : "") << line << std::endl;
                }
                out_buf << ((files_cnt > 1) ? (file_name + ":") : "") << line << std::endl;

                size_t i = 0;
                while (i < n and getline(file, line)) {

                    if (!is_pipe) {
                        out << ((files_cnt > 1) ? (file_name + ":") : "") << line << std::endl;
                    }
                    out_buf << ((files_cnt > 1) ? (file_name + ":") : "") << line << std::endl;

                    ++i;

                    if (std::regex_search(line, regx_pat)) {
                        i = 0;
                    }
                }
            }
        }
    } else if (files_cnt == 0) {
        std::stringstream old_buf{};
        old_buf << out_buf.rdbuf();
        out_buf.str("");
        out_buf.clear();

        while (getline(old_buf, line)) {
            if (std::regex_search(line, regx_pat)) {
                if (!is_pipe) {
                    out << line << std::endl;
                }
                out_buf <<  line << std::endl;

                size_t i = 0;
                while (i < n and getline(old_buf, line)) {

                    if (!is_pipe) {
                        out << line << std::endl;
                    }
                    out_buf << line << std::endl;

                    ++i;

                    if (std::regex_search(line, regx_pat)) {
                        i = 0;
                    }
                }
            }
        }
    }
}
