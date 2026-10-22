# Identified issues and fixes

Line numbers refer to the original script in commit `51ec8b0`, also preserved
in `reports/before/`. Bandit severity is used where available; other priorities
are manual assessments. No analyzer warnings were suppressed.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell execution (B605, high) | Security | 56 | A filename is concatenated into a shell command, allowing command injection. | Replace `os.system` with `print`; filenames are only passed to file I/O. |
| MD5 (B324, high) | Security | 45 | MD5 is unsuitable for security-sensitive identifier hashing. | Use SHA-256; document that predictable patient IDs are not anonymized by hashing. |
| `eval` (B307, medium; W0123) | Security | 40 | Formula strings can execute arbitrary Python. | Interpret a bounded AST allowing numbers, `base_bill`, parentheses, unary signs and `+ - * /` only. Reject calls, attributes and other syntax. |
| Hardcoded printed access key (manual, medium) | Security | 68, 77 | A demo master key is embedded in source and printed. | Remove the unused credential and output; this demo does not implement authentication. |
| Mutable default (W0102, manual medium) | Bug | 13 | The same intake log list is reused by independent calls. | Default to `None`, allocate a new list per call, and retain caller-supplied lists. |
| Swallowed exceptions (B110, low; W0702; E722) | Bug | 22-25 | A bare handler hides missing patients and unexpected failures. | Check membership explicitly and return a success boolean; do not swallow other errors. |
| Insecure randomness (B311, low) | Security | 49 | General-purpose randomness generates a ward token. | Use `secrets.randbelow`, retaining the 1000-9999 range. A four-digit token is a demo value, not standalone authentication. |
| Manual file cleanup (R1732, W1514) | Reliability | 53-55 | Exceptions can leave the file open; encoding is platform-dependent. | Use a context manager and explicit UTF-8 encoding. |
| Dead code and redundant conditions (W0611, W0612, C0121, R1703, R1705, E711) | Maintainability | 4, 29-35, 39, 61 | Unused imports/variables and verbose admission checks obscure intent. | Remove unused code, use explicit record lookup, and count admitted records directly. |
| Naming, shadowing and missing docs (C0103, W0621, C0114, C0116, C0209) | Maintainability | 1, 13-67 | Naming, undocumented behavior and shadowing make the API harder to follow. | Rename to `admit_patient`, update the caller, add docstrings, use f-strings and rename the summary parameter. |
| Formatting (E501, W292, C0304) | Style | 7-9, 16, 72, 80 | Long lines and a missing final newline violate style rules. | Wrap long statements and add the final newline. |
| Import executes demo (manual) | Bug | 80 | Importing the module changes records, writes a ledger and prints output. | Add a `__main__` guard, enabling isolated tests and safe imports. |
| Floating-point display (manual) | Output | 72 | The example prints `1344.0000000000002`. | Round the treatment total to two decimal places and reject negative/nonfinite totals. This remains a float-based teaching demo. |

## Verification

| Tool | Before | After |
|------|--------|-------|
| Pylint 4.1.3 | 5.19/10 | 10.00/10 |
| Bandit 1.9.4 | 5 findings: 2 high, 1 medium, 2 low | 0 findings |
| Flake8 7.4.1 | 11 findings | 0 findings |

Original reports are under `reports/before/`. Final reports are the three
`*_report.txt` files at the repository root. An empty Flake8 report means no
findings. Regression tests exercise admission, discharge, billing, malicious
formulas, hashing, token range, ledger contents and import behavior.
