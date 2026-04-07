#include <iostream>
#include <string>
#include <cassert>

// This file is tested via Catch2 or another framework, but for now we write a basic custom main
// to test print_error directly if we can isolate it, or we could compile it with network files.

void print_error(); // prototype

int main() {
    // print_error() calls exit(1). It's hard to test without fork/exec.
    // Instead, I'll compile with Catch2, or write a bash script to test the exit code.
    return 0;
}
