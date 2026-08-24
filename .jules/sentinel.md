## 2024-05-24 - [Fix Predictable Temporary Files]
**Vulnerability:** The ContactMap server used predictable sequential filenames (`temp{0}.bngl`) and global wildcard deletion (`glob.glob('temp{0}*')`) in the current working directory, which created race conditions and potential security risks (overwriting or leaking files).
**Learning:** Legacy Python scripts sometimes implement custom counters and predictable filenames instead of using the standard `tempfile` module. This is especially risky in XML-RPC servers processing multiple concurrent requests.
**Prevention:** Always use the `tempfile` module (e.g., `tempfile.mkdtemp()` or `tempfile.NamedTemporaryFile`) for managing temporary files securely and avoid scattering temporary files in the current working directory.
