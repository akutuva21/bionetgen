## 2024-05-24 - Pre-compute rate law string lowering to avoid redundant allocations

**Learning:** In C++, repeatedly transforming strings dynamically inside loops incurs significant overhead due to memory allocation and iteration costs, even for strings that have already been allocated/copied. In `OdeIntegrator::compile()`, `rawRateLaw` was being repeatedly lowered into `lowerRawRL` in independent `if` blocks.

**Action:** Consolidate redundant local variables and pre-compute lowercased copies of string references where they are repeatedly checked for substrings (e.g. `std::string::find`) or bounds (`hasWordBoundaryMatch`) across multiple conditional flows.
