import hashlib
import ast
import operator
import secrets
import math

patient_records = {
    "P101": {"name": "John Doe", "ward": "ICU", "is_admitted": True, "bill": 2400.0},
    "P102": {"name": "Jane Smith", "ward": "General", "is_admitted": False, "bill": 450.0},
    "P103": {"name": "Robert Brown", "ward": "Private", "is_admitted": True, "bill": 1200.0},
}


def admitPatient(p_id, name, ward, intake_log=[]):
    if p_id in patient_records:
        return False
    patient_records[p_id] = {"name": name, "ward": ward, "is_admitted": True, "bill": 0.0}
    intake_log.append("Admitted patient %s into ward %s" % (p_id, ward))
    return True


def discharge_patient(p_id):
    if p_id not in patient_records:
        return False
    patient_records[p_id]["is_admitted"] = False
    return True


def verify_admission_status(p_id):
    bed_charge = 75.0
    if patient_records.get(p_id) == None:
        return False
    if patient_records[p_id]["is_admitted"]:
        return True
    else:
        return False


def calculate_treatment_cost(p_id, formula_expr):
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
    operations = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
    }
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_bill":
        return base_bill
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_formula(node.operand, base_bill)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in operations:
        return operations[type(node.op)](
            _evaluate_formula(node.left, base_bill),
            _evaluate_formula(node.right, base_bill),
        )
    raise ValueError("Only base_bill, numbers, +, -, *, / are allowed")


def generate_patient_hash(p_id):
    return hashlib.sha256(p_id.encode("utf-8")).hexdigest()


def generate_ward_token():
    return secrets.randbelow(9000) + 1000


def export_patient_ledger(filename="patient_records.txt"):
    f = open(filename, "w")
    f.write(str(patient_records))
    f.close()
    print(f"Patient ledger exported to: {filename}")


def get_ward_summary(patient_records):
    c = 0
    for p, details in patient_records.items():
        if details["is_admitted"]:
            c += 1
    return c


def main():
    admitPatient("P104", "Alice Walker", "General")
    discharge_patient("P101")
    print("Is P103 admitted:", verify_admission_status("P103"))
    print("Cost calculated:", calculate_treatment_cost("P103", "base_bill * 1.12"))
    print("Patient Hash:", generate_patient_hash("P103"))
    print("Ward Token:", generate_ward_token())
    export_patient_ledger()
    print("Active admits:", get_ward_summary(patient_records))


main()