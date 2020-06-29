/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 */
#include "wc_cmd.hpp"

/*
 *  Метод wc_cmd::words_lines_counter вспомогательная функция wc_cmd,
 *  подсчитывающая размер файла, число строк и слов, входящих в него.
 *
 *  Используется в wc_cmd::execute.
 */
void wc_cmd::words_lines_counter(std::istream& stream, size_t& f_size,  size_t& l_cnt,   size_t& w_cnt,
                                 size_t& f_total, size_t& l_total, size_t& w_total) {

    std::string tmp{};

    l_cnt = std::count(std::istreambuf_iterator<char>(stream),std::istreambuf_iterator<char>(), '\n');
    stream.seekg(0, std::ifstream::beg);

    while (stream >> tmp) {
        ++w_cnt;
    }
    f_total += f_size;
    l_total += l_cnt;
    w_total += w_cnt;
}

/*
 *  Метод wc_cmd::execute реализует абстрактный метод command::execute,
 *  реализуя функциональность команды bash - wc.
 */
int wc_cmd::execute(std::stringstream& out_buf,
                    std::ostream& out,
                    std::ostream& err,
                    const std::vector<std::string>& args,
                    size_t& pos,
                    bool is_pipe) {
    std::string buf{};
    size_t f_cnt    = 0;
    size_t l_cnt    = 0;
    size_t w_cnt    = 0;
    size_t f_size   = 0;
    size_t f_total  = 0;
    size_t l_total  = 0;
    size_t w_total  = 0;
    if ((pos + 1 >= args.size() || (pos + 1 < args.size() && args[pos + 1] == "|")) and !out_buf.str().empty()) {

        f_size = out_buf.str().size();
        words_lines_counter(out_buf, f_size, l_cnt, w_cnt, f_total, l_total, w_total);

        out_buf.str("");
        out_buf.clear();

        if (!is_pipe) {
            out << " " << l_cnt << "\t" << w_cnt << "\t" << f_size << std::endl;
        }
        out_buf << " " << l_cnt << "\t" << w_cnt << "\t" << f_size << std::endl;

    } else {
        out_buf.str("");
        out_buf.clear();

        for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
            fs::path p(args[pos]);

            if (fs::exists(p)) {

                if (fs::is_directory(p)) {

                    if (!is_pipe) {
                        out << "wc: " << args[pos] << ": Это каталог" << std::endl;
                        out << "\t0\t0\t0 " << args[pos] << std::endl;
                    }

                    out_buf << "wc: " << args[pos] << ": Это каталог";
                    out_buf << "\t0\t0\t0 " << args[pos] << std::endl;

                } else {
                    std::fstream file(args[pos]);

                    f_size = fs::file_size(p);
                    words_lines_counter(file, f_size, l_cnt, w_cnt, f_total, l_total, w_total);

                    file.close();

                    if (!is_pipe) {
                        out << " " << l_cnt << "\t" << w_cnt << "\t" << f_size << " " << args[pos] << std::endl;
                    }
                    out_buf << " " << l_cnt << "\t" << w_cnt << "\t" << f_size << " " << args[pos] << std::endl;

                    ++f_cnt;
                    w_cnt = 0;
                }
            } else {
                if (!is_pipe) {
                    error_message(err, "wc", args[pos], file_catalog_not_exist);
                }
            }
        }
        --pos;
    }
    if (f_cnt > 1) {
        if (!is_pipe) {
            out << " " << l_total << "\t" << w_total << "\t" << f_total << " итого" << std::endl;
        }
        out_buf << " " << l_total << "\t" << w_total << "\t" << f_total << " итого" << std::endl;
    }

    return OK;
}
