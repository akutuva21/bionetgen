add_executable(test_run_network test_run_network.cpp)
target_link_libraries(test_run_network PRIVATE Catch2::Catch2WithMain Catch2::Catch2)

# Pass the absolute path to the bng2 run_network executable
# Using CMAKE_CURRENT_SOURCE_DIR to be safe if tests is built as the root
target_compile_definitions(test_run_network PRIVATE
    RUN_NETWORK_PATH="${CMAKE_CURRENT_SOURCE_DIR}/../bng2/Network3/run_network"
)

include(Catch)
catch_discover_tests(test_run_network)
