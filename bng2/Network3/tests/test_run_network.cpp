#include <catch2/catch_test_macros.hpp>
#include <unistd.h>
#include <sys/wait.h>
#include <iostream>
#include <string>
#include <sstream>

#define XSTR(x) STR(x)
#define STR(x) #x

// We can test this by running the executable with < 4 arguments (or with an unknown argument but the < 4 check calls print_error directly)

TEST_CASE("print_error usage output and exit code", "[run_network][print_error]") {
    int pipefd[2];
    REQUIRE(pipe(pipefd) == 0);

    pid_t pid = fork();
    REQUIRE(pid >= 0);

    if (pid == 0) {
        // Child
        close(pipefd[0]);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        // execl with run_network using the absolute path provided by CMake
        const char* binary_path = "./run_network";
        execl(binary_path, binary_path, NULL);

        exit(127); // If execl fails
    } else {
        // Parent
        close(pipefd[1]);

        char buffer[1024];
        std::string output;
        ssize_t bytes_read;
        while ((bytes_read = read(pipefd[0], buffer, sizeof(buffer) - 1)) > 0) {
            buffer[bytes_read] = '\0';
            output += buffer;
        }
        close(pipefd[0]);

        int status;
        waitpid(pid, &status, 0);

        // Verify exit status is 1
        REQUIRE(WIFEXITED(status));
        REQUIRE(WEXITSTATUS(status) == 1);

        // Verify correct usage message
        REQUIRE(output.find("Usage:") != std::string::npos);
        REQUIRE(output.find("run_network  [-bcdefkmsvx] [-a atol]") != std::string::npos);
        REQUIRE(output.find("netfile sample_time n_sample") != std::string::npos);
        REQUIRE(output.find("netfile t1 t2 ... tn") != std::string::npos);
    }
}
