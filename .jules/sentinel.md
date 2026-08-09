## 2024-05-31 - Insecure Temporary File Management
**Vulnerability:** Predictable temporary file naming and manual deletion using `os.remove` and `glob.glob` inside `parsers/ContactMap/server.py`.
**Learning:** Sequential naming and wildcard deletion introduces race conditions, can accidentally delete unintended files, and makes files predictable which can be used in attacks.
**Prevention:** Use the `tempfile` module (e.g., `tempfile.mkdtemp()`) for secure temporary file/directory management and ensure cleanup using `shutil.rmtree` within a `try...finally` block.
