"""Regression tests for patient operations and unsafe-input boundaries."""

import ast
import contextlib
import copy
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import hospital_patient_system as hospital


class HospitalTests(unittest.TestCase):
    """Restore the demo records after each test."""

    def setUp(self):
        self.original = copy.deepcopy(hospital.patient_records)

    def tearDown(self):
        hospital.patient_records.clear()
        hospital.patient_records.update(self.original)

    def test_admissions_and_caller_logs(self):
        """Duplicate admission preserves records and does not append logs."""
        log = []
        self.assertTrue(hospital.admit_patient("P200", "Alice", "ICU", log))
        self.assertFalse(hospital.admit_patient("P200", "Other", "ICU", log))
        self.assertEqual(len(log), 1)
        self.assertEqual(hospital.patient_records["P200"]["name"], "Alice")
        self.assertIsNone(hospital.admit_patient.__defaults__[0])
        self.assertTrue(hospital.admit_patient("P201", "Bob", "General"))
        self.assertTrue(hospital.admit_patient("P202", "Carol", "Private"))

    def test_discharge_status_and_summary(self):
        """Unknown IDs return False and discharges update the count."""
        self.assertEqual(hospital.get_ward_summary(hospital.patient_records), 2)
        self.assertTrue(hospital.discharge_patient("P101"))
        self.assertFalse(hospital.verify_admission_status("P101"))
        self.assertFalse(hospital.discharge_patient("missing"))
        self.assertFalse(hospital.verify_admission_status("missing"))
        self.assertEqual(hospital.get_ward_summary(hospital.patient_records), 1)

    def test_treatment_arithmetic(self):
        """Retain formulas, parentheses and unary arithmetic without eval."""
        self.assertEqual(
            hospital.calculate_treatment_cost("P103", "base_bill * 1.12"),
            1344.0,
        )
        self.assertEqual(
            hospital.calculate_treatment_cost("P103", "(+base_bill - 200)/2"),
            500.0,
        )
        with self.assertRaises(ZeroDivisionError):
            hospital.calculate_treatment_cost("P103", "base_bill / 0")
        with self.assertRaises(KeyError):
            hospital.calculate_treatment_cost("missing", "base_bill")

    def test_unsafe_and_invalid_formulas(self):
        """Reject execution, attribute access, nonnumbers and invalid bills."""
        formulas = [
            "__import__('os').getcwd()", "base_bill.__class__", "[1][0]",
            "unknown + 1", "True", "'text'", "2 ** 100", "1e309",
            "-base_bill", "base_bill +", "1" * 257,
        ]
        for formula in formulas:
            with self.subTest(formula=formula), self.assertRaises(ValueError):
                hospital.calculate_treatment_cost("P103", formula)

    def test_hash_and_token(self):
        """Hashes are deterministic SHA-256 digests; tokens stay four digits."""
        digest = hospital.generate_patient_hash("P103")
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, hospital.generate_patient_hash("P103"))
        self.assertNotEqual(digest, hospital.generate_patient_hash("P102"))
        for _ in range(100):
            self.assertIn(hospital.generate_ward_token(), range(1000, 10000))

    def test_ledger_and_import_side_effects(self):
        """Treat shell metacharacters literally; importing creates no ledger."""
        with tempfile.TemporaryDirectory(
                dir=Path(__file__).resolve().parent) as directory:
            target = Path(directory) / "ledger & echo injected.txt"
            with contextlib.redirect_stdout(io.StringIO()):
                hospital.export_patient_ledger(target)
            self.assertEqual(
                ast.literal_eval(target.read_text(encoding="utf-8")),
                hospital.patient_records,
            )
            module_dir = str(Path(hospital.__file__).resolve().parent)
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {module_dir!r}); "
                 "import hospital_patient_system"],
                cwd=directory, capture_output=True, text=True, check=True,
            )
            self.assertEqual(result.stdout, "")
            self.assertFalse((Path(directory) / "patient_records.txt").exists())


if __name__ == "__main__":
    unittest.main()
