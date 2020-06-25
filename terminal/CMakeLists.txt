cmake_minimum_required(VERSION 3.8)

project(terminal)

set(CMAKE_CXX_STANDARD 17)

include_directories(.)

find_package(Boost 1.73.0 COMPONENTS program_options REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

add_executable(boost_TEST src/boost_test.cpp)

target_link_libraries(boost_TEST ${Boost_LIBRARIES})

# run mode
add_executable(terminal
                src/main.cpp
                src/terminal.cpp
                src/cli/commands.cpp
                src/cli/commands/command.cpp
                src/cli/commands/wc_cmd.cpp
                src/cli/commands/cat_cmd.cpp
                src/cli/commands/exit_cmd.cpp
                src/cli/commands/pwd_cmd.cpp
                src/cli/commands/echo_cmd.cpp
                src/cli/commands/grep_cmd.cpp
               )

target_link_libraries(terminal stdc++fs ${Boost_LIBRARIES})

# test mode
add_executable(test src/test.cpp
                src/terminal.cpp
                src/cli/commands.cpp
                src/cli/commands/command.cpp
                src/cli/commands/wc_cmd.cpp
                src/cli/commands/cat_cmd.cpp
                src/cli/commands/exit_cmd.cpp
                src/cli/commands/pwd_cmd.cpp
                src/cli/commands/echo_cmd.cpp
                src/cli/commands/grep_cmd.cpp
                )

target_link_libraries(test stdc++fs ${Boost_LIBRARIES})
