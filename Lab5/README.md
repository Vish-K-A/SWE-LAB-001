# Lab 5: Static Code Analysis - Hospital Patient System

A Python teaching demo for patient admission, discharge, treatment calculations,
identifier hashing, ward tokens and ledger export. Records are held in memory.

## Setup and run (Windows)

Python 3.10 or newer must be available on PATH. From the project folder:

```bat
system.bat
run.bat
```

`system.bat` reuses the existing `venv` or creates it, then installs the pinned
analysis dependencies in `requirements.txt`. `run.bat` uses that environment
without requiring activation. The demo requires no interactive input.
It writes an ignored `patient_records.txt` ledger in the project folder.

For other platforms, the equivalent commands are:

```sh
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python hospital_patient_system.py
```

## Analysis and tests

Run from the project folder on Windows:

```bat
venv\Scripts\python.exe -m pylint --persistent=n hospital_patient_system.py > pylint_report.txt
venv\Scripts\python.exe -m bandit -r hospital_patient_system.py -f txt > bandit_report.txt
venv\Scripts\python.exe -m flake8 hospital_patient_system.py > flake8_report.txt
venv\Scripts\python.exe -m unittest -v
```

The saved baseline reports are in `reports/before/`; final reports are at the
repository root. Final results: Pylint 10.00/10, Bandit zero findings and Flake8
zero findings. The empty Flake8 report is intentional. Six regression tests
exercise normal operations and unsafe-input boundaries.

## Deliverables

- `hospital_patient_system.py`: cleaned implementation.
- `issues.md`: prioritized findings, original line numbers and fixes.
- `reflection.md`: four reflection answers with a note about missing prompts.
- `reports/before/*_report.txt`: reports against the original `51ec8b0` script.
- `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`: final reports.
- `test_hospital_patient_system.py`: regression checks using standard unittest.
- `requirements.txt`, `system.bat`, `run.bat`: reproducible setup and execution.

Treatment formulas permit numbers, `base_bill`, parentheses, unary signs and
`+ - * /`, with a 256-character limit. Calls, attributes and other syntax are
rejected. Missing patients raise `KeyError` for billing and return `False` for
admission-status/discharge queries. Treatment totals must be finite and
non-negative, and are rounded to two decimals.

This is an in-memory lab exercise. Plaintext ledgers, predictable identifier
hashes and four-digit demo tokens are not a production patient-data or
authentication design. No real patient data is included.
