## 2024-10-24 - [Insecure Temporary File Management]
**Vulnerability:** The XML-RPC server used predictable, sequentially named files in the current working directory for processing BNGL data. This could lead to a race condition or allow an attacker to read/write temporary files.
**Learning:** Sequential/predictable filenames using `open('temp{0}.bngl')` create race conditions when concurrent requests are handled, and scattering them in the current directory increases exposure.
**Prevention:** Use `tempfile.mkdtemp()` to create a dedicated, randomly-named temporary directory for each request, process the files inside it, and clean it up reliably using `shutil.rmtree` inside a `try...finally` block.
