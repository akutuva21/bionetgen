## 2024-08-13 - Defer and cache rate law lowercasing in ODE compilation
**Learning:** Unconditional string allocations and transformations inside nested loops cause severe performance regressions, especially for models with many reactions, as they create O(N*M) unnecessary operations.
**Action:** Defers the creation and std::transform lowercasing of rate law strings in OdeIntegrator::compile() until they are explicitly needed for function name matching, and caches the result for subsequent checks.
