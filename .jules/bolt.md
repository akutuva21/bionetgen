## 2024-05-15 - Replace std::regex with manual string parsing
**Learning:** Even pre-compiled `static const std::regex` objects incur significant overhead in loops because `std::regex_search` and `std::smatch` perform heap allocations.
**Action:** For performance-critical code, replace regex with manual string operations like `std::string::find` and `std::string::substr`.

## 2024-05-15 - Replace std::transform with manual for loops
**Learning:** `std::transform` with `std::tolower` inside a tight loop introduces overhead compared to manual loop iteration.
**Action:** For performance-critical paths where strings must be mutated in-place, replace `std::transform` with a manual `for` loop.
