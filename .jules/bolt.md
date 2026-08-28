## 2024-05-18 - String allocations in tight loops
**Learning:** In C++, constructing `std::string` objects (e.g. from string literals or substrings) inside tight loops creates significant memory allocation overhead, even for small strings, due to construction/destruction churn.
**Action:** Use `std::string_view` for non-owning string references and hoist reusable `std::string` buffers outside loops to reuse their heap allocation via `.clear()`.
