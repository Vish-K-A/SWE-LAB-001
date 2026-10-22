# Reflection

The README requests four reflection answers, but the supplied three-page lab
handout does not include the question text. The four prompts below are derived
from its learning objectives; they are not quoted handout questions.

## 1. What did each static analysis tool contribute?

Pylint highlighted maintainability problems such as the shared default list,
unused variables, missing docstrings and shadowed names. Flake8 identified
formatting and basic coding errors, including long lines and a bare exception
handler. Bandit prioritized security issues: shell execution and MD5 were high
severity, `eval` was medium, and weak randomness and silent exception handling
were low. Their overlap helped confirm issues, while their different focuses
gave a broader review than any single tool.

## 2. Which fixes mattered most, and why?

The highest priority was removing shell execution and arbitrary evaluation.
The ledger only needs to print a message, so starting a shell served no purpose.
Treatment formulas do need arithmetic on `base_bill`, so replacing `eval` with
`literal_eval` would not preserve the example. An allowlisted AST interpreter
retains that arithmetic while rejecting function calls and attribute access.
SHA-256 and secure token generation resolve the remaining primitive warnings.
The mutable default and silent discharge failure also needed attention because
they could produce unexpected behavior even when normal demo output looked fine.

## 3. How were the fixes verified?

Reports were captured before editing and regenerated with the same tool versions
after editing. Pylint improved from 5.19 to 10.00, Bandit went from five findings
to zero, and Flake8 went from eleven findings to zero without suppressions.
Unit tests check the normal workflow and failure boundaries, including duplicate
admission, unknown patients, malicious formulas and literal export filenames.
The demo still reports two active admissions and a treatment cost of 1344.0.

## 4. What are the limits of static analysis and the remaining limitations?

A clean report is evidence of improvement, not proof of correctness or security.
Running the original program exposed its printed credential and awkward
floating-point output; inspection also revealed import-time side effects.
Behavioral tests are needed alongside the tools. This is still an in-memory
teaching program: records are not stored in a database, the ledger is plaintext,
patient-ID hashes are predictable, and four-digit tokens are not an authentication
system. Monetary calculations still use floats, rounded for the example; a real
billing system would need a defined decimal and currency policy.
