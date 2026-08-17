## 2024-05-15 - [Fix Predictable Temporary Filename Vulnerability]
**Vulnerability:** The XML-RPC server used predictable file names (temp{counter}.bngl) in the current working directory for processing files, which could lead to race conditions or unauthorized file access.
**Learning:** Hardcoded, sequentially generated file names inside public servers open up a large attack surface where attackers can intercept, read or spoof processed contents.
**Prevention:** Always use dedicated temporary directory managers like `tempfile.mkdtemp()` when handling multiple interdependent generated artifacts securely.
