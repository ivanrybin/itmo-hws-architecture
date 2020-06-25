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
#include <iterator>
#include <algorithm>
#include <string>
#include <boost/program_options/parsers.hpp>
#include <boost/program_options/variables_map.hpp>

namespace fs = std::experimental::filesystem;
namespace po = boost::program_options;

/*
 * grep_cmd - реализация абстрактного класса command,
 *            обеспечивающая функциональность команды grep.
 */
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
