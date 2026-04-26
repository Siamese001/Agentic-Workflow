"""Generate `agentic_core/L5_safety/contracts/` from the doctrine outputs.

Produces:
  agentic_core/L5_safety/contracts/
    __init__.py
    _base.py
    _vocab.py
    parent.py            (00_L5_Governance_Safety)
    enforcement.py       (00.1)
    authority.py         (00.2)
    origin.py            (00.3)
    hitl.py              (00.4)
    egress.py            (00.5)
    replay.py            (00.6)
    static.py            (00.7)
    registry.py

Every named output in the 8 L5 doctrine docs becomes a frozen dataclass
inheriting from a kind-specific base in `_base.py`. The registry exposes
``CONTRACT_REGISTRY: dict[str, type]`` covering all 736 outputs.

Re-runnable. Idempotent (overwrites generated files).
"""

from __future__ import annotations

import json
import pathlib
import re
import textwrap
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[2]
JSON_PATH = REPO / "tools" / "l5_contracts" / "_l5_outputs.json"
STATUS_ENUMS_JSON = REPO / "tools" / "l5_contracts" / "_l5_status_enums.json"
PKG_DIR = REPO / "agentic_core" / "L5_safety" / "contracts"


def to_enum_class_name(field_name: str) -> str:
    """``classification_status`` -> ``ClassificationStatus``."""
    return "".join(part.capitalize() for part in field_name.split("_"))


# Map doc filename → module name in `contracts/`
DOC_TO_MODULE: dict[str, str] = {
    "00A_L5_Governance_Safety_detailed.md": "parent",
    "00A.1_L5_Safety_Enforcement_Plane_detailed.md": "enforcement",
    "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md": "authority",
    "00A.3_L5_Origin_Trust_and_Content_Boundary_detailed.md": "origin",
    "00A.4_L5_HITL_Reclearance_Human_Input_Gov.md": "hitl",
    "00A.5_L5_Egress_and_Provider_Governance_detailed.md": "egress",
    "00A.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md": "replay",
    "00A.7_L5_Static_Governance_and_Structure_Drift_detailed.md": "static",
    "00A.8_L5_Runtime_Certification_Binding.md": "runtime_binding",
}

# Suffix → base class
SNAKE_SUFFIX_TO_BASE: dict[str, str] = {
    "packet": "L5Packet",
    "receipt": "L5Receipt",
    "report": "L5Report",
    "manifest": "L5Manifest",
    "log": "L5Log",
    "diff": "L5Diff",
    "envelope": "L5Envelope",
    "result": "L5Result",
    "map": "L5Map",
    "status": "L5Status",
    "ref": "L5Ref",
}

PASCAL_SUFFIX_TO_BASE: dict[str, str] = {
    "Packet": "L5Packet",
    "Receipt": "L5Receipt",
    "Report": "L5Report",
    "Manifest": "L5Manifest",
    "Result": "L5Result",
    "Diff": "L5Diff",
    "Envelope": "L5Envelope",
    "Map": "L5Map",
    "Log": "L5Log",
    "Context": "L5Context",
    "Token": "L5Token",
}


def snake_suffix(name: str) -> str | None:
    parts = name.rsplit("_", 1)
    if len(parts) == 2 and parts[1] in SNAKE_SUFFIX_TO_BASE:
        return parts[1]
    return None


def pascal_suffix(name: str) -> str | None:
    for suf in PASCAL_SUFFIX_TO_BASE:
        if name.endswith(suf):
            return suf
    return None


def to_class_name(name: str) -> str:
    """snake_case → PascalCase; PascalCase → unchanged."""
    if name[0].isupper():
        return name
    return "".join(part.capitalize() for part in name.split("_"))


def base_for(name: str) -> str:
    if name[0].isupper():
        suf = pascal_suffix(name)
        if suf is None:
            return "L5OutputBase"
        return PASCAL_SUFFIX_TO_BASE[suf]
    suf = snake_suffix(name)
    if suf is None:
        return "L5OutputBase"
    return SNAKE_SUFFIX_TO_BASE[suf]


def kind_for(name: str) -> str:
    if name[0].isupper():
        suf = pascal_suffix(name)
        return (suf or "Output").lower()
    suf = snake_suffix(name)
    return suf or "output"


def build_assignment_map(
    mapping: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Group doctrine output names by Python class name and module.

    Two doctrine forms can collapse to one Python class — for example,
    ``ModelEgressReceipt`` (PascalCase) and ``model_egress_receipt``
    (snake_case) both render to ``ModelEgressReceipt``. They become a
    single class whose ``output_names`` ClassVar lists both doctrine
    names, and the registry maps both keys to that single class.

    Returns:
        per_module_classes: module_name -> sorted list of class names
            owned by that module.
        class_to_names: class_name -> sorted tuple of doctrine names that
            collapse to this class. Module assignment uses the
            first-seen doc (in DOC_TO_MODULE order).
    """
    # name -> first-seen doc (in DOC_TO_MODULE order)
    name_to_doc: dict[str, str] = {}
    for doc_filename in DOC_TO_MODULE:
        for name in mapping.get(doc_filename, []):
            name_to_doc.setdefault(name, doc_filename)

    # class_name -> set of doctrine names
    class_to_name_set: dict[str, set[str]] = {}
    # class_name -> first-seen doc filename (drives module assignment)
    class_to_doc: dict[str, str] = {}
    for doc_filename in DOC_TO_MODULE:
        for name in mapping.get(doc_filename, []):
            cls = to_class_name(name)
            class_to_name_set.setdefault(cls, set()).add(name)
            class_to_doc.setdefault(cls, doc_filename)

    class_to_names: dict[str, list[str]] = {cls: sorted(names) for cls, names in class_to_name_set.items()}

    per_module_classes: dict[str, list[str]] = {m: [] for m in DOC_TO_MODULE.values()}
    for cls, doc_filename in class_to_doc.items():
        per_module_classes[DOC_TO_MODULE[doc_filename]].append(cls)
    for m in per_module_classes:
        per_module_classes[m].sort()
    return per_module_classes, class_to_names


# ---------------------------------------------------------------------------
# Static module bodies
# ---------------------------------------------------------------------------

BASE_PY = '''"""Base dataclasses for L5 doctrine output contracts.

Every named L5 output (packet / receipt / report / manifest / log / diff /
envelope / result / map / status / ref / context / token) defined in the
8 doctrine documents under ``docs/reference/00_L5_Policy_Plane`` is
implemented as a frozen dataclass that inherits from one of the bases
below.

L5 doctrine forbids these contracts from carrying runtime dispositions
(ALLOW / DENY / REROUTE / etc.). They carry **evidence** only. Downstream
consumers (Runtime Gates, Exit Eval, UWG, L6) decide live outcomes.

Generated and re-runnable. Do not hand-edit individual contract modules
(parent.py, enforcement.py, ..., static.py) — re-run
``python tools/l5_contracts/generate_contracts.py`` instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping

# Empty mapping default — produced fresh per instance via default_factory.
# ``dict`` is mutable, but doctrine treats payload contents as
# read-after-emission. Callers must not mutate after construction.


@dataclass(frozen=True, slots=True)
class L5OutputBase:
    """Doctrine-level common envelope for every L5 output.

    Carries evidence only — never runtime disposition.
    """

    run_id: str = ""
    trace_id: str = ""
    emitted_at_utc: str = ""
    digest_sha256: str = ""

    output_name: ClassVar[str] = ""
    source_doc: ClassVar[str] = ""
    output_kind: ClassVar[str] = "output"

    def is_evidence_only(self) -> bool:
        """L5 contracts are evidence-only by doctrine."""
        return True


@dataclass(frozen=True, slots=True)
class L5Packet(L5OutputBase):
    """Bundle of evidence fields for a single L5 concern."""

    payload: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class L5Receipt(L5OutputBase):
    """Confirmation that an L5 step executed and produced bound evidence."""

    receipt_status: str = ""
    evidence_refs: tuple[str, ...] = ()
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class L5Report(L5OutputBase):
    """Findings from an L5 scan or evaluation. Severity-graded."""

    severity: str = "info"
    findings: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class L5Manifest(L5OutputBase):
    """Enumerated set of items bound under one L5 evidence header."""

    entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "manifest"


@dataclass(frozen=True, slots=True)
class L5Log(L5OutputBase):
    """Hash-chained sequence of L5 events. ``prev_hash`` chains entries."""

    prev_hash: str = ""
    entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "log"


@dataclass(frozen=True, slots=True)
class L5Diff(L5OutputBase):
    """Before/after delta evidence between two L5 snapshots or artifacts."""

    before_ref: str = ""
    after_ref: str = ""
    diff_entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class L5Envelope(L5OutputBase):
    """Sealed wrapper around evidence contents with a hash seal."""

    contents_ref: str = ""
    seal_hash: str = ""
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class L5Result(L5OutputBase):
    """L5 certification outcome. Status + reason_codes + evidence_refs."""

    certification_status: str = ""
    reason_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    output_kind: ClassVar[str] = "result"


@dataclass(frozen=True, slots=True)
class L5Map(L5OutputBase):
    """Key→value evidence index (e.g., affected consumer surfaces)."""

    entries: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class L5Status(L5OutputBase):
    """Single-state evidence marker (e.g., readiness status)."""

    status_value: str = ""
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class L5Ref(L5OutputBase):
    """Pointer-style reference to externally stored evidence."""

    ref_uri: str = ""
    ref_kind: str = ""
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class L5Context(L5OutputBase):
    """Bound governance context object (e.g., GovernedValidationContext)."""

    payload: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "context"


@dataclass(frozen=True, slots=True)
class L5Token(L5OutputBase):
    """Capability-style scoped token evidence (issuance shape only)."""

    token_value: str = ""
    scope: tuple[str, ...] = ()
    expires_at_utc: str = ""
    output_kind: ClassVar[str] = "token"


__all__ = [
    "L5OutputBase",
    "L5Packet",
    "L5Receipt",
    "L5Report",
    "L5Manifest",
    "L5Log",
    "L5Diff",
    "L5Envelope",
    "L5Result",
    "L5Map",
    "L5Status",
    "L5Ref",
    "L5Context",
    "L5Token",
]
'''

VOCAB_PY = '''"""Controlled vocabularies pulled from L5 doctrine parent (00).

These are evidence/certification terms only. They never represent runtime
dispositions (per parent ``00_L5_Governance_Safety_detailed.md``).
"""
from __future__ import annotations

from enum import Enum


class L5CertificationStatus(str, Enum):
    """Top-level certification status set defined by the L5 parent doc."""

    L5_CERTIFIED = "L5_CERTIFIED"
    L5_NOT_CERTIFIED = "L5_NOT_CERTIFIED"
    L5_REQUIRES_RECLEARANCE = "L5_REQUIRES_RECLEARANCE"
    L5_REQUIRES_REMEDIATION_EVIDENCE = "L5_REQUIRES_REMEDIATION_EVIDENCE"
    L5_REQUIRES_HUMAN_REVIEW_PACKET = "L5_REQUIRES_HUMAN_REVIEW_PACKET"
    L5_INCIDENT_EVIDENCE_REQUIRED = "L5_INCIDENT_EVIDENCE_REQUIRED"
    L5_STATIC_VIOLATION_EVIDENCE = "L5_STATIC_VIOLATION_EVIDENCE"
    L5_AUTHORITY_GAP_EVIDENCE = "L5_AUTHORITY_GAP_EVIDENCE"
    L5_EGRESS_GAP_EVIDENCE = "L5_EGRESS_GAP_EVIDENCE"
    L5_REPLAY_AUDIT_GAP_EVIDENCE = "L5_REPLAY_AUDIT_GAP_EVIDENCE"


class L5ReasonCode(str, Enum):
    """Reason codes attached to certification results."""

    POLICY_VIOLATION_EVIDENCE = "policy_violation_evidence"
    HARD_CONSTRAINT_BREACH_EVIDENCE = "hard_constraint_breach_evidence"
    MISSING_AUTHORITY_EVIDENCE = "missing_authority_evidence"
    REGISTRY_MISMATCH_EVIDENCE = "registry_mismatch_evidence"
    ROUTE_MISMATCH_EVIDENCE = "route_mismatch_evidence"
    INJECTION_EVIDENCE = "injection_evidence"
    CONTEXT_BLEED_EVIDENCE = "context_bleed_evidence"
    CROSS_TENANT_RISK_EVIDENCE = "cross_tenant_risk_evidence"
    DATA_SENSITIVITY_RISK_EVIDENCE = "data_sensitivity_risk_evidence"
    EVIDENCE_WEAK_SIGNAL = "evidence_weak_signal"
    GROUNDEDNESS_REQUIRED_SIGNAL = "groundedness_required_signal"
    HUMAN_REVIEW_REQUIRED_SIGNAL = "human_review_required_signal"
    SANDBOX_INSUFFICIENT_EVIDENCE = "sandbox_insufficient_evidence"
    REPLAY_INCOMPLETE_EVIDENCE = "replay_incomplete_evidence"
    PROVIDER_MISMATCH_EVIDENCE = "provider_mismatch_evidence"
    TOOL_SCHEMA_MISMATCH_EVIDENCE = "tool_schema_mismatch_evidence"
    CONNECTOR_SCOPE_MISMATCH_EVIDENCE = "connector_scope_mismatch_evidence"
    BUDGET_RISK_EVIDENCE = "budget_risk_evidence"
    DRIFT_EVIDENCE = "drift_evidence"


class L5EvidenceRefKind(str, Enum):
    """Canonical evidence reference categories surfaced in certifications."""

    AUTHORITY_CONTEXT = "authority_context_evidence_ref"
    ORIGIN_TRUST = "origin_trust_evidence_ref"
    STATIC_GOVERNANCE = "static_governance_evidence_ref"
    EGRESS_CERTIFICATION = "egress_certification_evidence_ref"
    HUMAN_RECLEARANCE = "human_reclearance_evidence_ref"
    REPLAY_AUDIT = "replay_audit_evidence_ref"
    CERTIFICATION_GAP = "certification_gap_evidence_ref"


# Forbidden runtime-disposition tokens that L5 contracts must never emit.
FORBIDDEN_RUNTIME_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "CLARIFY",
        "ABSTAIN",
        "REROUTE",
        "SHRINK_SCOPE",
        "RETRY",
        "HEAL",
        "ESCALATE_HITL",
        "QUARANTINE",
        "REDACT",
        "SAFE_FALLBACK",
        "MARK_DEGRADED",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
        "downstream_disposition",
        "allow_l2_execution",
        "allow_model_call",
        "allow_tool_call",
        "allow_connector_call",
        "require_HITL",
        "require_UWG_commit_review",
        "incident_lockdown",
    }
)


__all__ = [
    "L5CertificationStatus",
    "L5ReasonCode",
    "L5EvidenceRefKind",
    "FORBIDDEN_RUNTIME_DISPOSITIONS",
]
'''


def render_module(
    module_name: str,
    doc_filename: str,
    class_names: list[str],
    class_to_names: dict[str, list[str]],
    status_enums: dict[str, list[str]],
) -> str:
    """Render a single contracts module."""
    # Find which status enum imports this module needs (only L5Status
    # subclasses whose canonical doctrine name has a value set).
    needed_enums: list[str] = []
    for cls_name in class_names:
        names = class_to_names[cls_name]
        canonical = cls_name if cls_name in names else names[0]
        if base_for(canonical) == "L5Status" and canonical in status_enums:
            needed_enums.append(to_enum_class_name(canonical))
    enum_import = ""
    if needed_enums:
        enum_import = (
            "from ._status_enums import (\n"
            + "".join(f"    {e},\n" for e in sorted(set(needed_enums)))
            + ")\n"
        )

    header = f'''"""Generated L5 contract dataclasses for ``{doc_filename}``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/{doc_filename}``
Module: ``agentic_core.L5_safety.contracts.{module_name}``
Generated count: {len(class_names)} contracts

Every class below is an evidence-only frozen dataclass. L5 contracts must
not emit runtime dispositions. See ``_base.py`` for the kind hierarchy,
``_vocab.py`` for the controlled vocabularies, and ``_status_enums.py``
for per-status field value sets.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from ._base import (
    L5OutputBase,
    L5Packet,
    L5Receipt,
    L5Report,
    L5Manifest,
    L5Log,
    L5Diff,
    L5Envelope,
    L5Result,
    L5Map,
    L5Status,
    L5Ref,
    L5Context,
    L5Token,
)
{enum_import}

'''
    from tqdm import tqdm  # progress per Constitutional §16

    bodies: list[str] = []
    for cls_name in tqdm(class_names, desc=f"Rendering {module_name}", unit="cls"):
        if not cls_name.isidentifier():
            raise ValueError(f"non-identifier class name: {cls_name!r}")
        names = class_to_names[cls_name]
        # Pick the canonical doctrine name: prefer PascalCase if the class
        # name itself appears in the doctrine; else the first sorted name.
        canonical = cls_name if cls_name in names else names[0]
        base = base_for(canonical)
        kind = kind_for(canonical)
        names_literal = ", ".join(f'"{n}"' for n in names)

        # Status subclass with a doctrine value set: bind the enum and
        # expose it as a ClassVar for matrix tooling.
        status_block = ""
        if base == "L5Status" and canonical in status_enums:
            enum_cls = to_enum_class_name(canonical)
            values = status_enums[canonical]
            values_literal = ", ".join(f'"{v}"' for v in values)
            status_block = textwrap.dedent(
                f"""
                allowed_values: ClassVar[tuple[str, ...]] = ({values_literal},)
                value_enum: ClassVar[type] = {enum_cls}

                def __post_init__(self) -> None:
                    if self.status_value and self.status_value not in self.allowed_values:
                        raise ValueError(
                            f"{{type(self).__name__}}.status_value={{self.status_value!r}} "
                            f"not in doctrine value set {{self.allowed_values!r}}"
                        )
                """
            ).rstrip()
            # Indent every line by 4 spaces (inside the class body).
            status_block = "\n".join(("    " + line) if line else "" for line in status_block.splitlines())

        body = textwrap.dedent(
            f'''\
            @dataclass(frozen=True, slots=True)
            class {cls_name}({base}):
                """L5 doctrine output ``{canonical}`` (kind={kind}).

                Source doctrine: ``{doc_filename}``.
                Canonical doctrine names: {", ".join(names)}.
                """

                output_name: ClassVar[str] = "{canonical}"
                output_names: ClassVar[tuple[str, ...]] = ({names_literal},)
                source_doc: ClassVar[str] = "{doc_filename}"
                output_kind: ClassVar[str] = "{kind}"
            '''
        )
        if status_block:
            body = body + status_block + "\n\n\n"
        else:
            body = body + "\n\n"
        bodies.append(body)

    all_block = "__all__ = [\n" + "".join(f'    "{n}",\n' for n in class_names) + "]\n"
    return header + "".join(bodies) + all_block


def render_status_enums(status_enums: dict[str, list[str]]) -> str:
    """Render ``_status_enums.py`` — one ``StrEnum`` per doctrine status
    field, plus a ``STATUS_ENUM_REGISTRY`` mapping field name -> enum.
    """
    header = '''"""Generated per-status enum value sets from L5 doctrine.

Each `<x>_status = a | b | c` declaration in `docs/reference/00_L5_Policy_Plane/`
becomes a ``StrEnum`` here. The corresponding ``L5Status`` subclass in
``parent.py`` / ``enforcement.py`` / ... validates ``status_value``
against ``allowed_values`` (also exposed as a ``ClassVar``).

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Final


'''
    bodies: list[str] = []
    registry_entries: list[str] = []
    all_names: list[str] = []
    for field_name in sorted(status_enums):
        values = status_enums[field_name]
        enum_cls = to_enum_class_name(field_name)
        all_names.append(enum_cls)
        body_lines = [f"class {enum_cls}(StrEnum):"]
        body_lines.append(f'    """Doctrine value set for ``{field_name}``.')
        body_lines.append(f"    Source: ``docs/reference/00_L5_Policy_Plane/`` ({len(values)} values).")
        body_lines.append('    """')
        for v in values:
            # Python attr name: uppercase, valid identifier.
            attr = v.upper()
            body_lines.append(f'    {attr} = "{v}"')
        body_lines.append("")
        body_lines.append("")
        bodies.append("\n".join(body_lines))
        registry_entries.append(f'    "{field_name}": {enum_cls},')

    registry_block = (
        "STATUS_ENUM_REGISTRY: Final[dict[str, type[StrEnum]]] = {\n"
        + "\n".join(registry_entries)
        + "\n}\n\n"
    )
    all_block = (
        "__all__ = [\n"
        + "".join(f'    "{n}",\n' for n in all_names)
        + '    "STATUS_ENUM_REGISTRY",\n'
        + "]\n"
    )
    return header + "\n".join(bodies) + registry_block + all_block


def render_registry(
    per_module_classes: dict[str, list[str]],
    class_to_names: dict[str, list[str]],
) -> str:
    """Render the contract registry mapping output_name -> class."""
    header = '''"""Generated registry of every L5 doctrine output contract.

``CONTRACT_REGISTRY`` maps the canonical output name (as written in the
doctrine docs, snake_case or PascalCase exactly) to its dataclass type.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""
from __future__ import annotations

from typing import Final

from ._base import L5OutputBase

'''
    imports: list[str] = []
    entries: list[str] = []
    for module_name in DOC_TO_MODULE.values():
        cls_list = per_module_classes.get(module_name, [])
        if not cls_list:
            continue
        imports.append(f"from .{module_name} import (\n" + "".join(f"    {c},\n" for c in cls_list) + ")\n")
        for c in cls_list:
            for n in class_to_names[c]:
                entries.append(f'    "{n}": {c},\n')

    body = (
        "".join(imports)
        + "\n"
        + "CONTRACT_REGISTRY: Final[dict[str, type[L5OutputBase]]] = {\n"
        + "".join(entries)
        + "}\n\n"
        + "ALL_OUTPUT_NAMES: Final[frozenset[str]] = frozenset(CONTRACT_REGISTRY.keys())\n\n"
        + "def get_contract(name: str) -> type[L5OutputBase]:\n"
        + '    """Lookup contract class by canonical doctrine name. Raises KeyError."""\n'
        + "    return CONTRACT_REGISTRY[name]\n\n"
        + '__all__ = ["CONTRACT_REGISTRY", "ALL_OUTPUT_NAMES", "get_contract"]\n'
    )
    return header + body


def render_init() -> str:
    return '''"""L5 doctrine output contracts.

Every named output across the 8 ``docs/reference/00_L5_Policy_Plane``
docs is a frozen dataclass here. Use ``CONTRACT_REGISTRY`` to lookup
a contract by its canonical doctrine name.

Constitutional discipline: contracts are evidence-only. They never
encode runtime dispositions (ALLOW/DENY/REROUTE/etc.).

Sub-modules:

* ``_base`` — kind hierarchy (``L5Packet``, ``L5Receipt``, etc.)
* ``_vocab`` — controlled vocabularies (statuses, reason codes)
* ``parent`` — outputs from ``00_L5_Governance_Safety_detailed.md``
* ``enforcement`` — outputs from ``00.1`` Safety Enforcement Plane
* ``authority`` — outputs from ``00.2`` Authority Context & Registry
* ``origin`` — outputs from ``00.3`` Origin Trust & Content Boundary
* ``hitl`` — outputs from ``00.4`` HITL Reclearance
* ``egress`` — outputs from ``00.5`` Egress & Provider Governance
* ``replay`` — outputs from ``00.6`` Replay/Audit/Certification Evidence
* ``static`` — outputs from ``00.7`` Static Governance & Structure Drift
* ``registry`` — name lookup table
"""
from __future__ import annotations

from ._base import (
    L5OutputBase,
    L5Packet,
    L5Receipt,
    L5Report,
    L5Manifest,
    L5Log,
    L5Diff,
    L5Envelope,
    L5Result,
    L5Map,
    L5Status,
    L5Ref,
    L5Context,
    L5Token,
)
from ._vocab import (
    L5CertificationStatus,
    L5ReasonCode,
    L5EvidenceRefKind,
    FORBIDDEN_RUNTIME_DISPOSITIONS,
)
from .registry import (
    CONTRACT_REGISTRY,
    ALL_OUTPUT_NAMES,
    get_contract,
)
from ._status_enums import STATUS_ENUM_REGISTRY

__all__ = [
    "L5OutputBase",
    "L5Packet",
    "L5Receipt",
    "L5Report",
    "L5Manifest",
    "L5Log",
    "L5Diff",
    "L5Envelope",
    "L5Result",
    "L5Map",
    "L5Status",
    "L5Ref",
    "L5Context",
    "L5Token",
    "L5CertificationStatus",
    "L5ReasonCode",
    "L5EvidenceRefKind",
    "FORBIDDEN_RUNTIME_DISPOSITIONS",
    "CONTRACT_REGISTRY",
    "ALL_OUTPUT_NAMES",
    "get_contract",
    "STATUS_ENUM_REGISTRY",
]
'''


def main() -> None:
    mapping: dict[str, list[str]] = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    per_module_classes, class_to_names = build_assignment_map(mapping)
    PKG_DIR.mkdir(parents=True, exist_ok=True)

    # Load doctrine status enums (run extract_status_enums.py first if missing).
    status_enums: dict[str, list[str]] = {}
    if STATUS_ENUMS_JSON.exists():
        payload = json.loads(STATUS_ENUMS_JSON.read_text(encoding="utf-8"))
        status_enums = payload.get("enums", {})
        print(f"  Loaded {len(status_enums)} per-status enum value sets.")
    else:
        print(
            f"  WARNING: {STATUS_ENUMS_JSON.relative_to(REPO)} missing; "
            f"run extract_status_enums.py to enable per-field validation."
        )

    (PKG_DIR / "_base.py").write_text(BASE_PY, encoding="utf-8")
    (PKG_DIR / "_vocab.py").write_text(VOCAB_PY, encoding="utf-8")
    (PKG_DIR / "_status_enums.py").write_text(render_status_enums(status_enums), encoding="utf-8")

    total_classes = 0
    total_names = 0
    for doc_filename, module_name in DOC_TO_MODULE.items():
        cls_list = per_module_classes[module_name]
        text = render_module(module_name, doc_filename, cls_list, class_to_names, status_enums)
        (PKG_DIR / f"{module_name}.py").write_text(text, encoding="utf-8")
        names_count = sum(len(class_to_names[c]) for c in cls_list)
        total_classes += len(cls_list)
        total_names += names_count
        print(f"  {module_name}.py: {len(cls_list)} classes / {names_count} doctrine names")

    (PKG_DIR / "registry.py").write_text(
        render_registry(per_module_classes, class_to_names), encoding="utf-8"
    )
    (PKG_DIR / "__init__.py").write_text(render_init(), encoding="utf-8")
    print(
        f"Wrote {PKG_DIR.relative_to(REPO)} \u2014 "
        f"{total_classes} classes covering {total_names} doctrine names "
        f"with {len(status_enums)} bound status enums"
    )


if __name__ == "__main__":
    main()
