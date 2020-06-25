#include "grep_cmd.hpp"

/*
 *  Метод grep_cmd::execute реализует абстрактный метод command::execute,
 *  реализуя функциональность команды bash - grep.
 */
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

            for (;pos < args.size() and args[pos] != "|"; ++pos) {}
            --pos;

            break;
        }
        case BAD_CONTEXT_LENGTH: {
            if (!is_pipe) {
                error_message(err, "grep", parse_info.second, "Неверный аргумент длины контекста");
            }

            for (;pos < args.size() and args[pos] != "|"; ++pos) {}
            --pos;

            break;
        }
        default: {
            break;
        }
    }
    return OK;
}

/*
 * Метод grep_cmd::parse_args отвечает за разбор строки на токены, используя boost::program_options.
 */
std::pair<int, std::string> grep_cmd::parse_args(size_t& pos,
                                                 const std::vector<std::string>& args,
                                                 std::string& pattern,
                                                 std::vector<std::string>& files,
                                                 bool& is_i,
                                                 bool& is_w,
                                                 bool& is_A,
                                                 size_t& n) {
    if (pos + 1 == args.size()) {
        return std::make_pair(BAD_KEY, "");
    }

    bool first = true;

// BOOST ---------------------------------------------------------------------------------------------------------------
    ++pos;
    if (pos < args.size() && args[pos] != "|") {
        auto pos_end = size_t(pos);
        for (; pos_end < args.size() && args[pos_end] != "|"; ++pos_end);

        std::vector<std::string> args_to_parse(args.begin() + pos, args.begin() + pos_end);

        po::options_description desc("grep options");
        desc.add_options()
                ("IGNORE_CASE,i", "ignore case option")
                ("WORD,w", "find only whole word")
                ("AFTER,A", po::value<size_t>(), "-A n, n lines after match")
                ;

        po::variables_map vm;

        try {
            po::store(po::command_line_parser(args_to_parse).options(desc).run(), vm);
            po::notify(vm);
        } catch (boost::wrapexcept<boost::program_options::invalid_option_value>& e1) {
            return std::make_pair(BAD_CONTEXT_LENGTH, "bad_context");

        } catch (boost::wrapexcept<boost::program_options::unknown_option>& e2) {
            return std::make_pair(BAD_KEY, e2.get_option_name());

        } catch (std::exception& e3) {
            return std::make_pair(BAD_KEY, "bad key");
        }


        is_i = vm.count("IGNORE_CASE");
        is_w = vm.count("WORD");
        is_A = vm.count("AFTER");

        if (is_A) {
            n = vm["AFTER"].as<size_t>();
        }

    }
// BOOST ---------------------------------------------------------------------------------------------------------------

    for (; pos < args.size() and args[pos] != "|"; ++pos) {
        if (args[pos][0] == '-' && args[pos].length() != 1) {
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

/*
 * Метод grep_cmd::regex_handler отвечает за разбор регулярных выражений в строке.
 */
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