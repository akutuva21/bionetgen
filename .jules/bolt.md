## 2024-05-14 - Precompute transformed strings to avoid O(N x M) loops
**Learning:** `std::transform` inside a nested loop can cause $O(N \times M)$ overhead due to repetitive transformations and allocations, as seen in `src/engine/OdeIntegrator.cpp`'s `hasWordBoundaryMatch` loops.
**Action:** Always precompute lowercased elements, such as function names, in an outer cache rather than repeating the transformation for each nested iteration.
