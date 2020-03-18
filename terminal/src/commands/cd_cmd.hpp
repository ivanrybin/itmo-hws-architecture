/*
 * Elizaveta Sidorova, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * cd - команда terminal, меняет текущую директорию. Принимает 0 или 1 аргумент. 
 * cd без аргументов переходит в root directory.
 * cd . -- не меняет текущей директории.
 * cd .. -- переходит в родительскую директорию,
 * cd path -- меняет текущую директорию на path, если это возможно. Иначе -- выводит сообщение об ошибке. 
 * cd_cmd - класс, реализующий функциональность команды cd в terminal
 *
 * Пример использования echo в terminal:
 * terminal@user:~ cd ..
 */

#pragma once
#include <unistd.h>
#include "command.hpp"

namespace fs = std::experimental::filesystem;

class cd_cmd : public command {
public:
    ~cd_cmd() override = default;
    int execute(std::stringstream& out_buf,
                std::ostream& out,
                std::ostream& err,
                const std::vector<std::string>& args,
                size_t& pos,
                bool is_pipe) override;
}; // cd_cmd

int cd_cmd::execute(std::stringstream& out_buf,
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

    size_t pos_stop = pos;

    if (count_of_args != 0 && count_of_args != 1) {
        out << "error count of args for command cd" << std::endl;
        pos--;
        return OK;
    }

    std::string current_path = std::string(fs::current_path());
    std::string newDir = current_path;
    if (count_of_args == 0) {
         newDir = std::string(fs::current_path().root_path());
    }

    if (count_of_args == 1) {
        for (pos = old_pos + 1; pos < args.size() and args[pos] != "|"; ++pos) {
            if (args[pos] ==  ".") {
                break;
            }
            if (args[pos] ==  "..") {
                newDir = std::string(fs::current_path().parent_path());
                break;
            }
            newDir = args[pos];
        }
    }

    int rc = chdir(newDir.c_str());
    if (rc < 0) {
         newDir = current_path + newDir;
         rc = chdir(newDir.c_str());
         if (rc < 0) {
             out << "error args for command cd" << std::endl;
             pos = pos_stop;
             pos--;
             return OK;
         }
    } 

    if (!is_pipe) {
        out << "new current directory: " <<  std::string(fs::current_path()) << std::endl;
    } else {
        out_buf << "new current directory: " <<  std::string(fs::current_path()) << std::endl;
    }

    if (!is_pipe) {
        out << std::endl;
    }
    out_buf << std::endl;

    --pos;
    return OK;
}

