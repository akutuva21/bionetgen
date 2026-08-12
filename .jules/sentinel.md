## 2024-05-24 - [Insecure Temporary File Management]
**Vulnerability:** In `parsers/ContactMap/server.py`, temporary files are created with predictable sequential names (`temp{counter}.bngl`) in the current working directory, and cleaned up using `glob.glob` and sequential `os.remove`.
**Learning:** This approach causes race conditions and insecure predictable filenames, making it vulnerable to symlink attacks, data leakage, and conflicts between concurrent requests.
**Prevention:** Use the `tempfile` module (e.g., `tempfile.mkdtemp()`) for temporary file management and ensure cleanup using `shutil.rmtree` within a `try...finally` block to prevent leftover artifacts.
