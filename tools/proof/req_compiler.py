"""Requirements-to-runtime evidence compiler (Install 7 from apps_proof RCA).

This compiler closes the gap that the apps_proof THREAT_MODEL.md flagged
explicitly: passing every harness validator does NOT prove architectural
compliance with the requirements written in ``docs/reference/``. The
compiler:

1. **Walks 12 reference layer dirs** (configurable).
2. **Extracts requirements** from each ``.md`` using MUST / SHALL / MUST
   NOT / SHALL NOT / REQ- markers in headings or text.
3. **Generates a stable REQ_ID** from `(dir_prefix, file_slug, line_no,
   sentence_hash)` so renaming a heading or shifting line numbers within
   a file does NOT invalidate the row.
4. **Attempts evidence linkage** by mechanical heuristics across:
   - ``apps_shared/proof/`` validators / negative controls
   - ``artifacts/runtime/apps_proof/latest/`` runtime artifacts
   - ``tests/`` files matching the layer
5. **Assigns a status** in
   ``{PASS, PARTIAL, MISSING, DOC_ONLY, MOCK_ONLY, FAKE, UNVERIFIED, NOT_APPLICABLE}``.
   Defaults to ``UNVERIFIED`` when the heuristics find no link — this
   honestly reflects "not yet bound to runtime evidence".
6. **Emits two artifacts**:
   - ``artifacts/runtime/req_evidence/latest/requirements_matrix.json``
   - ``artifacts/runtime/req_evidence/latest/requirements_matrix.md``

The CI gate (``ops_scripts/ci/check_req_evidence_matrix.py``) is ADVISORY
in this wave (Install 7 W1) — emits the matrix and surfaces the gap
counts but exits 0. A future wave will flip it to STRICT once enough
requirements have explicit ``REQ_BINDING`` annotations in code/tests
to make the matrix tractable.

The honest first-run output WILL be mostly UNVERIFIED. That's the point:
it surfaces the architectural compliance gap that the harness's local
"all green" masks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[2]

# 12 reference layer dirs (per RCA Install 7 + apps_proof THREAT_MODEL.md §5).
DEFAULT_LAYER_DIRS: tuple[tuple[str, str, str], ...] = (
    # (dir_path, owning_layer, dir_prefix_for_REQ_ID)
    ("docs/reference/00A_L5_Governance_Safety", "L5", "L5G"),
    ("docs/reference/00B_L4_State_Archive_and_UWG", "L4", "L4S"),
    ("docs/reference/00C_Runtime_Gates_Current_Run_Mesh", "Runtime", "RUN"),
    ("docs/reference/01_Request_Intake", "U0", "U0I"),
    ("docs/reference/02_L1_Reasoning_Plan", "L1", "L1P"),
    ("docs/reference/03_L0_Route_Decision_and_L3_Orchestration", "L0L3", "L0L3"),
    ("docs/reference/03A_C0_Context_Engine", "C0", "C0C"),
    ("docs/reference/03B_PA_Prompt_Assembly", "PA", "PAS"),
    ("docs/reference/04_L2_Execute", "L2", "L2E"),
    ("docs/reference/05_Exit_Evaluation_and_Control", "Exit", "EXT"),
    ("docs/reference/06_L6_Observability_and_System_Learning", "L6", "L6S"),
    ("docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance", "E2E", "E2E"),
)


# Status taxonomy (per RCA Install 7).
STATUS_PASS = "PASS"
STATUS_PARTIAL = "PARTIAL"
STATUS_MISSING = "MISSING"
STATUS_DOC_ONLY = "DOC_ONLY"
STATUS_MOCK_ONLY = "MOCK_ONLY"
STATUS_FAKE = "FAKE"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"

ALL_STATUSES = (
    STATUS_PASS,
    STATUS_PARTIAL,
    STATUS_MISSING,
    STATUS_DOC_ONLY,
    STATUS_MOCK_ONLY,
    STATUS_FAKE,
    STATUS_UNVERIFIED,
    STATUS_NOT_APPLICABLE,
)
RELEASE_BLOCKING_STATUSES = (
    STATUS_MISSING,
    STATUS_DOC_ONLY,
    STATUS_MOCK_ONLY,
    STATUS_FAKE,
    STATUS_UNVERIFIED,
)


# Requirement-detection patterns. Case-insensitive on RFC-2119 keywords
# because the doc corpus mixes "MUST" and "must" — both carry the same
# normative weight in this corpus.
_REQ_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bREQ-[A-Z0-9_]+-\d+\b"),  # explicit REQ-XYZ-NNN markers
    re.compile(r"\b(MUST|SHALL|MUST NOT|SHALL NOT)\b", re.IGNORECASE),
)
# Filter ONLY non-content lines: pure separators, table rows, blanks.
# Headings ARE included because the corpus often states requirements
# directly in headings (e.g. "## L1 MUST hold a Plan Contract").
_TRIVIAL_LINE = re.compile(r"^\s*(\||---+\s*$|\s*$)")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Requirement:
    """One extracted requirement row in the matrix."""

    req_id: str
    source_doc: str  # repo-relative path
    source_section: str  # last seen H1/H2/H3 heading, "" if none
    requirement_text: str  # single-line snippet of the requirement
    owning_layer: str
    expected_runtime_artifact: str | None = None
    expected_otel_span: str | None = None
    expected_validator: str | None = None
    expected_negative_control: str | None = None
    expected_test: str | None = None
    actual_runtime_artifact: str | None = None
    actual_otel_span: str | None = None
    actual_validator: str | None = None
    actual_negative_control: str | None = None
    actual_test: str | None = None
    status: str = STATUS_UNVERIFIED
    gap_reason: str = ""
    required_fix: str = ""
    detection_pattern: str = ""  # which regex matched
    line_no: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "req_id": self.req_id,
            "source_doc": self.source_doc,
            "source_section": self.source_section,
            "requirement_text": self.requirement_text,
            "owning_layer": self.owning_layer,
            "expected_runtime_artifact": self.expected_runtime_artifact,
            "expected_otel_span": self.expected_otel_span,
            "expected_validator": self.expected_validator,
            "expected_negative_control": self.expected_negative_control,
            "expected_test": self.expected_test,
            "actual_runtime_artifact": self.actual_runtime_artifact,
            "actual_otel_span": self.actual_otel_span,
            "actual_validator": self.actual_validator,
            "actual_negative_control": self.actual_negative_control,
            "actual_test": self.actual_test,
            "status": self.status,
            "gap_reason": self.gap_reason,
            "required_fix": self.required_fix,
            "detection_pattern": self.detection_pattern,
            "line_no": self.line_no,
        }


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _slug(s: str) -> str:
    """Stable slug from a string — keep alnum + dash, max 24 chars."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return cleaned[:24] if cleaned else "X"


def _stable_req_id(*, dir_prefix: str, file_slug: str, line_no: int, sentence: str) -> str:
    """Generate a stable REQ_ID.

    Format: ``REQ-<DIR>-<FILE>-<LINE6>-<SHA8>``. The line number is
    zero-padded to 6 digits so the ID sorts naturally; the sentence hash
    makes the ID resilient to small wording tweaks (sha8 of canonical-cased
    sentence content).
    """
    canon = re.sub(r"\s+", " ", sentence).strip().lower()
    sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:8]
    return f"REQ-{dir_prefix}-{file_slug}-{line_no:06d}-{sha}"


def _extract_section_headings(lines: list[str]) -> list[tuple[int, str]]:
    """Return (line_no, heading_text) for every '#'-level heading."""
    out: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        m = re.match(r"^(#+)\s+(.+?)\s*$", line)
        if m:
            out.append((i, m.group(2).strip()))
    return out


def _section_for_line(headings: list[tuple[int, str]], line_no: int) -> str:
    """Find the most recent heading at or before line_no."""
    last = ""
    for lh, text in headings:
        if lh <= line_no:
            last = text
        else:
            break
    return last


def _extract_requirements_from_file(
    *,
    doc_path: Path,
    owning_layer: str,
    dir_prefix: str,
    repo_root: Path,
) -> list[Requirement]:
    """Scan a markdown file and return extracted Requirements."""
    try:
        text = doc_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    headings = _extract_section_headings(lines)
    file_slug = _slug(doc_path.stem)
    rel = doc_path.relative_to(repo_root).as_posix()

    out: list[Requirement] = []
    seen_ids: set[str] = set()
    for i, line in enumerate(lines, start=1):
        if _TRIVIAL_LINE.match(line):
            continue
        for pattern in _REQ_PATTERNS:
            if pattern.search(line):
                section = _section_for_line(headings, i)
                req_id = _stable_req_id(
                    dir_prefix=dir_prefix,
                    file_slug=file_slug,
                    line_no=i,
                    sentence=line,
                )
                if req_id in seen_ids:
                    continue
                seen_ids.add(req_id)
                # Truncate requirement_text to keep matrix readable
                snippet = line.strip()
                if len(snippet) > 240:
                    snippet = snippet[:237] + "..."
                out.append(
                    Requirement(
                        req_id=req_id,
                        source_doc=rel,
                        source_section=section,
                        requirement_text=snippet,
                        owning_layer=owning_layer,
                        detection_pattern=pattern.pattern,
                        line_no=i,
                    )
                )
                break  # one pattern match per line is enough
    return out


# ---------------------------------------------------------------------------
# Evidence linkage (heuristic — Wave 1)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Binding rules (Wave 2 — explicit req_bindings.json)
# ---------------------------------------------------------------------------
#
# A *binding rule* declares that a documented requirement is provably
# enforced at runtime by a specific validator + (optional) negative
# control + test + runtime artifact. When a binding rule matches a
# requirement, the requirement's status is upgraded:
#
#   coverage="full"    → STATUS_PASS (subject to runtime_artifact_glob
#                        resolving on disk, if declared)
#   coverage="partial" → STATUS_PARTIAL (with binding-derived actual_*
#                        fields, more honest than keyword heuristics)
#
# Bindings are defined in ``tools/proof/req_bindings.json`` so they can be
# audited and PR-reviewed independently of compiler logic. A binding can
# match by:
#
#   - ``req_id_pattern`` (fnmatch glob against REQ_ID)
#   - ``source_doc_pattern`` (fnmatch glob against repo-relative path)
#   - ``section_pattern`` (fnmatch glob against the most recent heading)
#   - ``line_no_min`` / ``line_no_max`` (inclusive integer range)
#
# When multiple keys are provided on a single binding rule, ALL must
# match (logical AND). Bindings are checked in declaration order; the
# FIRST match wins so put narrow rules before broad ones.

import fnmatch as _fnmatch  # noqa: E402  (intentionally below dataclasses)


@dataclass
class Binding:
    """One req_bindings.json row, post-parse."""

    binding_id: str
    rationale: str
    validator: str | None = None
    negative_control: str | None = None
    test: str | None = None
    runtime_artifact_glob: str | None = None
    coverage: str = "partial"
    # Match keys
    req_id_pattern: str | None = None
    source_doc_pattern: str | None = None
    section_pattern: str | None = None
    line_no_min: int | None = None
    line_no_max: int | None = None

    def matches(self, req: "Requirement") -> bool:
        if self.req_id_pattern and not _fnmatch.fnmatch(req.req_id, self.req_id_pattern):
            return False
        if self.source_doc_pattern and not _fnmatch.fnmatch(req.source_doc, self.source_doc_pattern):
            return False
        if self.section_pattern and not _fnmatch.fnmatch(req.source_section or "", self.section_pattern):
            return False
        if self.line_no_min is not None and req.line_no < self.line_no_min:
            return False
        if self.line_no_max is not None and req.line_no > self.line_no_max:
            return False
        # At least ONE match key must be set — otherwise this rule binds
        # everything, which is almost certainly a config error.
        any_key = any(
            v is not None
            for v in (
                self.req_id_pattern,
                self.source_doc_pattern,
                self.section_pattern,
                self.line_no_min,
                self.line_no_max,
            )
        )
        return any_key


def load_bindings(path: Path) -> list[Binding]:
    """Load and validate ``tools/proof/req_bindings.json`` if it exists.

    Missing file is fine (returns empty list). Malformed JSON or invalid
    rows raise — bindings are auditable contract, not best-effort.
    """
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "bindings" not in raw:
        raise ValueError(f"{path}: expected top-level object with a 'bindings' key")
    out: list[Binding] = []
    for i, row in enumerate(raw["bindings"]):
        if not isinstance(row, dict):
            raise ValueError(f"{path}: bindings[{i}] is not an object")
        coverage = row.get("coverage", "partial")
        if coverage not in {"full", "partial"}:
            raise ValueError(f"{path}: bindings[{i}].coverage must be 'full' or 'partial', got {coverage!r}")
        binding_id = row.get("binding_id") or f"binding_{i}"
        out.append(
            Binding(
                binding_id=str(binding_id),
                rationale=str(row.get("rationale", "")),
                validator=row.get("validator"),
                negative_control=row.get("negative_control"),
                test=row.get("test"),
                runtime_artifact_glob=row.get("runtime_artifact_glob"),
                coverage=coverage,
                req_id_pattern=row.get("req_id_pattern"),
                source_doc_pattern=row.get("source_doc_pattern"),
                section_pattern=row.get("section_pattern"),
                line_no_min=row.get("line_no_min"),
                line_no_max=row.get("line_no_max"),
            )
        )
    return out


def _runtime_artifact_resolves(glob: str | None, repo_root: Path) -> tuple[bool, str | None]:
    """Return (resolved, sample_path) for a runtime_artifact_glob.

    ``glob`` is repo-relative. Resolves to True if at least one file
    matches and is non-empty.
    """
    if not glob:
        return True, None  # no claim made, no claim to falsify
    matches = sorted(repo_root.glob(glob))
    for m in matches:
        try:
            if m.is_file() and m.stat().st_size > 0:
                return True, m.relative_to(repo_root).as_posix()
        except OSError:
            continue
    return False, None


# Layer → expected validator hint mapping. Wave 1 is heuristic; later waves
# can replace this with explicit REQ_BINDING annotations.
_LAYER_VALIDATOR_HINT: dict[str, str] = {
    "U0": "validate_trace_tree (U0 span present)",
    "L1": "validate_trace_tree (L1 span present)",
    "L0L3": "validate_trace_tree (L0/L3 spans present); replay validator (RouteContract)",
    "C0": "validate_replay (FinalEvidenceContract)",
    "PA": "validate_replay (PromptEnvelope)",
    "L2": "validate_replay (SealedArtifact); L2 bounded executor span",
    "Exit": "validate_artifact_inventory (gate verdicts); Exit span",
    "L4": "validate_write_sovereignty (no apps_* writes outside UWG)",
    "L5": "validate_artifact_inventory + write_sovereignty (governance)",
    "L6": "L6 firewall assertion span (apps_eval customizer)",
    "Runtime": "All harness validators in --mode full",
    "E2E": "ops_scripts/ci/check_apps_runtime_proof.py --mode full",
}


def _link_evidence(
    req: Requirement,
    *,
    repo_root: Path,
    bindings: list[Binding] | None = None,
) -> None:
    """Apply evidence linkage.

    Wave 2: explicit ``Binding`` rules from ``tools/proof/req_bindings.json``
    take precedence. A matching ``coverage='full'`` binding flips a row to
    PASS (subject to ``runtime_artifact_glob`` resolving on disk).
    A matching ``coverage='partial'`` binding flips a row to PARTIAL with
    binding-derived ``actual_*`` fields (more honest than keyword bins).

    Wave 1 fallback: if no binding matches, the legacy keyword heuristic
    runs to mark PARTIAL or UNVERIFIED.
    """
    # Expected validator hint based on owning layer
    req.expected_validator = _LAYER_VALIDATOR_HINT.get(req.owning_layer, "no validator binding declared")

    # Wave 2 — explicit binding rules (first-match wins)
    if bindings:
        for b in bindings:
            if not b.matches(req):
                continue
            req.actual_validator = b.validator
            req.actual_negative_control = b.negative_control
            req.actual_test = b.test
            if b.runtime_artifact_glob:
                resolved, sample = _runtime_artifact_resolves(
                    b.runtime_artifact_glob,
                    repo_root,
                )
                req.actual_runtime_artifact = sample or b.runtime_artifact_glob
                if b.coverage == "full" and resolved:
                    req.status = STATUS_PASS
                    req.gap_reason = ""
                    req.required_fix = ""
                    return
                if b.coverage == "full" and not resolved:
                    req.status = STATUS_PARTIAL
                    req.gap_reason = (
                        f"Binding '{b.binding_id}' claims coverage=full but "
                        f"runtime_artifact_glob={b.runtime_artifact_glob!r} "
                        f"did not resolve on disk."
                    )
                    req.required_fix = (
                        "Run the harness that produces this artifact and "
                        "re-run the compiler, OR weaken the binding to "
                        "coverage='partial'."
                    )
                    return
            else:
                # No runtime_artifact_glob declared — coverage='full' is
                # accepted on faith (validator+test+control pinned
                # explicitly by the binding).
                if b.coverage == "full":
                    req.status = STATUS_PASS
                    req.gap_reason = ""
                    req.required_fix = ""
                    return
            # coverage="partial" path
            req.status = STATUS_PARTIAL
            req.gap_reason = f"Binding '{b.binding_id}' claims partial coverage. Rationale: {b.rationale}"
            req.required_fix = (
                f"Promote binding '{b.binding_id}' to coverage='full' "
                "(after writing the validator + negative control + test "
                "that prove this requirement end-to-end), OR add a more "
                "specific binding for this REQ_ID."
            )
            return

    # Heuristic: does the requirement text mention something the harness
    # provably checks? (full-text search of apps_shared/proof/ would be
    # heavier — for Wave 1 we use keyword bins.)
    text_lower = req.requirement_text.lower()

    # Keyword → harness-binding heuristic
    heuristic: list[tuple[str, str]] = []
    if "trace" in text_lower or "span" in text_lower:
        heuristic.append(("validator", "validate_trace_tree"))
    if "hash" in text_lower or "tamper" in text_lower or "integrity" in text_lower:
        heuristic.append(("validator", "validate_artifact_inventory"))
        heuristic.append(("negative_control", "T1_packet_hash_mutation, T6, T9, T10, T11"))
    if "replay" in text_lower or "deterministic" in text_lower or "reproducible" in text_lower:
        heuristic.append(("validator", "validate_replay"))
    if "uwg" in text_lower or "write" in text_lower or "commit" in text_lower:
        heuristic.append(("validator", "validate_write_sovereignty"))
    if "policy" in text_lower or "governance" in text_lower:
        heuristic.append(("validator", "L5 customizer assertion (per-app)"))
    if "evidence" in text_lower or "grounded" in text_lower or "citation" in text_lower:
        heuristic.append(("validator", "C0 grounding assertion"))

    if heuristic:
        # We have at least one heuristic binding — call it PARTIAL.
        actual_validators = "; ".join(v for kind, v in heuristic if kind == "validator")
        actual_controls = "; ".join(v for kind, v in heuristic if kind == "negative_control")
        req.actual_validator = actual_validators or None
        req.actual_negative_control = actual_controls or None
        req.status = STATUS_PARTIAL
        req.gap_reason = (
            "Heuristic keyword match only — no explicit REQ_BINDING annotation. "
            "A future wave should add REQ_BINDING comments in apps_shared/proof/* "
            "that name this REQ_ID."
        )
        req.required_fix = (
            f"Add `# REQ_BINDING: {req.req_id}` comment to the validator(s) and "
            "negative control(s) that prove this requirement at runtime."
        )
    else:
        req.status = STATUS_UNVERIFIED
        req.gap_reason = (
            "No heuristic keyword match between requirement text and any "
            "harness validator. Requirement may need a new validator OR "
            "may already be covered by a validator whose binding isn't "
            "yet declared."
        )
        req.required_fix = (
            f"Triage REQ_ID {req.req_id}: either (a) write a validator + "
            "negative control + REQ_BINDING comment, OR (b) mark "
            "NOT_APPLICABLE with rationale."
        )


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------


@dataclass
class CompilationResult:
    generated_at: str
    repo_root: str
    layer_dirs: list[str]
    requirements: list[Requirement] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "repo_root": self.repo_root,
            "layer_dirs": list(self.layer_dirs),
            "requirements": [r.to_dict() for r in self.requirements],
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, Any]:
        by_status: dict[str, int] = {s: 0 for s in ALL_STATUSES}
        by_layer: dict[str, dict[str, int]] = {}
        for r in self.requirements:
            by_status[r.status] = by_status.get(r.status, 0) + 1
            layer = r.owning_layer
            by_layer.setdefault(layer, {s: 0 for s in ALL_STATUSES})
            by_layer[layer][r.status] = by_layer[layer].get(r.status, 0) + 1
        blocking = sum(by_status.get(s, 0) for s in RELEASE_BLOCKING_STATUSES)
        return {
            "total": len(self.requirements),
            "by_status": by_status,
            "by_layer": by_layer,
            "release_blocking_count": blocking,
        }


def compile_requirements(
    *,
    repo_root: Path = REPO_ROOT,
    layer_dirs: tuple[tuple[str, str, str], ...] = DEFAULT_LAYER_DIRS,
    bindings_path: Path | None = None,
) -> CompilationResult:
    """Walk every layer dir, extract requirements, link evidence.

    Wave 2: ``bindings_path`` defaults to
    ``<repo_root>/tools/proof/req_bindings.json`` if not provided. Pass
    a different path (or a non-existent path) to bypass.
    """
    if bindings_path is None:
        bindings_path = repo_root / "tools" / "proof" / "req_bindings.json"
    bindings = load_bindings(bindings_path)
    out = CompilationResult(
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        repo_root=str(repo_root),
        layer_dirs=[d[0] for d in layer_dirs],
    )
    for rel_dir, owning_layer, dir_prefix in layer_dirs:
        dir_path = repo_root / rel_dir
        if not dir_path.exists():
            continue
        for md in sorted(dir_path.glob("*.md")):
            reqs = _extract_requirements_from_file(
                doc_path=md,
                owning_layer=owning_layer,
                dir_prefix=dir_prefix,
                repo_root=repo_root,
            )
            for req in reqs:
                _link_evidence(req, repo_root=repo_root, bindings=bindings)
                out.requirements.append(req)
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def write_matrix(
    result: CompilationResult,
    *,
    out_dir: Path,
) -> tuple[Path, Path]:
    """Write JSON + Markdown matrix files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "requirements_matrix.json"
    md_path = out_dir / "requirements_matrix.md"

    json_path.write_text(
        json.dumps(result.to_dict(), sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )

    summary = result.summary()
    md: list[str] = [
        "# Requirements-to-Runtime Evidence Matrix",
        "",
        f"- Generated: {result.generated_at}",
        f"- Total requirements: {summary['total']}",
        f"- **Release-blocking**: {summary['release_blocking_count']} "
        f"(status in {list(RELEASE_BLOCKING_STATUSES)})",
        "",
        "## Status totals",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status in ALL_STATUSES:
        md.append(f"| {status} | {summary['by_status'].get(status, 0)} |")
    md.append("")
    md.append("## Per-layer breakdown")
    md.append("")
    md.append("| Layer | Total | " + " | ".join(ALL_STATUSES) + " |")
    md.append("|---|---:|" + "|".join(":---:" for _ in ALL_STATUSES) + "|")
    for layer, counts in sorted(summary["by_layer"].items()):
        layer_total = sum(counts.values())
        cells = [str(counts.get(s, 0)) for s in ALL_STATUSES]
        md.append(f"| {layer} | {layer_total} | " + " | ".join(cells) + " |")
    md.append("")
    md.append("## Sample requirements (first 30)")
    md.append("")
    md.append("| REQ_ID | Layer | Status | Source | Snippet |")
    md.append("|---|---|---|---|---|")
    for r in result.requirements[:30]:
        snippet = r.requirement_text.replace("|", "\\|")[:120]
        md.append(
            f"| `{r.req_id}` | {r.owning_layer} | {r.status} | `{r.source_doc}:{r.line_no}` | {snippet} |"
        )
    md.append("")
    md.append("## How to close gaps")
    md.append("")
    md.append("Every UNVERIFIED / PARTIAL / MISSING / DOC_ONLY / MOCK_ONLY / FAKE row needs ONE of:")
    md.append("")
    md.append(
        "1. **Real binding**: add a `# REQ_BINDING: <REQ_ID>` comment to the validator + negative control + test that proves it at runtime. The next compiler pass will detect the binding and upgrade the row to PASS."
    )
    md.append(
        "2. **Explicit NOT_APPLICABLE**: the requirement is documentation-only and has no runtime obligation. Add a `NOT_APPLICABLE` annotation with rationale in `tools/proof/req_compiler_overrides.json` (created on demand)."
    )
    md.append("")
    md.append("## Honest first-pass note")
    md.append("")
    md.append(
        "This Wave 1 compiler uses keyword heuristics, not explicit REQ_BINDINGs. Most rows will be UNVERIFIED or PARTIAL — that's the correct first signal. The number going down over time is the metric to track."
    )

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile requirements-to-runtime evidence matrix",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "runtime" / "req_evidence" / "latest",
        help="Output directory for matrix files",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any row is in release-blocking status",
    )
    args = parser.parse_args(argv)

    print("Compiling requirements-evidence matrix...")
    result = compile_requirements()
    json_path, md_path = write_matrix(result, out_dir=args.out_dir)
    summary = result.summary()
    print(f"  total requirements: {summary['total']}")
    print(f"  release-blocking: {summary['release_blocking_count']}")
    print(f"  by_status: {summary['by_status']}")
    print(f"  matrix JSON: {json_path}")
    print(f"  matrix MD:   {md_path}")

    if args.strict and summary["release_blocking_count"] > 0:
        print(
            f"FAIL — {summary['release_blocking_count']} requirements in {list(RELEASE_BLOCKING_STATUSES)}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
