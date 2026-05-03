## 2024-05-13 - [O(N^2) lists to O(1) mappings in BipartiteGraph]
**Learning:** Python operations converting lists to sets dynamically over O(N^2) list comprehensions creates significant bottlenecks when processing large bipartite maps (rules vs patterns vs transformations).
**Action:** Always pre-compute and store O(1) set-based reverse mappings (e.g. `p2t` from `t2p`) directly alongside the original mappings during initialization. Update queries to merge pre-computed lookup set values using `.update()`.
