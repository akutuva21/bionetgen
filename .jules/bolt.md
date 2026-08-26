## 2024-05-24 - Avoid redundant case-transformations in loops
**Learning:** In C++, converting strings to lowercase within a loop over reactions (like `std::transform(lowerRawRL.begin(), lowerRawRL.end(), ...)` inside `OdeIntegrator::compile()`) creates unnecessary memory allocations and transformations for every reaction. Also, the same transformation (`std::transform`) might be done multiple times in the same iteration (e.g. at line 545 and then again at line 598).
**Action:** Do string transformations only once and cache the result for the entire inner loop execution, or use case-insensitive equality checks if applicable. Avoid repeatedly performing operations like lowercase conversion in nested/inner loops.

## 2024-05-24 - Reuse string buffer allocations
**Learning:** Re-declaring a new `std::string` object inside a loop (like iterating through reactions in `OdeIntegrator::compile()`) results in a heap memory allocation in every loop iteration (if the string exceeds SSO capacity).
**Action:** Declare string objects that are repeatedly overwritten and manipulated outside of the loop so the underlying heap buffer can be reused, avoiding allocator churn.
