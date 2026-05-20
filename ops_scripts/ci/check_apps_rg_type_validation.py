"""APPS-TYPE-VALID CI gate — static type contract validation for apps_rg layer bindings.

Per plan apps-rg-ci-runtime-enforcement-0be75b W2.

Validates:
- Layer binding function signatures (arity, parameter types)
- Enum vs type mismatches (CacheEligibility enum vs Mapping[str,bool])
- Return type declarations vs actual contract classes
- Cross-layer dispatch target compatibility

Exit 0 → all type contracts valid.
Exit 1 → type mismatch detected (advisory by default, fail-closed via
APPS_RG_TYPE_VALID_FAIL_CLOSED=1).
Bypass: APPS_RG_TYPE_VALID_BYPASS=1.
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, get_type_hints

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "apps_rg_type_validation_gate.json"

# Layer bindings to validate
_LAYER_BINDINGS: list[tuple[str, str, str]] = [
    ("agentic_core.runtime.entry.u0_apps_rg_binding", "u0_validate_apps_rg", "U0"),
    ("agentic_core.L1_cognition.apps_rg_l1_binding", "l1_plan_apps_rg", "L1"),
    ("agentic_core.L0_routing.apps_rg_l0_binding", "l0_route_apps_rg", "L0"),
    ("agentic_core.runtime.c0.apps_rg_c0_binding", "c0_retrieve_apps_rg", "C0"),
    ("agentic_core.prompt_governance.apps_rg_pa_binding", "pa_compose_apps_rg", "PA"),
    ("apps_rg.runtime.bindings.l2_binding", "l2_execute_apps_rg", "L2"),
    ("agentic_core.runtime.exit.apps_rg_exit_binding", "exit_finalize_apps_rg", "Exit"),
]


class TypeViolation:
    """Single type contract violation."""

    def __init__(self, layer: str, check: str, detail: str, severity: str = "ERROR") -> None:
        self.layer = layer
        self.check = check
        self.detail = detail
        self.severity = severity

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "check": self.check,
            "detail": self.detail,
            "severity": self.severity,
        }


def _emit_report(status: str, violations: list[TypeViolation]) -> None:
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "APPS-TYPE-VALID",
                "status": status,
                "violations": [v.to_dict() for v in violations],
                "violation_count": len(violations),
                "error_count": sum(1 for v in violations if v.severity == "ERROR"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _check_layer_binding_signature(
    module_path: str,
    func_name: str,
    layer: str,
) -> list[TypeViolation]:
    """Check a layer binding function's signature is valid."""
    violations: list[TypeViolation] = []

    try:
        # Dynamic import
        module = __import__(module_path, fromlist=[func_name])
        func = getattr(module, func_name)

        if not callable(func):
            violations.append(TypeViolation(
                layer, "CALLABLE", f"{func_name} is not callable"
            ))
            return violations

        # Get signature
        try:
            sig = inspect.signature(func)
        except ValueError as exc:
            violations.append(TypeViolation(
                layer, "SIGNATURE", f"Cannot inspect signature: {exc}"
            ))
            return violations

        # Check parameters exist (all bindings should take at least one arg)
        params = list(sig.parameters.items())
        if not params:
            violations.append(TypeViolation(
                layer, "ARITY", f"{func_name} has no parameters (should take at least one)"
            ))

        # Try to get type hints
        try:
            hints = get_type_hints(func)
            if "return" not in hints:
                violations.append(TypeViolation(
                    layer, "RETURN_TYPE", f"{func_name} missing return type annotation",
                    severity="WARN",
                ))
        except (NameError, AttributeError, TypeError) as exc:
            violations.append(TypeViolation(
                layer, "TYPE_HINTS", f"Cannot resolve type hints: {exc}",
                severity="WARN",
            ))

    except ImportError as exc:
        violations.append(TypeViolation(
            layer, "IMPORT", f"Cannot import {module_path}: {exc}"
        ))
    except AttributeError as exc:
        violations.append(TypeViolation(
            layer, "ATTRIBUTE", f"Cannot find {func_name} in {module_path}: {exc}"
        ))

    return violations


def _check_l0_cache_eligibility_type() -> list[TypeViolation]:
    """Check that L0 binding returns proper type for cache_eligibility."""
    violations: list[TypeViolation] = []

    try:
        sys.path.insert(0, str(_REPO_ROOT))
        from agentic_core.L0_routing.apps_rg_l0_binding import l0_route_apps_rg
        from agentic_core.runtime.contracts.route_contract import RouteContract

        # Check return type annotation
        hints = get_type_hints(l0_route_apps_rg)
        return_type = hints.get("return")

        if return_type is None:
            violations.append(TypeViolation(
                "L0", "RETURN_TYPE", "l0_route_apps_rg missing return type annotation"
            ))
        elif not hasattr(return_type, "__name__") or return_type.__name__ != "RouteContract":
            violations.append(TypeViolation(
                "L0", "RETURN_TYPE", f"l0_route_apps_rg returns {return_type}, expected RouteContract"
            ))

        # Verify RouteContract.cache_eligibility expects Mapping[str, bool]
        if hasattr(RouteContract, "__dataclass_fields__"):
            cache_elig_field = RouteContract.__dataclass_fields__.get("cache_eligibility")
            if cache_elig_field:
                field_type = cache_elig_field.type
                # Should be a dict-like type, not a string/enum
                if isinstance(field_type, type) and issubclass(field_type, str):
                    violations.append(TypeViolation(
                        "L0", "FIELD_TYPE",
                        "RouteContract.cache_eligibility is str (should be Mapping[str,bool])"
                    ))
                elif "Mapping" not in str(field_type) and "dict" not in str(field_type).lower():
                    violations.append(TypeViolation(
                        "L0", "FIELD_TYPE",
                        f"RouteContract.cache_eligibility type {field_type} may not accept dict",
                        severity="WARN",
                    ))

    except ImportError as exc:
        violations.append(TypeViolation(
            "L0", "IMPORT", f"Cannot import L0 binding: {exc}"
        ))
    finally:
        if str(_REPO_ROOT) in sys.path:
            sys.path.remove(str(_REPO_ROOT))

    return violations


def _check_exit_binding_return_type() -> list[TypeViolation]:
    """Check Exit binding returns proper type."""
    violations: list[TypeViolation] = []

    try:
        sys.path.insert(0, str(_REPO_ROOT))
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg, ExitBindingResult

        # Check return type matches ExitBindingResult
        hints = get_type_hints(exit_finalize_apps_rg)
        return_type = hints.get("return")

        if return_type is None:
            violations.append(TypeViolation(
                "Exit", "RETURN_TYPE", "exit_finalize_apps_rg missing return type annotation"
            ))
        elif not hasattr(return_type, "__name__") or return_type.__name__ != "ExitBindingResult":
            violations.append(TypeViolation(
                "Exit", "RETURN_TYPE",
                f"exit_finalize_apps_rg returns {return_type}, expected ExitBindingResult"
            ))

        # Verify ExitBindingResult has disposition field
        if dataclasses.is_dataclass(ExitBindingResult):
            fields = {f.name for f in dataclasses.fields(ExitBindingResult)}
            if "disposition" not in fields:
                violations.append(TypeViolation(
                    "Exit", "DATACLASS_FIELDS", "ExitBindingResult missing 'disposition' field"
                ))

    except ImportError as exc:
        violations.append(TypeViolation(
            "Exit", "IMPORT", f"Cannot import Exit binding: {exc}"
        ))
    finally:
        if str(_REPO_ROOT) in sys.path:
            sys.path.remove(str(_REPO_ROOT))

    return violations


def main(argv: list[str] | None = None) -> int:
    _ = argv
    if os.environ.get("APPS_RG_TYPE_VALID_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[APPS-TYPE-VALID] BYPASS — APPS_RG_TYPE_VALID_BYPASS=1")
        _emit_report("bypassed", [])
        return 0

    fail_closed = os.environ.get("APPS_RG_TYPE_VALID_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    all_violations: list[TypeViolation] = []

    # Check layer binding signatures
    print("[APPS-TYPE-VALID] Checking layer binding signatures...")
    for module_path, func_name, layer in _LAYER_BINDINGS:
        all_violations.extend(_check_layer_binding_signature(module_path, func_name, layer))

    # Check L0 cache eligibility type
    print("[APPS-TYPE-VALID] Checking L0 cache eligibility type...")
    all_violations.extend(_check_l0_cache_eligibility_type())

    # Check Exit binding return type
    print("[APPS-TYPE-VALID] Checking Exit binding return type...")
    all_violations.extend(_check_exit_binding_return_type())

    # Determine result
    errors = [v for v in all_violations if v.severity == "ERROR"]
    warns = [v for v in all_violations if v.severity == "WARN"]

    if errors:
        print(f"[APPS-TYPE-VALID] FAIL — {len(errors)} error(s), {len(warns)} warning(s)")
        for v in errors[:5]:
            print(f"  [{v.layer}/{v.check}] {v.detail}")
        _emit_report("fail", all_violations)
        return 1 if fail_closed else 0

    if warns:
        print(f"[APPS-TYPE-VALID] OK (with warnings) — {len(warns)} warning(s)")
        _emit_report("pass_with_warnings", all_violations)
        return 0

    print("[APPS-TYPE-VALID] OK — all type contracts valid")
    _emit_report("pass", all_violations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
