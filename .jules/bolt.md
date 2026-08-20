## 2024-05-15 - Remove duplicate lowercase operations in OdeIntegrator::compile
**Learning:** In execution flow where the exact string manipulations (like lower-casing via `std::transform`) are used across different conditions for a given variable inside a loop, they will unnecessarily consume CPU time due to redundant string allocations and iterations if repeatedly called.
**Action:** Cache the transformed strings outside the conditional blocks (using a state variable or boolean flag) if the original string content hasn't changed.
