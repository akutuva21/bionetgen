## 2024-05-14 - Cache PatternGraphs in HybridModelGenerator
**What:** Added a `PatternGraph` cache (`std::unordered_map` with a `std::mutex`) to memoize the parsing of species and patterns within `isIsomorphic` and `countMatches` of `HybridModelGenerator`.
**Why:** Re-parsing the strings using ANTLR on every call within nested loops caused significant performance degradation.
**Impact:** Massive speedup (~584x per operation) to `generate_hybrid_model` execution time during BNGL network processing by circumventing redundant compilation overhead.
**Measurement:** The `isIsomorphic` benchmark improved from ~20.93ms to ~35us (a 584x speedup per execution).
## 2026-07-09 - Avoid dynamic std::regex instantiation in parsing loops
**Learning:** Constructing `std::regex` objects dynamically inside parsing loops or frequently called functions (like `pre_macr` or `hash_sor`) incurs significant state machine compilation overhead, degrading parsing performance. Variable-dependent regexes (e.g., `std::regex(name + "(...)")`) cannot be effectively cached as `static const` and should be substituted with direct standard string methods like `std::string::find`.
**Action:** When working in C++ codebase (especially `MacroBNGModel.cpp` and `PopulationMappingRule.cpp`), review and modify `std::regex` usage in inner loops or frequent parsing routines by changing them to `static const` or avoiding regexes entirely where possible via direct string manipulation methods.
