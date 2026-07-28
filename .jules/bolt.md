## 2024-06-25 - [Precomputing transformed strings outside loops]
**Learning:** In C++, repeatedly allocating strings and case-transforming them (`std::transform` with `std::tolower`) inside nested loops over large datasets (like `OdeIntegrator::compile()`) creates severe $O(N \times M)$ overhead.
**Action:** Always inspect nested loops for any string operations or data that can be precomputed or cached in the outer scope, turning $O(N \times M)$ transformations into $O(N)$ lookups.
