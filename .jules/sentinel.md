## 2025-02-14 - Predictable Temporary Files & Race Conditions
**Vulnerability:** Insecure file handling in `parsers/ContactMap/server.py` using sequential predictability (`temp{counter}.bngl`) and `glob` for deletion, stored in the current working directory.
**Learning:** Hardcoded temporary files in working directories introduce predictable filename vulnerabilities and race conditions across concurrent XML-RPC requests.
**Prevention:** Use `tempfile.mkdtemp()` to generate unique, secure temporary directories and ensure robust cleanup with `shutil.rmtree` inside a `try...finally` block.
