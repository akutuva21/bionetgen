## 2024-05-14 - Cache PatternGraphs in HybridModelGenerator
**What:** Added a `PatternGraph` cache (`std::unordered_map` with a `std::mutex`) to memoize the parsing of species and patterns within `isIsomorphic` and `countMatches` of `HybridModelGenerator`.
**Why:** Re-parsing the strings using ANTLR on every call within nested loops caused significant performance degradation.
**Impact:** Massive speedup (~584x per operation) to `generate_hybrid_model` execution time during BNGL network processing by circumventing redundant compilation overhead.
**Measurement:** The `isIsomorphic` benchmark improved from ~20.93ms to ~35us (a 584x speedup per execution).

## 2024-05-14 - Inline Regex Compilation Overhead
**Learning:** Compiling `std::regex` objects dynamically inside tight loops or string replacement functions causes extreme performance degradation due to state machine initialization overhead. Additionally, when a regex pattern depends on a runtime variable, it cannot be safely cached as `static const`.
**Action:** Extract constant regex patterns into `static const std::regex` variables (or wrap inline `std::regex_match`/`std::regex_search` calls with IILEs to return a static reference). For variable-dependent patterns, refactor to use direct string manipulation (e.g., `std::string::find` and `std::string::substr`) instead of `std::regex`.
