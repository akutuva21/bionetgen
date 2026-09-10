## 2024-05-15 - Case-Insensitive Matching Performance
**Learning:** `std::string` allocations via `std::transform(..., ::tolower)` in tight loops are a massive performance drain. However, standard SIMD acceleration in `std::string::find` makes pre-lowercasing the input string faster than custom iterator-based case-insensitive searching in most cases. Wait, what? Oh, looking for boundaries, it makes a huge difference. Using `std::string` object buffer reusing.
**Action:** When performing case-insensitive matching repeatedly, use an external string buffer that avoids allocating memory on each call, or rely on `std::string_view` where applicable.

## 2024-05-15 - O(N) lookup in resolvers
**Learning:** `OdeIntegrator` defines local `resolver` lambdas in several ODE loop iterations (`integrateEuler`, `integrateRK4`, `integrateCvode`, etc) which use an O(N) search through `compiledGroups_` to resolve group indices by string. When the number of observables is large and these resolvers are called often (like for `stop_if`), it severely limits performance.
**Action:** Since `observableIndex_` is already pre-computed as an `std::unordered_map<std::string, std::size_t>`, these resolvers should use `observableIndex_` for O(1) lookups instead of iterating over `compiledGroups_`.
