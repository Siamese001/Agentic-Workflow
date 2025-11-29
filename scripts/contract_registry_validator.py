#!/usr/bin/env python3
"""
contract_registry_validator.py
Validates contracts.yaml for planners, executors, tools, etc.

Covers:
- Required fields present
- Valid semver version
- Referenced schemas exist on disk
- Timeout required and > 0
"""

import os
import sys
import yaml

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
CONTRACTS_PATH = os.path.join(REPO_ROOT, "contracts.yaml")

REQUIRED_FIELDS = [
    "version",
    "input_schema",
    "output_schema",
    "error_model",
    "timeout_ms",
]


def is_semver(v: str) -> bool:
    if not isinstance(v, str):
        return False
    parts = v.split(".")
    return len(parts) == 3 and all(p.isdigit() for p in parts)


def load_contracts():
    if not os.path.exists(CONTRACTS_PATH):
        print(f"[CONTRACTS] Missing contracts.yaml at {CONTRACTS_PATH}")
        sys.exit(1)
    with open(CONTRACTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    contracts = load_contracts()
    errors = []

    for name, contract in contracts.items():
        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in contract:
                errors.append(f"[CONTRACT] {name} missing required field: {field}")

        # Semver
        ver = contract.get("version")
        if not is_semver(ver):
            errors.append(f"[CONTRACT] {name} invalid semver version: {ver}")

        # Timeout > 0
        timeout = contract.get("timeout_ms")
        if not isinstance(timeout, int) or timeout <= 0:
            errors.append(f"[CONTRACT] {name} timeout_ms must be positive int, got: {timeout}")

        # Schema files exist
        for schema_field in ("input_schema", "output_schema", "error_model"):
            schema_path = contract.get(schema_field)
            if isinstance(schema_path, str):
                full = os.path.join(REPO_ROOT, schema_path).replace("\\", "/")
                if not os.path.exists(full):
                    errors.append(f"[CONTRACT] {name} {schema_field} missing file: {schema_path}")

    if errors:
        print("\n=== CONTRACT REGISTRY VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Contract registry validation PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()

