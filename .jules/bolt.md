## 2024-05-18 - Replacing O(N) list comprehensions with O(1) generator expression extraction
**Learning:** Legacy Python code often uses `[x for x in list if condition][0]` to extract a single element, which builds a full new list in memory and processes every element needlessly (O(N) time and memory).
**Action:** Replace this pattern with `next((x for x in list if condition), None)`. This evaluates lazily, immediately exiting the loop when the first match is found (best case O(1)), improving both memory efficiency and CPU cycles.
