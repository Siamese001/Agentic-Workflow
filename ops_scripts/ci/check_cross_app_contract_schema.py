"""CI gate: cross-app contract schema validator.

Validates instances of the five cross-app data contracts:

  - REQ-CROSS-APP-AGENTSPEC-001            (AgentSpec)
  - REQ-CROSS-APP-EVIDENCE-PACKET-001      (EvidencePacket)
  - REQ-CROSS-APP-EVAL-RUBRIC-001          (EvaluationRubric)
  - REQ-CROSS-APP-OVERFIT-REPORT-001       (OverfitReport)
  - REQ-CROSS-APP-RELEASE-RECOMMENDATION-001 (ReleaseRecommendation)

Discovery rules
---------------
- AgentSpec      instances at:  apps_*/config/specs/agent_spec.*.yaml
                 fixtures at:    tests/**/fixtures/agentspec/*.yaml
- EvidencePacket fixtures at:    tests/**/fixtures/evidence_packet/*.yaml
- EvalRubric     instances at:   apps_*/config/rubrics/*.yaml
- OverfitReport  fixtures at:    tests/**/fixtures/overfit_report/*.yaml
- ReleaseRecmnd  fixtures at:    tests/**/fixtures/release_recommendation/*.yaml

Discovery is lenient: a directory missing entirely is NOT a failure (no instances yet).
A file present but malformed IS a failure.

Validation
----------
Two passes:
  1. JSON-Schema validation against the contract's `schema` block.
  2. Invariant checks listed under the contract's `invariants` block — implemented
     as code-level checks below (a small invariant runner).

Exit codes
----------
0 — all discovered instances pass schema + invariants.
1 — at least one instance fails.
2 — operational error (cannot read contract file, etc).

Bypass
------
CROSS_APP_CONTRACT_BYPASS=1 in env logs a bypass row to
`artifacts/governance/cross_app_contract_violations.jsonl` and exits 0.

Plan: docs/requirements/contracts/REQ-CROSS-APP-* (Phase A).
"""

from __future__ import annotations

# This script reads YAML files; it does not query ADG views directly.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "docs" / "requirements" / "contracts"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "cross_app_contract_violations.jsonl"

CONTRACT_FILES = {
    "AgentSpec": "REQ-CROSS-APP-AGENTSPEC-001.contract.yaml",
    "EvidencePacket": "REQ-CROSS-APP-EVIDENCE-PACKET-001.contract.yaml",
    "EvaluationRubric": "REQ-CROSS-APP-EVAL-RUBRIC-001.contract.yaml",
    "OverfitReport": "REQ-CROSS-APP-OVERFIT-REPORT-001.contract.yaml",
    "ReleaseRecommendation": "REQ-CROSS-APP-RELEASE-RECOMMENDATION-001.contract.yaml",
}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    contract: str
    instance_path: str
    rule_id: str
    severity: str  # error | warn
    message: str

    def to_jsonl(self) -> str:
        return json.dumps(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "contract": self.contract,
                "instance_path": self.instance_path,
                "rule_id": self.rule_id,
                "severity": self.severity,
                "message": self.message,
            },
            sort_keys=True,
        )


@dataclass
class GateResult:
    instances_scanned: int = 0
    schema_failures: int = 0
    invariant_failures: int = 0
    violations: list[Violation] = field(default_factory=list)


# ---------------------------------------------------------------------------
# YAML loader (best-effort: prefer pyyaml, fall back to a minimal loader)
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        raise RuntimeError(
            "pyyaml is required to validate cross-app contract instances. "
            "Install via `pip install pyyaml`."
        )
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _glob_apps(pattern: str) -> list[Path]:
    """Return matching files under apps_*/<pattern>."""
    out: list[Path] = []
    for app_dir in REPO_ROOT.glob("apps_*"):
        if not app_dir.is_dir():
            continue
        out.extend(sorted(app_dir.glob(pattern)))
    return out


def _filter_underscore(paths: list[Path]) -> list[Path]:
    """Skip files whose stem starts with '_' — those are config fragments, not instances."""
    return [p for p in paths if not p.name.startswith("_")]


def discover_instances() -> dict[str, list[Path]]:
    """Map contract name -> list of instance paths."""
    return {
        "AgentSpec": (
            _glob_apps("config/specs/agent_spec.*.yaml")
            + sorted((REPO_ROOT / "tests").rglob("fixtures/agentspec/*.yaml"))
        ),
        "EvidencePacket": sorted(
            (REPO_ROOT / "tests").rglob("fixtures/evidence_packet/*.yaml")
        ),
        "EvaluationRubric": _filter_underscore(
            _glob_apps("config/rubrics/*.yaml")
            + sorted((REPO_ROOT / "tests").rglob("fixtures/evaluation_rubric/*.yaml"))
        ),
        "OverfitReport": sorted(
            (REPO_ROOT / "tests").rglob("fixtures/overfit_report/*.yaml")
        ),
        "ReleaseRecommendation": sorted(
            (REPO_ROOT / "tests").rglob("fixtures/release_recommendation/*.yaml")
        ),
    }


# ---------------------------------------------------------------------------
# Minimal JSON-Schema validator (subset sufficient for our contracts)
# ---------------------------------------------------------------------------


_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def _check_type(value: Any, type_decl: Any) -> bool:
    if isinstance(type_decl, str):
        py_type = _TYPE_MAP.get(type_decl)
        return py_type is not None and isinstance(value, py_type)
    if isinstance(type_decl, list):
        return any(_check_type(value, t) for t in type_decl)
    return True


def _validate(value: Any, schema: dict, path: str = "$") -> list[str]:
    """Subset JSON-Schema validator. Returns list of error messages."""
    errs: list[str] = []
    if "type" in schema:
        if not _check_type(value, schema["type"]):
            errs.append(f"{path}: expected type {schema['type']!r}, got {type(value).__name__}")
            return errs

    if "enum" in schema:
        if value not in schema["enum"]:
            errs.append(f"{path}: value {value!r} not in enum {schema['enum']}")

    if "pattern" in schema and isinstance(value, str):
        if not re.match(schema["pattern"], value):
            errs.append(f"{path}: value {value!r} does not match pattern {schema['pattern']!r}")

    if "minLength" in schema and isinstance(value, str):
        if len(value) < schema["minLength"]:
            errs.append(f"{path}: length {len(value)} < minLength {schema['minLength']}")
    if "maxLength" in schema and isinstance(value, str):
        if len(value) > schema["maxLength"]:
            errs.append(f"{path}: length {len(value)} > maxLength {schema['maxLength']}")

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errs.append(f"{path}: value {value} < minimum {schema['minimum']}")
    if "maximum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value > schema["maximum"]:
            errs.append(f"{path}: value {value} > maximum {schema['maximum']}")

    if "minItems" in schema and isinstance(value, list):
        if len(value) < schema["minItems"]:
            errs.append(f"{path}: items {len(value)} < minItems {schema['minItems']}")
    if "maxItems" in schema and isinstance(value, list):
        if len(value) > schema["maxItems"]:
            errs.append(f"{path}: items {len(value)} > maxItems {schema['maxItems']}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errs.append(f"{path}: missing required field {key!r}")
        props = schema.get("properties", {})
        for key, sub_schema in props.items():
            if key in value:
                errs.extend(_validate(value[key], sub_schema, f"{path}.{key}"))

    if "items" in schema and isinstance(value, list):
        item_schema = schema["items"]
        for i, item in enumerate(value):
            errs.extend(_validate(item, item_schema, f"{path}[{i}]"))

    return errs


# ---------------------------------------------------------------------------
# Invariant runners (one per contract)
# ---------------------------------------------------------------------------


def _check_agentspec_invariants(spec: dict, path: Path) -> list[Violation]:
    out: list[Violation] = []
    p = str(path)

    # SPEC-INV-001: non-WORKFLOW tier => non-empty justification
    agency = spec.get("agency", {})
    tier = agency.get("tier")
    if tier in {"SINGLE_AGENT", "MULTI_AGENT"}:
        just = (agency.get("justification") or "").strip()
        if not just:
            out.append(
                Violation(
                    "AgentSpec", p, "SPEC-INV-001", "error",
                    f"agency.tier={tier} requires non-empty agency.justification",
                )
            )

    # SPEC-INV-002: memory_policy.promotion_path == UWG_only
    mp = spec.get("memory_policy", {})
    if mp.get("promotion_path") not in {None, "UWG_only"}:
        out.append(
            Violation(
                "AgentSpec", p, "SPEC-INV-002", "error",
                f"memory_policy.promotion_path={mp.get('promotion_path')!r}; only UWG_only is valid",
            )
        )

    # SPEC-INV-003: instruction_hierarchy fixed order
    expected = [
        "policy", "registry_constraints", "developer_constraints",
        "evidence_rules", "tone_bounds", "one_off_user_instruction",
    ]
    ih = spec.get("instruction_hierarchy", [])
    if list(ih) != expected:
        out.append(
            Violation(
                "AgentSpec", p, "SPEC-INV-003", "error",
                f"instruction_hierarchy must be the fixed 6-element ordered list: {expected}",
            )
        )

    # SPEC-INV-004: signed_by non-empty (for non-draft)
    status = spec.get("status", "experimental")
    signed_by = (spec.get("signed_by") or "").strip()
    if not signed_by and status not in {"draft", "experimental"}:
        out.append(
            Violation(
                "AgentSpec", p, "SPEC-INV-004", "error",
                "signed_by must be non-empty for any spec written to the registry",
            )
        )

    # SPEC-INV-005: compilation_hash present + 64-hex (when populated)
    ca = spec.get("compiled_artifacts") or {}
    ch = ca.get("compilation_hash", "")
    if ch and not re.match(r"^[a-f0-9]{64}$", ch):
        out.append(
            Violation(
                "AgentSpec", p, "SPEC-INV-005", "error",
                f"compiled_artifacts.compilation_hash must be 64-hex; got {ch!r}",
            )
        )

    return out


def _check_evidence_packet_invariants(pkt: dict, path: Path) -> list[Violation]:
    out: list[Violation] = []
    p = str(path)
    kind = pkt.get("kind")
    auth = pkt.get("authority_label")
    influence = pkt.get("influence_scope", []) or []

    # EVP-INV-001: tone_sample => authority_label=reference, influence subset
    if kind == "tone_sample":
        if auth != "reference":
            out.append(
                Violation(
                    "EvidencePacket", p, "EVP-INV-001", "error",
                    f"tone_sample requires authority_label=reference; got {auth!r}",
                )
            )
        allowed = {"tone_bounds", "response_format"}
        bad = [s for s in influence if s not in allowed]
        if bad:
            out.append(
                Violation(
                    "EvidencePacket", p, "EVP-INV-001", "error",
                    f"tone_sample.influence_scope must subset {sorted(allowed)}; offenders: {bad}",
                )
            )

    # EVP-INV-002: user-supplied content => intent or data
    origin = (pkt.get("source_lineage", {}) or {}).get("origin", "")
    if "user_intent" in origin or "user_data" in origin:
        if auth not in {"intent", "data"}:
            out.append(
                Violation(
                    "EvidencePacket", p, "EVP-INV-002", "error",
                    f"user-supplied origin requires authority_label in [intent, data]; got {auth!r}",
                )
            )

    # EVP-INV-003: rule_set / policy => authoritative
    if kind in {"rule_set", "policy", "tool_constraint"}:
        if auth != "authoritative":
            out.append(
                Violation(
                    "EvidencePacket", p, "EVP-INV-003", "error",
                    f"kind={kind} requires authority_label=authoritative; got {auth!r}",
                )
            )

    return out


def _check_eval_rubric_invariants(rub: dict, path: Path) -> list[Violation]:
    out: list[Violation] = []
    p = str(path)

    # RUB-INV-001: weight sum
    dims = rub.get("dimensions", []) or []
    pos = [d for d in dims if d.get("direction", "higher_is_better") == "higher_is_better"]
    s = sum(float(d.get("weight", 0)) for d in pos)
    if pos and abs(s - 1.0) > 0.01:
        out.append(
            Violation(
                "EvaluationRubric", p, "RUB-INV-001", "error",
                f"sum(weights) over higher_is_better dimensions = {s:.3f}; expected ~1.0",
            )
        )

    # RUB-INV-002: judge_model_pin non-empty
    pin = rub.get("judge_model_pin", {}) or {}
    if not all(pin.get(k) for k in ("provider", "model", "version")):
        out.append(
            Violation(
                "EvaluationRubric", p, "RUB-INV-002", "error",
                "judge_model_pin.{provider, model, version} must all be non-empty",
            )
        )

    # RUB-INV-003: calibration freshness
    cal = rub.get("human_calibration", {}) or {}
    last_iso = cal.get("last_calibrated_at", "")
    cadence = cal.get("cadence", "")
    if last_iso and cadence:
        try:
            last = datetime.fromisoformat(last_iso.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            # P30D heuristic; only flag obvious staleness (>2x cadence days)
            m = re.match(r"P(\d+)D", cadence)
            if m:
                days = int(m.group(1))
                if (now - last).days > days * 2:
                    out.append(
                        Violation(
                            "EvaluationRubric", p, "RUB-INV-003", "warn",
                            f"human_calibration is {(now-last).days}d old > 2x cadence ({days}d)",
                        )
                    )
        except (ValueError, TypeError):
            pass

    return out


def _check_overfit_report_invariants(rep: dict, path: Path) -> list[Violation]:
    out: list[Violation] = []
    p = str(path)

    # OVR-INV-001: independence
    ind = rep.get("independence_attestation", {}) or {}
    if ind.get("judge_scorecard_consulted") is not False:
        out.append(
            Violation(
                "OverfitReport", p, "OVR-INV-001", "error",
                "independence_attestation.judge_scorecard_consulted must be false (literal)",
            )
        )

    # OVR-INV-003: fake_history without memory pointer => flag
    fh = rep.get("signals", {}).get("fake_history", {}) or {}
    spans = fh.get("spans", []) or []
    has_unanchored = any(s.get("has_memory_pointer") is False for s in spans)
    flags = rep.get("flags", []) or []
    if has_unanchored and "fake_history_detected" not in flags:
        out.append(
            Violation(
                "OverfitReport", p, "OVR-INV-003", "error",
                "fake_history span without memory_pointer must emit fake_history_detected flag",
            )
        )

    return out


def _check_release_recommendation_invariants(rec: dict, path: Path) -> list[Violation]:
    out: list[Violation] = []
    p = str(path)
    verdict = rec.get("verdict")
    triggers = rec.get("hitl_triggers_fired", []) or []

    # REC-INV-001: is_recommendation_only=true
    aa = rec.get("authority_attestation", {}) or {}
    if aa.get("is_recommendation_only") is not True:
        out.append(
            Violation(
                "ReleaseRecommendation", p, "REC-INV-001", "error",
                "authority_attestation.is_recommendation_only must be true (literal)",
            )
        )

    # REC-INV-002: HITL triggers force hold/escalate
    if triggers and verdict in {"approve", "bounded_revise"}:
        out.append(
            Violation(
                "ReleaseRecommendation", p, "REC-INV-002", "error",
                f"hitl_triggers_fired={triggers} but verdict={verdict}; must be hold_for_human or reject",
            )
        )

    # REC-INV-003: bounded_revise must have scope.max_revise_attempts=1
    if verdict == "bounded_revise":
        scope = rec.get("bounded_revise_scope") or {}
        attempts = scope.get("max_revise_attempts", 0)
        if attempts != 1:
            out.append(
                Violation(
                    "ReleaseRecommendation", p, "REC-INV-003", "error",
                    f"bounded_revise requires bounded_revise_scope.max_revise_attempts=1; got {attempts}",
                )
            )

    return out


_INVARIANT_RUNNERS = {
    "AgentSpec": _check_agentspec_invariants,
    "EvidencePacket": _check_evidence_packet_invariants,
    "EvaluationRubric": _check_eval_rubric_invariants,
    "OverfitReport": _check_overfit_report_invariants,
    "ReleaseRecommendation": _check_release_recommendation_invariants,
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _load_contract_schema(name: str) -> dict:
    p = CONTRACTS_DIR / CONTRACT_FILES[name]
    if not p.exists():
        raise FileNotFoundError(f"Contract file missing: {p}")
    contract = _load_yaml(p)
    if not isinstance(contract, dict):
        raise ValueError(f"Contract {p} did not parse to a mapping")
    return contract.get("schema", {}) or {}


def _validate_one(contract_name: str, path: Path, schema: dict) -> list[Violation]:
    try:
        instance = _load_yaml(path)
    except Exception as exc:
        return [Violation(contract_name, str(path), "PARSE", "error", f"yaml parse error: {exc}")]
    if instance is None:
        return [Violation(contract_name, str(path), "EMPTY", "error", "instance is empty")]

    out: list[Violation] = []
    schema_errs = _validate(instance, schema)
    out.extend(
        Violation(contract_name, str(path), "SCHEMA", "error", e) for e in schema_errs
    )
    runner = _INVARIANT_RUNNERS.get(contract_name)
    if runner is not None and isinstance(instance, dict):
        out.extend(runner(instance, path))
    return out


def _print_progress(total: int, current: int, label: str) -> None:
    if total == 0:
        return
    pct = int(100 * current / total)
    width = 40
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    color = "\033[91m" if pct < 40 else "\033[93m" if pct < 70 else "\033[94m" if pct < 90 else "\033[92m"
    sys.stdout.write(f"\r{color}[{bar}]\033[0m {pct:3d}% ({current}/{total}) - {label}")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate cross-app contract instances.")
    parser.add_argument("--strict", action="store_true", help="Promote warn-level violations to errors.")
    args = parser.parse_args(argv)

    if os.environ.get("CROSS_APP_CONTRACT_BYPASS") == "1":
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "reason": "bypass",
                        "env": "CROSS_APP_CONTRACT_BYPASS=1",
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        print("[cross-app-contract-gate] bypass active; exit 0")
        return 0

    try:
        schemas = {name: _load_contract_schema(name) for name in CONTRACT_FILES}
    except Exception as exc:
        print(f"[cross-app-contract-gate] operational error: {exc}", file=sys.stderr)
        return 2

    inventory = discover_instances()
    total = sum(len(v) for v in inventory.values())
    result = GateResult()
    seen = 0

    for contract_name, paths in inventory.items():
        for path in paths:
            seen += 1
            _print_progress(total, seen, f"{contract_name}: {path.name}")
            violations = _validate_one(contract_name, path, schemas[contract_name])
            for v in violations:
                if v.rule_id == "SCHEMA":
                    result.schema_failures += 1
                else:
                    result.invariant_failures += 1
                result.violations.append(v)
            result.instances_scanned += 1

    if total == 0:
        print("[cross-app-contract-gate] no instances discovered (advisory pass)")

    # Persist violations
    if result.violations:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as f:
            for v in result.violations:
                f.write(v.to_jsonl() + "\n")

    # Print summary
    print(
        f"[cross-app-contract-gate] scanned={result.instances_scanned} "
        f"schema_failures={result.schema_failures} "
        f"invariant_failures={result.invariant_failures}"
    )
    for v in result.violations[:25]:  # cap output
        print(f"  [{v.severity:5s}] {v.contract:22s} {v.rule_id:14s} {v.instance_path}")
        print(f"            -> {v.message}")
    if len(result.violations) > 25:
        print(f"  ... and {len(result.violations) - 25} more (see {VIOLATIONS_LOG})")

    error_count = sum(
        1 for v in result.violations
        if v.severity == "error" or (args.strict and v.severity == "warn")
    )
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
