## 2024-05-24 - Buffer Overflow via `sprintf`
**Vulnerability:** The codebase uses `sprintf` to format strings into fixed-size buffers like `char buf[1000]`. This could lead to a buffer overflow if the generated string exceeds 1000 bytes.
**Learning:** Legacy C code often used `sprintf` before `snprintf` was widely standardized. Replacing it is a standard security practice, but one must ensure the size argument to `snprintf` is correct (e.g., using `sizeof(buf)` when it's an array).
**Prevention:** Always use `snprintf` or modern C++ string formatting tools (like `std::string` concatenation or `std::ostringstream`) to prevent buffer overflows.
