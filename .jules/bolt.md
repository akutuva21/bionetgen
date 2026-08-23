## 2024-05-18 - Optimized compileGroups and string allocations
**Learning:** Found unnecessary string allocations inside nested loops and redundant parser compilation. In C++, repeated allocations and case-transformations (`std::transform` with `std::tolower`) inside loops should be avoided. Also, parsing patterns inside nested loops causes significant overhead.
**Action:** Lift `std::string` allocations outside loops and cache transformed strings. Pre-parse observable patterns before the inner species loop in `compileGroups()`.
