## 2024-08-08 - Insecure predictable temporary files in XML-RPC server
**Vulnerability:** The XML-RPC server was generating temporary files using sequential predictable names (e.g. `temp{0}.bngl`) and cleaning them up via `glob.glob()`. This introduced race conditions and the risk of file overwriting or deletion.
**Learning:** This implementation lacked isolation for requests and assumed a dedicated execution space, leading to a medium severity risk of state pollution and file corruption under concurrent loads.
**Prevention:** Always use `tempfile.mkdtemp()` to provide isolated temporary directories for concurrent handling tasks, ensuring cleanup is performed safely within a `try...finally` block utilizing `shutil.rmtree(temp_dir, ignore_errors=True)`.
