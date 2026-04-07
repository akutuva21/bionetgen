# Need to compile the actual C file
add_library(localfunc_mex_cvode_lib OBJECT ${CMAKE_CURRENT_SOURCE_DIR}/../localfunc_mex_cvode.c)
target_include_directories(localfunc_mex_cvode_lib PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
# Suppress the string constant to char* warnings
set_target_properties(localfunc_mex_cvode_lib PROPERTIES COMPILE_FLAGS "-Wno-write-strings")

add_executable(test_bng_mex_cvode test_localfunc_mex_cvode.cpp)
target_link_libraries(test_bng_mex_cvode Catch2::Catch2WithMain localfunc_mex_cvode_lib)
target_include_directories(test_bng_mex_cvode PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
add_test(NAME bng_mex_cvode_test COMMAND test_bng_mex_cvode)
