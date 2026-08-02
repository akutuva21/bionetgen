## 2024-11-20 - Avoid Repetitive String Transformation

**Learning:** In C++, avoid repetitive string allocations and case-transformations (`std::transform` with `std::tolower`) inside loops for case-insensitive comparisons. In `OdeIntegrator::compile()`, `std::transform` was heavily used on each inner iteration over model functions inside reaction iteration.

**Action:** Use an inline iterator-based case-insensitive equality check (e.g., `std::search` with a custom case-insensitive lambda, like our custom `hasWordBoundaryMatchI`) for zero-allocation performance. We implemented this in `src/engine/OdeIntegrator.cpp`.
