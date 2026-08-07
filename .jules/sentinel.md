## 2024-05-18 - [Insecure Temporary File Management]
**Vulnerability:** Predictable filename generation for temporary files using sequential IDs without isolating temp files to specific directories can lead to race conditions and file collisions.
**Learning:** Sequential IDs (e.g. `temp1.bngl`) can easily be guessed and collide, especially in concurrent requests or if cleanup fails. Relying on `glob.glob` deletion in the current working directory without directory isolation is risky.
**Prevention:** Always use the `tempfile` module (e.g. `tempfile.mkdtemp()`) for secure temporary file generation and handle cleanup using `shutil.rmtree` within a `try...finally` block to guarantee removal even on exceptions.
