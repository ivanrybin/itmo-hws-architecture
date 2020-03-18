/*
 * Elizaveta Sidorova, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * ls - команда terminal, выводит список файлов и директорий. Принимает 0 или 1 аргумент. 
 * ls без аргументов выводит список файлов и директорий в текущей директории,
 * ls path, выводит список файлов и директорий в директории path, где path -- полный путь. 
 * ls directory выводит список файлов и директорий в директории pwd/directory.
 *
 * Пример использования ls в terminal:
 * terminal@user:~ ls 
 * terminal@user:~ ls path
 * terminal@user:~ ls directory
 */

#pragma once
#include "command.hpp"

namespace fs = std::experimental::filesystem;

class ls_cmd : public command {
public:
    ~ls_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // ls_cmd

int ls_cmd::execute(std::stringstream& out_buf,
                          std::ostream& out,
                          std::ostream& err,
                          const std::vector<std::string>& args,
                          size_t& pos,
                          bool is_pipe) {
   
    out_buf.str("");
    out_buf.clear();
    size_t count_of_args = 0;
    size_t old_pos = pos;
    for (pos = pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
        count_of_args++; 
    }

    if (count_of_args != 0 && count_of_args != 1) {
        out << "error count of args for command ls" << std::endl;
        pos--;
        return OK;
    }
    
    size_t pos_stop = pos;

    std::string current_path = std::string(fs::current_path());
    std::string path = current_path;
 
    if (count_of_args == 0) {
        for (auto & p : fs::directory_iterator(path)) {
            if (!is_pipe) {
                out << p.path().filename() << std::endl;
            }
            out_buf << p.path().filename() << std::endl;
        }
    }

    if (count_of_args == 1) {
        for (pos = old_pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
           path = args[pos];
           const auto & p = fs::path(path);
           if (!is_directory(p)) {
               path = current_path + path;
           }
           const auto & p2 = fs::path(path);
           if (!is_directory(p2)) {
               out << "error args for command ls" << std::endl;
               pos = pos_stop;
               pos--;
               return OK;
           }
           for (auto & p : fs::directory_iterator(path)) {
               if (!is_pipe) {
                   out << p.path().filename() << std::endl;
               }
               out_buf << p.path().filename() << std::endl;
           }
        }
    }

    if (!is_pipe) {
        out << std::endl;
    }
    out_buf << std::endl;

    --pos;
    return OK;
}
