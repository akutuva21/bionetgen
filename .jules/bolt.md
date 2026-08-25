## 2024-05-24 - Zero-allocation Case-Insensitive String Boundary Matching
**Learning:** In C++, avoiding dynamic allocations (like `std::string` and `std::transform`) inside loops for case-insensitive matching significantly improves performance. Using an iterative `std::string_view` approach with `std::tolower` allows zero-allocation boundary matching.
**Action:** Always prefer `std::string_view` and character-wise transformations over `std::transform` when doing repeated substring checks inside loops.
