## 2024-07-15 - [Avoid std::regex compilation inside loops]
**Learning:** `std::regex` compilation is extremely slow in C++. Instantiating or evaluating dynamic `std::regex` objects in a tight loop incurs heavy performance penalties (up to ~200x slower than static initialization).
**Action:** Always extract `std::regex` definitions as `static const std::regex` when the pattern does not change, to compile the regular expression state machine exactly once.
