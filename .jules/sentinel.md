## 2024-05-24 - File Path Command Injection in Perl
**Vulnerability:** 2-argument `open()` calls in Perl (e.g. `open(FH, ">$file")`) are vulnerable to command injection if the file path is attacker-controlled, as paths starting or ending with a pipe `|` will execute a shell command.
**Learning:** Legacy Perl scripts often use 2-argument `open()`, which dynamically interpolates variables into the mode/path string, exposing a critical injection surface.
**Prevention:** Always use the 3-argument `open()` (e.g. `open(FH, ">", $file)`) to strictly separate the file open mode from the file path string, ensuring the path is never interpreted as a command.
