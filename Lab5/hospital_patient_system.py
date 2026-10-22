"""Manage demo hospital admissions, treatment formulas and ledger exports."""

import ast
import hashlib
import math
import operator
import secrets

patient_records = {
    "P101": {
        "name": "John Doe", "ward": "ICU",
        "is_admitted": True, "bill": 2400.0,
    },
    "P102": {
        "name": "Jane Smith", "ward": "General",
        "is_admitted": False, "bill": 450.0,
    },
    "P103": {
        "name": "Robert Brown", "ward": "Private",
        "is_admitted": True, "bill": 1200.0,
    },
}


def admit_patient(p_id, name, ward, intake_log=None):
    """Admit a new patient and optionally append to the caller's log."""
    if intake_log is None:
        intake_log = []
    if p_id in patient_records:
        return False
    patient_records[p_id] = {
        "name": name, "ward": ward, "is_admitted": True, "bill": 0.0,
    }
    intake_log.append(f"Admitted patient {p_id} into ward {ward}")
    return True


def discharge_patient(p_id):
    """Discharge a known patient; return False for an unknown ID."""
    if p_id not in patient_records:
        return False
    patient_records[p_id]["is_admitted"] = False
    return True


def verify_admission_status(p_id):
    """Return whether the patient exists and is currently admitted."""
    record = patient_records.get(p_id)
    return record is not None and record["is_admitted"]


def calculate_treatment_cost(p_id, formula_expr):
    """Evaluate bounded arithmetic on base_bill and round to two decimals.

    Unknown IDs raise KeyError; invalid formulas raise ValueError.
    Division by zero raises ZeroDivisionError.
    """
    if len(formula_expr) > 256:
        raise ValueError("Formula is too long")
    try:
        expression = ast.parse(formula_expr, mode="eval")
    except (SyntaxError, RecursionError) as error:
        raise ValueError("Invalid treatment formula") from error
    total = _evaluate_formula(expression.body, patient_records[p_id]["bill"])
    if not math.isfinite(total) or total < 0:
        raise ValueError("Treatment cost must be finite and non-negative")
    return round(total, 2)


def _evaluate_formula(node, base_bill):
    """Interpret only numeric literals, base_bill and arithmetic AST nodes."""
    operations = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
    }
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_bill":
        return base_bill
    if (isinstance(node, ast.UnaryOp)
            and isinstance(node.op, (ast.UAdd, ast.USub))):
        value = _evaluate_formula(node.operand, base_bill)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in operations:
        return operations[type(node.op)](
            _evaluate_formula(node.left, base_bill),
            _evaluate_formula(node.right, base_bill),
        )
    raise ValueError("Only base_bill, numbers, +, -, *, / are allowed")


def generate_patient_hash(p_id):
    """Return an identifier digest; this does not anonymize patient IDs."""
    return hashlib.sha256(p_id.encode("utf-8")).hexdigest()


def generate_ward_token():
    """Generate a four-digit demo token using secure randomness."""
    return secrets.randbelow(9000) + 1000


def export_patient_ledger(filename="patient_records.txt"):
    """Write a UTF-8 ledger and report its path without invoking a shell."""
    with open(filename, "w", encoding="utf-8") as ledger:
        ledger.write(str(patient_records))
    print(f"Patient ledger exported to: {filename}")


def get_ward_summary(records):
    """Count admitted patients in the supplied records."""
    return sum(1 for details in records.values() if details["is_admitted"])


def main():
    """Run the sample admission, discharge, billing and export workflow."""
    admit_patient("P104", "Alice Walker", "General")
    discharge_patient("P101")
    print("Is P103 admitted:", verify_admission_status("P103"))
    cost = calculate_treatment_cost("P103", "base_bill * 1.12")
    print("Cost calculated:", cost)
    print("Patient Hash:", generate_patient_hash("P103"))
    print("Ward Token:", generate_ward_token())
    export_patient_ledger()
    print("Active admits:", get_ward_summary(patient_records))


if __name__ == "__main__":
    main()
