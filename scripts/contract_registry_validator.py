# contract_registry_validator.py
# Validates L1–L5 contracts defined in contracts.yaml.

import os
import sys
import yaml

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
CONTRACTS_PATH = os.path.join(REPO_ROOT, "contracts.yaml")

REQUIRED_CONTRACT_FIELDS = [
    "version",
    "input_schema",
    "output_schema",
    "error_model",
    "timeout_ms",
]

def load_contracts():
    if not os.path.exists(CONTRACTS_PATH):
        print(f"ERROR: Missing contracts.yaml at: {CONTRACTS_PATH}")
        sys.exit(1)
    with open(CONTRACTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def validate_contract(name, contract, errors):
    for field in REQUIRED_CONTRACT_FIELDS:
        if field not in contract:
            errors.append(f"Contract {name} missing field: {field}")

    # Version must be semver
    ver = contract.get("version", "")
    if not isinstance(ver, str) or not ver.count(".") == 2:
        errors.append(f"Contract {name} version not valid semver: {ver}")

def main():
    contracts = load_contracts()
    errors = []

    for name, contract in contracts.items():
        validate_contract(name, contract, errors)

    if errors:
        print("\n=== CONTRACT VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Contract registry validation PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
