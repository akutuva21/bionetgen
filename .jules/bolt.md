## 2024-05-18 - Replacing nested loop with map lookups in parsers/BipartiteGraph
**Learning:** Found an O(N) array lookup with loop generator expressions used heavily in bpgMaps.py and bipartiteGraph.py.
**Action:** Replaced linear scans with pre-computed hash maps (O(1)) reducing complexity significantly when rendering large graphs.
