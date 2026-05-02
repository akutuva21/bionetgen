## 2024-05-02 - Flat vector tracking for iteration state
**Learning:** `ReactionRule::findEmbeddingsForSpecies` uses an unordered set for already searched species. `lastProcessedInIteration_` tracking logic scales by maximum `speciesIndex`.
**Action:** Use an explicit linear vector `std::vector<bool>` or flat index check to avoid O(N^2) behavior inside loop instead of iterating the entire matches.
