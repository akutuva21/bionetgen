## 2024-08-18 - [Insecure Temporary File Management]
**Vulnerability:** Predictable temporary file names with global pattern deletion (`glob.glob`) in `parsers/ContactMap/server.py` and `parsers/BipartiteGraph/server.py`.
**Learning:** Sequential naming and global deletion of temp files creates race conditions in concurrent access and makes the application vulnerable to symlink attacks or arbitrary file deletion.
**Prevention:** Use `tempfile.mkdtemp()` to create isolated directories for temporary processing and `shutil.rmtree` in a `finally` block to ensure cleanup.
