
## 2024-05-18 - Optimized Bipartite Graph Maps and Structures
**Learning:** In the BioNetGen Python parsers (`parsers/BipartiteGraph/bpgMaps.py` and `structures.py`), performance bottlenecks were found due to multiple `O(N)` list scans inside hot loops (`getFlow`, `getFlux`, `addComponent`, `getTraces`), scaling terribly as `O(N*M)` nested lookups or list comprehensions.
**Action:** Always pre-group repeated relation checks into Python dictionaries (`O(1)` access time). Also, substitute repeated Python list `in` membership checks with `set` objects, and prefer direct attribute accesses (e.g. `.name`) over method calls (e.g. `.getName()`) inside inner loops to avoid call stack overhead.
