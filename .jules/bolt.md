## 2025-02-12 - Prevented O(N*M) Allocations in Reaction Loop
**Learning:** `std::transform` with `::tolower` dynamically string-allocates on every iteration for `model_.getFunctions()`, inside the outer reaction iteration loop, causing large unnecessary heap allocations on large models.
**Action:** When scanning rules/reactions for functions using string transformations, ensure that the functional lowercase maps are precomputed exactly once outside the reaction iteration loop, converting `O(N_rxns * N_funcs)` memory allocations to just `O(N_funcs)`.
