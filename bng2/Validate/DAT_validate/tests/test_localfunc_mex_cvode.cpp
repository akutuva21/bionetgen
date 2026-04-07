#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_all.hpp>
#include <iostream>
#include <sstream>
#include <cstdarg>
#include <cstdio>

// Mock mexPrintf to avoid linking MATLAB libraries
std::ostringstream mexOutput;
extern "C" void mexPrintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    char buffer[1024];
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    mexOutput << buffer;
    va_end(args);
}

// Mock other functions required by localfunc_mex_cvode.c
extern "C" void mexErrMsgTxt(const char* err) {
    mexOutput << "ERROR: " << err;
}

extern "C" int mxGetM(const void* pm) { return 2; }
extern "C" int mxGetN(const void* pm) { return 1; }
extern "C" double* mxGetPr(const void* pm) { return nullptr; }
extern "C" void* mxCreateDoubleMatrix(int m, int n, int ComplexFlag) { return nullptr; }

extern "C" {
    int check_flag(void *flagvalue, char *funcname, int opt);
}

TEST_CASE("check_flag function validation", "[cvode][mex]") {
    // Reset output capture before each test
    mexOutput.str("");
    mexOutput.clear();

    int dummy_val = 1;
    void *valid_ptr = &dummy_val;
    char func_name1[] = "test_alloc_success";
    char func_name2[] = "test_alloc_fail";

    SECTION("opt == 0 (pointer allocation check)") {
        REQUIRE(check_flag(valid_ptr, func_name1, 0) == 0);
        REQUIRE(mexOutput.str().empty());

        REQUIRE(check_flag(NULL, func_name2, 0) == 1);
        REQUIRE(mexOutput.str().find("SUNDIALS_ERROR: test_alloc_fail() failed - returned NULL pointer") != std::string::npos);
    }

    char func_name3[] = "test_flag_pos";
    char func_name4[] = "test_flag_zero";
    char func_name5[] = "test_flag_neg";

    SECTION("opt == 1 (flag value check)") {
        int err_flag_pos = 1;
        int err_flag_zero = 0;
        int err_flag_neg = -1;

        REQUIRE(check_flag(&err_flag_pos, func_name3, 1) == 0);
        REQUIRE(mexOutput.str().empty());

        REQUIRE(check_flag(&err_flag_zero, func_name4, 1) == 0);
        REQUIRE(mexOutput.str().empty());

        REQUIRE(check_flag(&err_flag_neg, func_name5, 1) == 1);
        REQUIRE(mexOutput.str().find("SUNDIALS_ERROR: test_flag_neg() failed with flag = -1") != std::string::npos);
    }

    char func_name6[] = "test_mem_success";
    char func_name7[] = "test_mem_fail";

    SECTION("opt == 2 (memory allocation check)") {
        REQUIRE(check_flag(valid_ptr, func_name6, 2) == 0);
        REQUIRE(mexOutput.str().empty());

        REQUIRE(check_flag(NULL, func_name7, 2) == 1);
        REQUIRE(mexOutput.str().find("MEMORY_ERROR: test_mem_fail() failed - returned NULL pointer") != std::string::npos);
    }

    char func_name8[] = "test_unknown_opt";

    SECTION("unhandled opt values") {
        REQUIRE(check_flag(NULL, func_name8, 3) == 0);
        REQUIRE(mexOutput.str().empty());
    }
}
