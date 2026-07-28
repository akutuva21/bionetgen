## 2024-05-30 - Fix 2-argument open() vulnerabilities
**Vulnerability:** Found multiple instances of the 2-argument `open()` function in Perl scripts (`MacroBNGModel.pm`, `BNGAction.pm`, etc.), which are vulnerable to file path and command injection.
**Learning:** Legacy Perl code often uses `open(FH, $file)` which evaluates magic characters like `>|` or `|` causing unintended consequences.
**Prevention:** Always use the secure 3-argument `open()` function: `open(FH, '<', $file)` or `open(FH, '>', $file)` for reading and writing files.
