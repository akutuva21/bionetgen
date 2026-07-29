## 2024-07-29 - Pre-computing lowercased values to prevent O(N*M) allocations
**Learning:** In OdeIntegrator::compile(), checking for functional rates dynamically converts rate laws to lowercase for every reaction multiplied by the number of model functions.
**Action:** Pre-compute case-transformed data outside nested loops, such as precomputing lowercase model function names in a vector prior to looping over reactions.
