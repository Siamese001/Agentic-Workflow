"""Deterministic SVP documentation review gates and X3 disposition.

The weekly automation uses ``--mode audit`` and cannot authorize publication.
An approved manual refresh uses ``--mode edit`` with a machine-readable approval
receipt, runs this command before and after editing, and hands ALLOW_TO_PR to the
repo's existing PR-only publisher.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".codex" / "automations" / "svp-readme-documentation-refresh" / "reviewer_packet.v1.json"
WEEKLY_AUTOMATION = REPO_ROOT / ".codex" / "automations" / "svp-readme-documentation-refresh" / "automation.toml"
MANUAL_AUTOMATION = REPO_ROOT / ".codex" / "automations" / "on-demand-svp-documentation-refresh" / "automation.toml"
SCHEMA_DIR = REPO_ROOT / ".codex" / "schemas"
SCHEMAS = {
    "x1d": SCHEMA_DIR / "svp_docs_x1d_v1.schema.json",
    "x2": SCHEMA_DIR / "svp_docs_x2_v1.schema.json",
    "x3": SCHEMA_DIR / "svp_docs_x3_v1.schema.json",
    "run": SCHEMA_DIR / "svp_docs_run_v1.schema.json",
}
X2_GATE_IDS = (
    "x2_toml_parse",
    "x2_app_launcher_ssot",
    "x2_stale_active_terms",
    "x2_relative_links",
    "x2_unsupported_claims_regex",
    "x2_docs_only_scope",
    "x2_high_signal_packet_present",
    "x2_required_sections",
    "x2_codex_primary",
    "x2_enforcement_home",
    "x2_diff_check",
    "x2_publication_isolation",
    "x2_architecture_status_consistency",
    "x2_claim_evidence_map",
    "x2_proof_command_resolves",
    "x2_receipt_schema_validate",
    "x2_approval_mode",
    "x2_no_absolute_unproven_language",
)
ALLOWED_X3 = {"ALLOW_TO_PR", "PLAN_ONLY", "BLOCK", "NOOP", "ESCALATE_HUMAN"}
DOC_ROOT_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "LICENSE.md",
}
UNSUPPORTED_CLAIM_RE = re.compile(
    r"\b(?:SOC\s*2|HIPAA|GDPR|PCI(?:-DSS)?|customer(?:s)?|ROI|support SLA|roadmap commitment)\b",
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PYTHON_SCRIPT_RE = re.compile(r"\bpython(?:\.exe)?\s+([A-Za-z0-9_./\\-]+\.py)\b")


@dataclass(frozen=True)
class GateResult:
    id: str
    status: str
    severity: str
    summary: str
    evidence: list[str]


def _run(argv: Sequence[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _git(*args: str, timeout: int = 60) -> tuple[int, str, str]:
    proc = _run(("git", *args), timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _load_manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


def _active_paths(manifest: dict[str, Any]) -> list[Path]:
    names = [*manifest.get("active_documents", []), *manifest.get("authority_files", [])]
    return [REPO_ROOT / str(name) for name in names]


def _packet_digest(manifest: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for path in sorted(_active_paths(manifest), key=lambda item: item.as_posix()):
        relative = path.relative_to(REPO_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if path.exists() and path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _git_ref(ref: str) -> str:
    code, stdout, stderr = _git("rev-parse", ref)
    if code != 0:
        raise RuntimeError(stderr or f"could not resolve {ref}")
    return stdout


def _current_branch() -> str:
    code, stdout, _ = _git("branch", "--show-current")
    return stdout if code == 0 and stdout else "DETACHED"


def _changed_files(base_ref: str) -> list[str]:
    changed: set[str] = set()
    code, stdout, _ = _git("diff", "--name-only", f"{base_ref}...HEAD")
    if code == 0:
        changed.update(line.strip() for line in stdout.splitlines() if line.strip())
    code, stdout, _ = _git("status", "--porcelain=v1")
    if code == 0:
        for line in stdout.splitlines():
            if len(line) >= 4:
                value = line[3:].strip()
                if " -> " in value:
                    value = value.split(" -> ", 1)[1]
                if value:
                    changed.add(value)
    return sorted(changed)


def _diff_digest(base_ref: str) -> str:
    code, stdout, stderr = _git("diff", "--binary", f"{base_ref}...HEAD")
    payload = stdout if code == 0 else f"ERROR:{stderr}"
    return _sha256_text(payload)


def _gate(
    gate_id: str,
    ok: bool,
    summary: str,
    evidence: Iterable[str] = (),
    *,
    warn: bool = False,
    not_applicable: bool = False,
) -> GateResult:
    if not_applicable:
        status = "NOT_APPLICABLE"
        severity = "advisory"
    elif ok:
        status = "WARN" if warn else "PASS"
        severity = "advisory"
    else:
        status = "FAIL"
        severity = "blocking"
    return GateResult(gate_id, status, severity, summary, list(evidence))


def _toml_gate() -> GateResult:
    failures: list[str] = []
    for path in (WEEKLY_AUTOMATION, MANUAL_AUTOMATION):
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
    return _gate("x2_toml_parse", not failures, "SVP automation TOML parses.", failures)


def _launcher_gate() -> GateResult:
    failures: list[str] = []
    try:
        weekly = tomllib.loads(WEEKLY_AUTOMATION.read_text(encoding="utf-8"))
        manual = tomllib.loads(MANUAL_AUTOMATION.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return _gate("x2_app_launcher_ssot", False, "SVP launcher contract could not be loaded.", [str(exc)])

    expected = (
        (weekly, "weekly-svp-readme-documentation-refresh", "cron", "ACTIVE", "audit_only", False),
        (manual, "on-demand-svp-documentation-refresh", "manual", "ON_DEMAND", "approved_edit", True),
    )
    for data, automation_id, kind, status, mode, approval_required in expected:
        if data.get("id") != automation_id:
            failures.append(f"{automation_id}: id mismatch")
        if data.get("kind") != kind:
            failures.append(f"{automation_id}: kind must be {kind}")
        if data.get("status") != status:
            failures.append(f"{automation_id}: status must be {status}")
        contract = data.get("svp_docs")
        if not isinstance(contract, dict):
            failures.append(f"{automation_id}: missing [svp_docs]")
            continue
        if contract.get("mode") != mode:
            failures.append(f"{automation_id}: svp_docs.mode must be {mode}")
        if bool(contract.get("require_approval_receipt")) != approval_required:
            failures.append(f"{automation_id}: approval requirement mismatch")
        if contract.get("publication_handoff") != "on-demand-pr-main-publisher":
            failures.append(f"{automation_id}: publication handoff must be on-demand-pr-main-publisher")
        if data.get("allow_direct_main_push") is not False:
            failures.append(f"{automation_id}: allow_direct_main_push must be false")
    return _gate("x2_app_launcher_ssot", not failures, "SVP launchers preserve one repo SSOT and PR-only publication.", failures)


def _stale_terms_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    terms = [str(term).casefold() for term in manifest.get("stale_active_terms", [])]
    historical = [str(term).casefold() for term in manifest.get("historical_context_markers", [])]
    for relative in manifest.get("active_documents", []):
        path = REPO_ROOT / str(relative)
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            folded = line.casefold()
            if any(marker in folded for marker in historical):
                continue
            for term in terms:
                if term in folded:
                    findings.append(f"{relative}:{number}: {term}")
    return _gate("x2_stale_active_terms", not findings, "Active reviewer documents contain no uncaveated stale terms.", findings)


def _relative_links_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    for relative in manifest.get("active_documents", []):
        path = REPO_ROOT / str(relative)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in MARKDOWN_LINK_RE.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(REPO_ROOT.resolve())
            except ValueError:
                findings.append(f"{relative}: link escapes repository: {target}")
                continue
            if not candidate.exists():
                findings.append(f"{relative}: missing link target {target}")
    return _gate("x2_relative_links", not findings, "Reviewer-packet relative links resolve.", findings)


def _unsupported_claims_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    caveats = ("not ", "no ", "historical", "unsupported", "avoid ", "do not ", "without claiming")
    for relative in manifest.get("active_documents", []):
        path = REPO_ROOT / str(relative)
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if UNSUPPORTED_CLAIM_RE.search(line) and not any(token in line.casefold() for token in caveats):
                findings.append(f"{relative}:{number}: {line.strip()}")
    return _gate("x2_unsupported_claims_regex", not findings, "No uncaveated customer, compliance, ROI, SLA, or roadmap claims were detected.", findings)


def _docs_only_gate(changed: list[str], implementation_change: bool) -> GateResult:
    if implementation_change:
        return _gate(
            "x2_docs_only_scope",
            True,
            "Gate implementation changes are explicitly outside a documentation publication run.",
            not_applicable=True,
        )
    invalid: list[str] = []
    for name in changed:
        path = Path(name)
        allowed = (
            name in DOC_ROOT_FILES
            or name.startswith("docs/")
            or name.startswith(".github/ISSUE_TEMPLATE/")
            or name.startswith(".github/PULL_REQUEST_TEMPLATE")
            or path.suffix.casefold() in {".md", ".mdx"}
        )
        if not allowed:
            invalid.append(name)
    return _gate("x2_docs_only_scope", not invalid, "Changed files are documentation-only.", invalid)


def _packet_present_gate(manifest: dict[str, Any]) -> GateResult:
    missing = [str(path.relative_to(REPO_ROOT)) for path in _active_paths(manifest) if not path.exists()]
    return _gate("x2_high_signal_packet_present", not missing, "The versioned high-signal reviewer packet is complete.", missing)


def _required_sections_gate(manifest: dict[str, Any]) -> GateResult:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8", errors="ignore")
    missing = [str(section) for section in manifest.get("required_readme_sections", []) if str(section) not in readme]
    return _gate("x2_required_sections", not missing, "Root README contains the required executive and reviewer sections.", missing)


def _command_gate(gate_id: str, argv: Sequence[str], summary: str) -> GateResult:
    try:
        proc = _run(argv, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        return _gate(gate_id, False, summary, [str(exc)])
    evidence = [f"exit_code={proc.returncode}"]
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-12:]
    evidence.extend(tail)
    return _gate(gate_id, proc.returncode == 0, summary, evidence)


def _diff_check_gate() -> GateResult:
    code, stdout, stderr = _git("diff", "--check")
    evidence = [value for value in (stdout, stderr) if value]
    return _gate("x2_diff_check", code == 0, "git diff --check passes.", evidence)


def _publication_isolation_gate(mode: str, branch: str, changed: list[str], implementation_change: bool) -> GateResult:
    if implementation_change:
        return _gate(
            "x2_publication_isolation",
            branch not in {"main", "master", "DETACHED"},
            "Gate implementation is isolated on a named non-main branch.",
            [f"branch={branch}"],
        )
    failures: list[str] = []
    if mode == "edit" and branch in {"main", "master", "DETACHED"}:
        failures.append(f"edit mode requires a named non-main branch; branch={branch}")
    if mode == "edit" and not changed:
        failures.append("edit mode has no changed documentation files")
    return _gate("x2_publication_isolation", not failures, "Documentation publication work is isolated from main.", failures)


def _registry_snapshot() -> tuple[list[str], list[str]]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    module = importlib.import_module("apps_shared.integrations.app_registry")
    governed_type = getattr(module, "GovernedAppEntry")
    formal_type = getattr(module, "FormalExceptionEntry")
    registry = getattr(module, "APP_REGISTRY")
    governed = sorted(name for name, entry in registry.items() if isinstance(entry, governed_type))
    exceptions = sorted(name for name, entry in registry.items() if isinstance(entry, formal_type))
    return governed, exceptions


def _architecture_consistency_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    try:
        governed, exceptions = _registry_snapshot()
    except Exception as exc:
        return _gate("x2_architecture_status_consistency", False, "APP_REGISTRY could not be loaded.", [repr(exc)])
    joined = "\n".join(
        (REPO_ROOT / str(relative)).read_text(encoding="utf-8", errors="ignore")
        for relative in manifest.get("active_documents", [])
        if (REPO_ROOT / str(relative)).exists()
    ).casefold()
    stale_phrases = ("5 governed apps + 2 formal exceptions", "36/36 checks", "all 7 apps", "all seven apps")
    findings.extend(f"stale phrase: {phrase}" for phrase in stale_phrases if phrase in joined)
    expected = f"{len(governed)} governed"
    expected_exceptions = f"{len(exceptions)} formal exception"
    if expected not in joined:
        findings.append(f"reviewer packet does not state current governed count: {len(governed)}")
    if expected_exceptions not in joined:
        findings.append(f"reviewer packet does not state current formal-exception count: {len(exceptions)}")
    for app in governed:
        if app.casefold() not in joined:
            findings.append(f"governed app missing from reviewer packet: {app}")
    for app in exceptions:
        if app.casefold() not in joined:
            findings.append(f"formal exception missing from reviewer packet: {app}")
    evidence = [f"governed={governed}", f"formal_exceptions={exceptions}", *findings]
    return _gate("x2_architecture_status_consistency", not findings, "Reviewer status agrees with APP_REGISTRY.", evidence)


def _claim_evidence_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    for item in manifest.get("claim_evidence", []):
        claim_id = str(item.get("claim_id", "missing"))
        evidence_paths = [REPO_ROOT / str(path) for path in item.get("evidence_paths", [])]
        if not evidence_paths:
            findings.append(f"{claim_id}: no evidence paths")
        for path in evidence_paths:
            if not path.exists():
                findings.append(f"{claim_id}: missing {path.relative_to(REPO_ROOT)}")
        if not item.get("proof_commands"):
            findings.append(f"{claim_id}: no proof commands")
    return _gate("x2_claim_evidence_map", not findings, "Major claims map to repository evidence and proof commands.", findings)


def _proof_command_gate(manifest: dict[str, Any]) -> GateResult:
    findings: list[str] = []
    commands: set[str] = set()
    for item in manifest.get("claim_evidence", []):
        commands.update(str(command) for command in item.get("proof_commands", []))
    for relative in manifest.get("active_documents", []):
        path = REPO_ROOT / str(relative)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        commands.update(f"python {match}" for match in PYTHON_SCRIPT_RE.findall(text))
    for command in sorted(commands):
        match = PYTHON_SCRIPT_RE.search(command)
        if not match:
            continue
        target = REPO_ROOT / match.group(1).replace("\\", "/")
        if not target.exists():
            findings.append(f"missing command target: {command}")
    return _gate("x2_proof_command_resolves", not findings, "Referenced Python proof command targets exist.", findings)


def _validate_shallow_schema(schema: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in receipt:
            errors.append(f"missing required field {key}")
    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in receipt or not isinstance(rules, dict):
            continue
        if "const" in rules and receipt[key] != rules["const"]:
            errors.append(f"{key}: expected {rules['const']!r}, got {receipt[key]!r}")
        if "enum" in rules and receipt[key] not in rules["enum"]:
            errors.append(f"{key}: value {receipt[key]!r} not in enum")
    return errors


def _schema_gate(x1d_receipt: Path | None) -> GateResult:
    findings: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    for name, path in SCHEMAS.items():
        try:
            loaded[name] = _load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
    if x1d_receipt is not None and x1d_receipt.exists() and "x1d" in loaded:
        try:
            receipt = _load_json(x1d_receipt)
            findings.extend(f"x1d: {error}" for error in _validate_shallow_schema(loaded["x1d"], receipt))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings.append(f"x1d receipt: {exc}")
    return _gate("x2_receipt_schema_validate", not findings, "Checked-in receipt schemas parse and supplied receipts match required fields.", findings)


def _approval_gate(mode: str, branch: str, approval_receipt: Path | None) -> GateResult:
    if mode == "audit":
        return _gate("x2_approval_mode", True, "Audit mode is read-only and has no publication authority.", [f"branch={branch}"])
    findings: list[str] = []
    if approval_receipt is None or not approval_receipt.exists():
        findings.append("edit mode requires --approval-receipt")
    else:
        try:
            data = _load_json(approval_receipt)
            if data.get("schema_version") != "svp_docs_approval/v1":
                findings.append("approval schema_version must be svp_docs_approval/v1")
            if data.get("status") != "APPROVED":
                findings.append("approval status must be APPROVED")
            if data.get("plan_id") != "svp-docs-gate-hardening-7c4e2a" and not data.get("plan_id"):
                findings.append("approval receipt must name a plan_id")
            approved_branch = data.get("branch")
            if approved_branch and approved_branch != branch:
                findings.append(f"approval branch {approved_branch!r} does not match {branch!r}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings.append(str(exc))
    return _gate("x2_approval_mode", not findings, "Edit mode has explicit machine-readable approval.", findings)


def _changed_markdown_lines(base_ref: str, changed: list[str]) -> Iterable[tuple[str, int, str]]:
    for name in changed:
        if Path(name).suffix.casefold() not in {".md", ".mdx"}:
            continue
        code, stdout, _ = _git("diff", "--unified=0", f"{base_ref}...HEAD", "--", name)
        if code != 0:
            continue
        line_number = 0
        for line in stdout.splitlines():
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                line_number = int(match.group(1)) if match else 0
                continue
            if line.startswith("+") and not line.startswith("+++"):
                yield name, line_number, line[1:]
                line_number += 1
            elif not line.startswith("-"):
                line_number += 1


def _absolute_claim_gate(manifest: dict[str, Any], base_ref: str, changed: list[str]) -> GateResult:
    findings: list[str] = []
    terms = [str(term).casefold() for term in manifest.get("absolute_claim_terms", [])]
    for name, number, line in _changed_markdown_lines(base_ref, changed):
        folded = line.casefold()
        for term in terms:
            if term not in folded:
                continue
            evidence_anchor = "`" in line or "proof" in folded or "gate" in folded or "intended" in folded or "designed" in folded
            if not evidence_anchor:
                findings.append(f"{name}:{number}: unsupported absolute term {term!r}: {line.strip()}")
    return _gate("x2_no_absolute_unproven_language", not findings, "Changed documentation contains no unanchored absolute claims.", findings)


def _x2_decision(gates: Sequence[GateResult]) -> str:
    if any(gate.status == "FAIL" for gate in gates):
        return "BLOCK"
    if any(gate.status == "WARN" for gate in gates):
        return "WARN"
    return "ALLOW"


def _load_or_default_x1d(path: Path | None, run_id: str, packet_digest: str) -> dict[str, Any]:
    if path is not None and path.exists():
        return _load_json(path)
    return {
        "schema_version": "svp_docs_x1d/v1",
        "run_id": run_id,
        "packet_digest": packet_digest,
        "decision": "WARN",
        "overall_score": None,
        "scores": {},
        "blocking_findings": [],
        "recommended_edits": [],
        "judge": {
            "provider": "unavailable",
            "model": "unavailable",
            "rubric_version": "svp-docs-rubric/v1",
            "prompt_hash": _sha256_text("x1d unavailable"),
            "independent": False,
            "transport_status": "UNAVAILABLE"
        }
    }


def _x3_disposition(
    *,
    run_id: str,
    mode: str,
    phase: str,
    x2_decision: str,
    x1d: dict[str, Any],
    changed: list[str],
    approval_receipt: Path | None,
    prior_x2: str,
    implementation_change: bool,
) -> dict[str, Any]:
    x1d_decision = str(x1d.get("decision", "WARN"))
    high_findings = [
        item for item in x1d.get("blocking_findings", [])
        if isinstance(item, dict) and item.get("severity") == "high"
    ]
    authorized = mode == "edit" and approval_receipt is not None and approval_receipt.exists()
    if x2_decision == "BLOCK" or x1d_decision == "BLOCK" or high_findings:
        decision = "BLOCK"
        reason = "A deterministic gate or high-severity X1D finding blocked the run."
        next_action = "Remediate the blocking receipt findings and rerun the failed gate bundle."
    elif mode == "audit":
        if implementation_change or changed:
            decision = "PLAN_ONLY"
            reason = "Audit mode is read-only; material changes require the approved manual refresh path."
            next_action = "Review and approve the proposed documentation change plan."
        else:
            decision = "NOOP"
            reason = "No material documentation change is present and deterministic review gates passed."
            next_action = "No action required."
    elif phase == "pre":
        decision = "PLAN_ONLY"
        reason = "Pre-edit gates passed; editing may proceed within the approved isolated scope."
        next_action = "Apply the approved documentation edits, then run the post-edit gate."
    elif authorized and x2_decision in {"ALLOW", "WARN"} and x1d_decision in {"ALLOW", "WARN"}:
        decision = "ALLOW_TO_PR"
        reason = "Post-edit deterministic gates passed and explicit approval is present."
        next_action = "Hand the committed branch to on-demand-pr-main-publisher for PR-only publication."
    else:
        decision = "ESCALATE_HUMAN"
        reason = "Publication authority or senior-reader judgment is incomplete."
        next_action = "Obtain explicit approval or resolve the X1D transport/judgment gap."
    assert decision in ALLOWED_X3
    return {
        "schema_version": "svp_docs_x3/v1",
        "run_id": run_id,
        "decision": decision,
        "reason": reason,
        "x2_pre": prior_x2 if phase == "post" else x2_decision,
        "x1d": x1d_decision,
        "x2_post": x2_decision if phase == "post" else "NOT_RUN",
        "publication_authorized": bool(decision == "ALLOW_TO_PR" and authorized),
        "changed_files": changed,
        "required_next_action": next_action,
        "approval_receipt_ref": str(approval_receipt) if approval_receipt else None,
        "publication_handoff": "on-demand-pr-main-publisher" if decision == "ALLOW_TO_PR" else None
    }


def build_review(
    *,
    mode: str,
    phase: str,
    base_ref: str,
    output_dir: Path,
    approval_receipt: Path | None = None,
    x1d_receipt: Path | None = None,
    implementation_change: bool = False,
    run_id: str | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest()
    run_id = run_id or datetime.now(UTC).strftime("svp_docs_%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)
    branch = _current_branch()
    changed = _changed_files(base_ref)
    packet_digest = _packet_digest(manifest)
    diff_digest = _diff_digest(base_ref)
    try:
        head = _git_ref("HEAD")
        origin_main = _git_ref(base_ref)
    except RuntimeError as exc:
        head = "UNKNOWN"
        origin_main = f"UNRESOLVED:{exc}"

    gates = [
        _toml_gate(),
        _launcher_gate(),
        _stale_terms_gate(manifest),
        _relative_links_gate(manifest),
        _unsupported_claims_gate(manifest),
        _docs_only_gate(changed, implementation_change),
        _packet_present_gate(manifest),
        _required_sections_gate(manifest),
        _command_gate("x2_codex_primary", (sys.executable, "scripts/governance/verify_codex_primary.py"), "Codex primary verifier passes."),
        _command_gate("x2_enforcement_home", (sys.executable, "scripts/governance/verify_codex_enforcement_home.py", "--json"), "Codex enforcement-home verifier passes."),
        _diff_check_gate(),
        _publication_isolation_gate(mode, branch, changed, implementation_change),
        _architecture_consistency_gate(manifest),
        _claim_evidence_gate(manifest),
        _proof_command_gate(manifest),
        _schema_gate(x1d_receipt),
        _approval_gate(mode, branch, approval_receipt),
        _absolute_claim_gate(manifest, base_ref, changed)
    ]
    observed_ids = tuple(gate.id for gate in gates)
    if observed_ids != X2_GATE_IDS:
        raise AssertionError(f"X2 gate order drift: {observed_ids!r}")
    x2_decision = _x2_decision(gates)
    blocked_reasons = [gate.summary for gate in gates if gate.status == "FAIL"]
    x2 = {
        "schema_version": "svp_docs_x2/v1",
        "run_id": run_id,
        "phase": phase,
        "repo_sha": head,
        "origin_main_sha": origin_main,
        "packet_digest": packet_digest,
        "diff_digest": diff_digest,
        "decision": x2_decision,
        "gates": [asdict(gate) for gate in gates],
        "changed_files": changed,
        "blocked_reasons": blocked_reasons
    }
    x2_path = output_dir / f"x2_{phase}.json"
    x2_path.write_text(json.dumps(x2, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    x1d = _load_or_default_x1d(x1d_receipt, run_id, packet_digest)
    x1d_path = output_dir / "x1d.json"
    x1d_path.write_text(json.dumps(x1d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    prior_x2 = "NOT_RUN"
    if phase == "post":
        prior_path = output_dir / "x2_pre.json"
        if prior_path.exists():
            prior_x2 = str(_load_json(prior_path).get("decision", "NOT_RUN"))
    x3 = _x3_disposition(
        run_id=run_id,
        mode=mode,
        phase=phase,
        x2_decision=x2_decision,
        x1d=x1d,
        changed=changed,
        approval_receipt=approval_receipt,
        prior_x2=prior_x2,
        implementation_change=implementation_change
    )
    x3_path = output_dir / "x3.json"
    x3_path.write_text(json.dumps(x3, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "FAIL" if x3["decision"] == "BLOCK" else ("WARN" if x3["decision"] in {"PLAN_ONLY", "ESCALATE_HUMAN"} else "PASS")
    run_receipt = {
        "schema_version": "svp_docs_run/v1",
        "run_id": run_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "phase": phase,
        "repo": {"root": str(REPO_ROOT), "branch": branch, "head": head, "origin_main": origin_main},
        "packet_digest": packet_digest,
        "diff_digest": diff_digest,
        "approval_receipt_ref": str(approval_receipt) if approval_receipt else None,
        "receipts": {"x2": str(x2_path), "x1d": str(x1d_path), "x3": str(x3_path)},
        "status": status
    }
    run_path = output_dir / "run_receipt.json"
    run_path.write_text(json.dumps(run_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"x2": x2, "x1d": x1d, "x3": x3, "run_receipt": run_receipt}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("audit", "edit"), default="audit")
    parser.add_argument("--phase", choices=("pre", "post"), default="pre")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts" / "codex" / "svp_docs" / "latest")
    parser.add_argument("--approval-receipt", type=Path)
    parser.add_argument("--x1d-receipt", type=Path)
    parser.add_argument("--implementation-change", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_review(
        mode=args.mode,
        phase=args.phase,
        base_ref=args.base_ref,
        output_dir=args.output_dir,
        approval_receipt=args.approval_receipt,
        x1d_receipt=args.x1d_receipt,
        implementation_change=args.implementation_change,
        run_id=args.run_id
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SVP docs X2: {report['x2']['decision']}")
        print(f"SVP docs X1D: {report['x1d']['decision']}")
        print(f"SVP docs X3: {report['x3']['decision']}")
    return 1 if report["x3"]["decision"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
