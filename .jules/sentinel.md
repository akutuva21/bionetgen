## 2025-02-23 - Buffer Overflow Fix with snprintf in Network3
**Vulnerability:** The C codebase (`bng2/Network3/src/`) used `sprintf` to format strings into fixed-size local stack buffers (e.g., `char buf[1000]`), which is susceptible to buffer overflow if inputs like `prefix` or `outpre` are large.
**Learning:** `sprintf` lacks bounds checking and must be consistently avoided when writing paths or concatenating strings, especially in C++ string manipulation.
**Prevention:** Always use `snprintf(buf, sizeof(buf), ...)` for stack-allocated arrays to ensure strict bounds checking. Ensure temporary test or script files are cleaned up or added to `.gitignore`.
