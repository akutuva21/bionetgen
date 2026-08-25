## 2024-05-15 - Insecure Temporary File Creation
**Vulnerability:** Predictable temporary files were created in the current working directory, which could lead to race conditions, insecure predictability, and workspace pollution if errors occur.
**Learning:** Hardcoding or using sequential temporary file names is dangerous and can lead to unintended side effects, especially in an RPC server context.
**Prevention:** Use Python's `tempfile` module (e.g. `tempfile.mkdtemp()`) for secure temporary file/directory management, and employ `try...finally` with `shutil.rmtree(..., ignore_errors=True)` to ensure reliable cleanup.
