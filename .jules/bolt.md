## 2024-08-21 - [Optimize rate law string processing in OdeIntegrator]
**Learning:** In C++, dynamically lowercasing rate law strings (`std::transform` with `std::tolower`) for case-insensitive matching was being performed twice per non-functional reaction due to duplicated logic inside two separate `if` blocks checking `crxn.isFunctional` and `rateExpr.has_value()`.
**Action:** Lazily initialize and cache the lowercased rate law string (`lowerRawRL`) into a single variable at the top of the per-reaction compilation loop so that `std::transform` is run at most once per reaction.
