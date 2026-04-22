## 2024-04-22 - Species Search Optimization
**Learning:** In the BioNetGen C++ core (`BNGcore`), species processing (such as in `ReactionRule::findEmbeddingsForSpecies`) must follow ascending index order to maintain deterministic network generation results. When optimizing lookups against an `unordered_set` of candidate species, copy the indices to a `std::vector` and sort them before iteration to reduce complexity from O(N_species) to O(N_candidates * log(N_candidates)) without breaking determinism.
**Action:** When iterating over a subset of candidates in a large sequential list where the order matters, extract and sort the subset instead of iterating the entire list and checking membership, ensuring O(K log K) instead of O(N).

## 2024-04-22 - Graph Traversal Optimization
**Learning:** In the BioNetGen C++ core (`BNGcore`), when implementing graph traversals or operating on collections (`std::vector`), using `std::find` inside loops (e.g., in `PatternGraph::gather_connected` or `PatternGraph::gather_subtree`) leads to O(N^2) complexity.
**Action:** Replace `std::find` membership checks inside loops with a `std::set` or `std::unordered_set` (e.g., `std::set<Node*> existing(vec.begin(), vec.end())`) to track inclusion efficiently, reducing complexity to O(N log N) or O(N).
