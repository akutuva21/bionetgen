## 2023-10-27 - Cache String Transformations in Loops
**Learning:** Pre-allocating strings and caching boolean state for lowercased text (`std::transform` with `std::tolower`) inside reaction compilation loops in C++ prevents repeated heap allocations and slow O(N) loops when testing against many functional rate names, avoiding severe compilation overheads.
**Action:** Always hoist case conversion outside of the inner match loop or cache it across iterations when checking string tokens against multiple keywords or functions.
