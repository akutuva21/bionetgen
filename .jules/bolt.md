## 2024-05-24 - Zero-Allocation Pre-computation for Strings
**Learning:** In C++ nested loops (like `OdeIntegrator::compile()`), dynamic string compilation or transformation (e.g., lowercasing strings with `std::transform`) incurs O(N*M) allocation overhead.
**Action:** Always precompute transformations of shared values outside the loops (like function names), or check if a string is empty to avoid transforming it more than once. Use `const std::string&` where possible to avoid copies.
