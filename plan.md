1. **Remove `std::regex` usage inside loops in `src/ast/MacroBNGModel.cpp`**:
   - The `num_site` function parses reactant and product names by extracting the contents inside parentheses. It dynamically created a `static const std::regex` which has significant overhead when `std::regex_search` and `std::smatch` allocate on the heap. I replaced it with `std::string::find`, `rfind`, and `substr`.
   - The `cor_net` function extracts group names matching `Molecules;name;`. It did this by repeatedly compiling/running `static const std::regex mol_re("Molecules;(.*?);")` inside a loop. I replaced this with manual `std::string::find` logic to slice out the token without regex heap allocations.
2. **Complete pre commit steps**
   - Run `ctest` to ensure C++ tests still pass.
   - We will write a `.jules/bolt.md` to document the performance learnings related to `std::regex` and C++.
3. **Submit the PR**
   - Use `gh pr create` with standard title format and details.
   - Use `submit` to finish the task.
