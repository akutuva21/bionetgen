## 2024-05-14 - Optimize Bipartite Graph mapping intersection
**Learning:** Legacy Python scripts in this codebase (`parsers/BipartiteGraph/bpgMaps.py`) frequently use O(N*M) list comprehensions (e.g., `[x for x,y in map for z in list if y==z]`) to perform graph intersections. For mapping dictionaries and edges, this is terribly inefficient.
**Action:** Replace nested loops with O(1) membership testing by pre-computing a `set` (e.g., `z_set = set(list)` and `[x for x,y in map if y in z_set]`).

## 2024-05-15 - C++ dense index tracking
**Learning:** In the BioNetGen C++ core (`src/ast`), dense integers (like species indexes) are often tracked using `std::map<std::size_t, std::size_t>`. In hot paths, this causes significant $O(\log n)$ lookup overhead.
**Action:** Always replace `std::map` with a flat `std::vector` indexed by the ID when tracking dense states per species, using `static_cast<std::size_t>(-1)` as an uninitialized sentinel value, to turn lookups into $O(1)$.
