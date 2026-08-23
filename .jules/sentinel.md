## 2024-05-24 - [Predictable Temp Files / Race Condition in XML-RPC server]
**Vulnerability:** The ContactMap `server.py` script used `iid` counting to sequentially assign temp file names (e.g., `temp1.bngl`, `temp1.xml`), and blindly cleaned them up via `glob.glob` and `os.remove`. This enables symlink attacks, data leakage if temp file sequence is predicted, and a race condition when executing parallel requests or other concurrent file removals.
**Learning:** Hardcoded counting temp file naming is vulnerable and fragile in multi-threaded network environments.
**Prevention:** Use Python's `tempfile` module (e.g., `tempfile.mkdtemp()`) to securely create temporary directories with random, collision-free names, and properly clean up using `shutil.rmtree()` within a `try...finally` block.
