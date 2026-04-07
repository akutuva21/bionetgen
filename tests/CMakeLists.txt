# Ensure the bng2/Network3 target is built
add_subdirectory(../bng2/Network3 bng2_Network3)

add_executable(test_run_network test_run_network.cpp)
target_link_libraries(test_run_network PRIVATE Catch2::Catch2WithMain Catch2::Catch2)

# Make test_run_network explicitly depend on run_network so it builds first
add_dependencies(test_run_network run_network)

# Pass the absolute path to the compiled run_network executable
target_compile_definitions(test_run_network PRIVATE
    RUN_NETWORK_PATH="$<TARGET_FILE:run_network>"
)

include(Catch)
catch_discover_tests(test_run_network)
