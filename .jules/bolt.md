## 2024-05-14 - Cache PatternGraphs in HybridModelGenerator
**What:** Added a `PatternGraph` cache (`std::unordered_map` with a `std::mutex`) to memoize the parsing of species and patterns within `isIsomorphic` and `countMatches` of `HybridModelGenerator`.
**Why:** Re-parsing the strings using ANTLR on every call within nested loops caused significant performance degradation.
**Impact:** Massive speedup (~584x per operation) to `generate_hybrid_model` execution time during BNGL network processing by circumventing redundant compilation overhead.
**Measurement:** The `isIsomorphic` benchmark improved from ~20.93ms to ~35us (a 584x speedup per execution).
## 2024-05-19 - Replace std::regex with manual parsing in loops
**Learning:** `std::regex` operations (like `std::regex_search` and `std::regex_match`) have significant overhead in C++ and can become performance bottlenecks when executed dynamically inside hot loops or heavily parsed files (like AST models in BNG).
**Action:** Replaced dynamic `std::regex` creations and evaluations inside parsing loops in `MacroBNGModel.cpp` and `PopulationMappingRule.cpp` with manual string traversal and `find`/`compare` standard library methods. This completely removes the regex state-machine initialization and lookup overhead.
