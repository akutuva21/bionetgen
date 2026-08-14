## 2024-08-14 - Fix Insecure Temporary File Generation
**Vulnerability:** Predictable temporary file generation using sequential counter in `parsers/ContactMap/server.py` and insecure cleanup via globbing and `os.remove`.
**Learning:** Sequential naming allows an attacker to guess the temp file name, leading to potential race conditions or symlink attacks. Using glob for deletion could accidentally remove untargeted files matching the pattern.
**Prevention:** Always use `tempfile.mkdtemp()` or `tempfile.NamedTemporaryFile` for generating secure temporary paths. Rely on `shutil.rmtree` within a `try...finally` block to guarantee safe directory deletion.
