## 2024-05-24 - File Injection Vulnerability
**Vulnerability:** 2-argument `open()` used for dynamic files without specifying mode explicitly, allowing file manipulation.
**Learning:** `open()` can be manipulated if it takes dynamic arguments without mode specification.
**Prevention:** Always use 3-argument `open()` like `open(FH, '<', $file)`.
