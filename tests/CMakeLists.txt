add_executable(localfunc_test localfunc_test.cpp)
target_include_directories(localfunc_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/mocks
    ${sundials_SOURCE_DIR}/include
    ${sundials_BINARY_DIR}/include
)
target_link_libraries(localfunc_test PRIVATE
    Catch2::Catch2WithMain
    sundials_nvecserial_static
    sundials_cvode_static
)
add_test(NAME localfunc_test COMMAND localfunc_test)
