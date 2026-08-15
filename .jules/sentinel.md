## 2024-05-24 - [Initial Sentinel Setup]
**Vulnerability:** None
**Learning:** Initial setup for Sentinel.
**Prevention:** None
## 2024-08-15 - [Predictable Temporary File Names in ContactMap Server]
**Vulnerability:** The ContactMap XMLRPC server used predictably named temporary files (`temp{counter}.bngl`) in the current working directory, creating a race condition and a risk of file content manipulation.
**Learning:** Tools like `bngdev` generate output files in the same directory as their input. Temporary file management in server environments must avoid shared state or predictable filenames.
**Prevention:** Use `tempfile.mkdtemp()` to create a dedicated, secure temporary directory for each request, and ensure cleanup using `shutil.rmtree` within a `try...finally` block.
