/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "cat_cmd.hpp"

/*
 * Метод cat_cmd::execute реализует абстрактный метод command::execute,
 * реализуя функциональность команды bash - cat.
 */
int cat_cmd::execute(std::stringstream& out_buf,
                     std::ostream& out,
                     std::ostream& err,
                     const std::vector<std::string>& args,
                     size_t& pos,
                     bool is_pipe) {

    if (pos + 1 == args.size() && !out_buf.str().empty()) {
        if (!is_pipe) {
            out << out_buf.str();
        }
        out_buf.str("");
        out_buf.clear();
    } else if (pos + 1 == args.size() && out_buf.str().empty()) {
        std::string input_str{};

        while(!getline(std::cin, input_str).eof()) {
            if (input_str == "^C") {
                break;
            }

            if (!is_pipe) {
                out << input_str << std::endl;
            }
            out_buf << input_str << std::endl;
        }

    } else {
        out_buf.str("");
        out_buf.clear();

        for (pos = pos + 1; pos < args.size() && args[pos] != "|"; ++pos) {
            fs::path p(args[pos]);

            if (fs::exists(p)) {

                if (fs::is_directory(p)) {

                    if (!is_pipe) {
                        error_message(err, "cat", args[pos], catalog_err);
                    }

                } else {
                    std::ifstream file(p, std::ios::out | std::ios::binary);

                    if (file.is_open()) {
                        if (!is_pipe) {
                            out << file.rdbuf() << std::endl;
                            file.seekg(0, std::istream::beg);
                        }
                        out_buf  << file.rdbuf();
                        file.close();
                    }
                }
            } else {
                if (!is_pipe) {
                    error_message(err, "cat", args[pos], file_catalog_not_exist);
                }
            }
        }
        --pos;
    }
    return OK;
}
