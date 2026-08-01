## 2025-05-18 - Fix insecure temporary file usage
**Vulnerability:** Use of predictable temporary files (`temp{0}.bngl`) in the current working directory combined with manual global counters and file deletion.
**Learning:** Manual temporary file handling leaves artifacts on crash, introduces race conditions, and is vulnerable to symlink attacks.
**Prevention:** Use Python's `tempfile.TemporaryDirectory()` to securely create and clean up isolated temporary environments.
