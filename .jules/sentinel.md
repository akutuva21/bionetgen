## 2024-05-24 - Secure Temporary File Handling in BipartiteServer
**Vulnerability:** The XML-RPC server (`parsers/ContactMap/server.py`) stored temporary files with predictable sequential names (`temp{counter}.*`) directly in the current working directory, using a simple glob and `os.remove` to clean up.
**Learning:** This is a classic insecure temporary file pattern, exposing the system to race conditions, naming collisions in concurrent requests, and incomplete cleanup on crashes.
**Prevention:** Always use the `tempfile` module (e.g. `tempfile.mkdtemp()`) for creating secure temporary directories and files, avoiding predictable names, and ensuring cleanup inside a `finally` block using `shutil.rmtree`.
