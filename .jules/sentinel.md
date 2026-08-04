## 2024-05-24 - Validate subprocess.call filename inputs
**Vulnerability:** Subprocess calls in dynamically exposed methods, while using `shell=False`, can still be risky if the input file names aren't strictly verified (path traversal, weird chars passed to the underlying tool, argument injection).
**Learning:** Always validate internal filenames before passing them to subprocesses.
**Prevention:** Add a strict whitelist check on filenames before `subprocess.call` or `Popen`, even when the filename isn't directly user-controllable (defense in depth).
