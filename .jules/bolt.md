## 2024-05-14 - Cache PatternGraphs in HybridModelGenerator
**What:** Added a `PatternGraph` cache (`std::unordered_map` with a `std::mutex`) to memoize the parsing of species and patterns within `isIsomorphic` and `countMatches` of `HybridModelGenerator`.
**Why:** Re-parsing the strings using ANTLR on every call within nested loops caused significant performance degradation.
**Impact:** Massive speedup (~584x per operation) to `generate_hybrid_model` execution time during BNGL network processing by circumventing redundant compilation overhead.
**Measurement:** The `isIsomorphic` benchmark improved from ~20.93ms to ~35us (a 584x speedup per execution).
## 2024-05-15 - Replace std::regex with std::string for parsing performance
**Learning:** `std::regex` compilation and matching inside loops in C++ causes massive performance degradation due to state machine overhead.
**Action:** Always prefer native `std::string::find` and `std::string::substr` operations over `std::regex` when parsing simple patterns like parentheses blocks or specific prefix tags in hot code paths.
