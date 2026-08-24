## 2024-08-24 - Cache string transformation states in loops
**Learning:** Inside inner loops (like reaction parsing in OdeIntegrator), repeatedly lowercasing the same string for case-insensitive matching causes significant overhead due to memory allocations and char transformations.
**Action:** When a string needs to be lowercased potentially multiple times in a sequence of checks, declare the string and a boolean flag (`lowerRawRLComputed = false`) outside the conditional blocks. Only perform `std::transform` once and update the flag to reuse the pre-computed lowercased string.
