/*
 * Ivan Rybin, 2020.
 * Software Architecture, ITMO JB SE.
 *
 * Точка входа в terminal.
 *
 */
#include "terminal.hpp"

int process(int argc, char **argv) {
    terminal bash{};
    return bash.run();
}

int main (int argc, char **argv) {
    return process(argc, argv);
}
