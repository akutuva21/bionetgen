## 2024-05-13 - Optimize compilation word matching
**Learning:** In C++, repeatedly checking for word boundary substring searches (`hasWordBoundaryMatch`) over the same static text inside a nested loop is an O(N * M) bottleneck. Pre-extracting tokens from the text into a `std::vector<std::string_view>` outside the inner loop transforms the operation into an O(M) token iteration, using zero-allocation views.
**Action:** When finding words in strings repeatedly, tokenize into string views once.
