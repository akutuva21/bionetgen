#include <catch2/catch_test_macros.hpp>
#include <unistd.h>
#include <sys/wait.h>
#include <string>
#include <iostream>

#ifndef RUN_NETWORK_PATH
#define RUN_NETWORK_PATH "../bng2/Network3/run_network"
#endif

TEST_CASE("run_network print_error calls exit(1) and prints usage", "[run_network]") {
    int pipefd[2];
    REQUIRE(pipe(pipefd) == 0);

    pid_t pid = fork();
    REQUIRE(pid >= 0);

    if (pid == 0) {
        // Child process
        close(pipefd[0]); // Close read end

        // Redirect stderr to the pipe to capture output
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        // Execute run_network without arguments
        execl(RUN_NETWORK_PATH, "run_network", nullptr);

        // If execl fails
        std::cerr << "execl failed: " << RUN_NETWORK_PATH << std::endl;
        exit(2);
    } else {
        // Parent process
        close(pipefd[1]); // Close write end

        // Read captured output
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

        // Verify printed output contains the usage text from print_error()
        REQUIRE(output.find("Usage:") != std::string::npos);
        REQUIRE(output.find("run_network  [-bcdefkmsvx]") != std::string::npos);
    }
}
