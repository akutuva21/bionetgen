with open("tests/CMakeLists.txt", "r") as f:
    content = f.read()

content = content.replace(
    'target_link_libraries(test_network_generator PRIVATE Catch2::Catch2WithMain Catch2::Catch2 bng_engine bng_ast)',
    'target_link_libraries(test_network_generator PRIVATE Catch2::Catch2WithMain Catch2::Catch2 bng_engine bng_ast bng_parser)'
)

with open("tests/CMakeLists.txt", "w") as f:
    f.write(content)
