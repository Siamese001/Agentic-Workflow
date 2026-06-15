"""
Canonical constants for the requirements proof system.

The 12 source folders below are the SOLE authoritative inputs. Older flat
files in ``docs/reference/`` outside these 12 folders are NOT authoritative
and MUST NOT be silently substituted — see the user request "do not use
older flat files in docs/reference unless they are inside one of the
folders above".
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

# Resolve repo root from this file's location:
#   agentic_core/runtime/prove_requirements/constants.py
#   parents[0] = prove_requirements/
#   parents[1] = runtime/
#   parents[2] = agentic_core/
#   parents[3] = repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[3]

# The 12 canonical source folders, in the exact order specified by the user.
SOURCE_FOLDERS: Tuple[str, ...] = (
    "docs/reference/06_L6_Observability_and_System_Learning",
    "docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance",
    "docs/reference/00A_L5_Governance_Safety",
    "docs/reference/00B_L4_State_Archive_and_UWG",
    "docs/reference/00C_Runtime_Gates_Current_Run_Mesh",
    "docs/reference/01_Request_Intake",
    "docs/reference/02_L1_Reasoning_Plan",
    "docs/reference/03_L0_Route_Decision",
    "docs/reference/03A_C0_Context_Engine",
    "docs/reference/03B_PA_Prompt_Assembly",
    "docs/reference/04_L2_Execute",
    "docs/reference/05_Exit_Evaluation_and_Control",
)

# Ingestible suffixes per the spec.
INGESTIBLE_SUFFIXES: Tuple[str, ...] = (
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
)

# Excluded directory names anywhere in the path.
EXCLUDED_DIRNAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
    }
)

# Excluded path fragments (POSIX-form match).
EXCLUDED_PATH_FRAGMENTS: Tuple[str, ...] = (
    "artifacts/runtime/requirements_proof",
)

# Excluded file suffixes (case-insensitive).
EXCLUDED_FILE_SUFFIXES: Tuple[str, ...] = (".tmp", ".bak")

# Folder name -> owning layer/stage. Folder name is the leaf directory of
# each entry in SOURCE_FOLDERS (e.g. "00A_L5_Governance_Safety").
FOLDER_TO_LAYER = {
    "00A_L5_Governance_Safety": "L5",
    "00B_L4_State_Archive_and_UWG": "L4",
    "00C_Runtime_Gates_Current_Run_Mesh": "RuntimeGates",
    "01_Request_Intake": "U0",
    "02_L1_Reasoning_Plan": "L1",
    "03_L0_Route_Decision": "L0",
    "03A_C0_Context_Engine": "C0",
    "03B_PA_Prompt_Assembly": "PA",
    "04_L2_Execute": "L2",
    "05_Exit_Evaluation_and_Control": "Exit",
    "06_L6_Observability_and_System_Learning": "L6",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "CrossCutting",
}

# C0 sub-stage prefixes (filename starts with these).
C0_SUBSTAGES: Tuple[str, ...] = (
    "C0.0",
    "C0.1",
    "C0.2",
    "C0.3",
    "C0.4",
    "C0.5",
    "C0.6",
    "C0.7",
)

# L3 sub-stage filename prefixes inside the L0/L3 folder.
L3_FILENAME_PREFIXES: Tuple[str, ...] = (
    "03.6",
    "03.7",
    "03.8",
    "03.9",
)

# ---------------------------------------------------------------------------
# Normative requirement detection patterns.
#
# The user spec lists a mixed set of strong and weak markers. We compile them
# with explicit word boundaries to avoid false positives (e.g. "gate" should
# not match "navigate"). Single-line normative requirements are detected by
# the presence of any pattern below.
# ---------------------------------------------------------------------------

NORMATIVE_PATTERNS: Tuple[Tuple["re.Pattern[str]", str], ...] = (
    # Strong markers — case-sensitive.
    (re.compile(r"\bMUST NOT\b"), "MUST_NOT"),
    (re.compile(r"\bMUST\b"), "MUST"),
    (re.compile(r"\bREQUIRED\b"), "REQUIRED"),
    (re.compile(r"\bHARD LAW\b"), "HARD_LAW"),
    (re.compile(r"\bHARD NO\b"), "HARD_NO"),
    (re.compile(r"\bNEVER\b"), "NEVER"),
    (re.compile(r"\bDO NOT\b"), "DO_NOT"),
    (re.compile(r"\bDOES NOT\b"), "DOES_NOT"),
    (re.compile(r"\bFORBIDDEN\b"), "FORBIDDEN"),
    (re.compile(r"\bCANNOT\b"), "CANNOT_STRONG"),
    (re.compile(r"\bBLOCKED\b"), "BLOCKED_STRONG"),
    # Weak markers — case-insensitive.
    (re.compile(r"\binvariant\b", re.IGNORECASE), "invariant"),
    (re.compile(r"\bacceptance criteria\b", re.IGNORECASE), "acceptance_criteria"),
    (re.compile(r"\bdone criteria\b", re.IGNORECASE), "done_criteria"),
    (re.compile(r"\boutput contract\b", re.IGNORECASE), "output_contract"),
    (re.compile(r"\binput contract\b", re.IGNORECASE), "input_contract"),
    (re.compile(r"\bgate\b", re.IGNORECASE), "gate"),
    (re.compile(r"\bfail conditions?\b", re.IGNORECASE), "fail_condition"),
    (re.compile(r"\bfails? closed\b", re.IGNORECASE), "fail_closed"),
    (re.compile(r"\breplay must prove\b", re.IGNORECASE), "replay_must_prove"),
    (re.compile(r"\bOTEL\b"), "OTEL"),
    (re.compile(r"\bOpenTelemetry\b", re.IGNORECASE), "OpenTelemetry"),
    (re.compile(r"\btest requirements?\b", re.IGNORECASE), "test_requirements"),
    (re.compile(r"\brequired attributes?\b", re.IGNORECASE), "required_attributes"),
    (re.compile(r"\bno direct\b", re.IGNORECASE), "no_direct"),
    (re.compile(r"\bsole durable write path\b", re.IGNORECASE), "sole_durable_write_path"),
    (re.compile(r"\bexactly one\b", re.IGNORECASE), "exactly_one"),
    (re.compile(r"\bcannot\b", re.IGNORECASE), "cannot_weak"),
    (re.compile(r"\bblocked\b", re.IGNORECASE), "blocked_weak"),
    (re.compile(r"\bshall not\b", re.IGNORECASE), "shall_not"),
    (re.compile(r"\bshall never\b", re.IGNORECASE), "shall_never"),
    (re.compile(r"\banti[-\s]?bypass\b", re.IGNORECASE), "anti_bypass"),
    (re.compile(r"\bnegative test\b", re.IGNORECASE), "negative_test_marker"),
)


# ---------------------------------------------------------------------------
# Requirement type classification rules — applied in order; first match wins.
#
# These map a matched line to one of the requirement_type values listed in
# the user spec: contract|boundary|gate|otel|replay|test|negative_test|
# acceptance|authority|lineage|schema|evidence|egress|write|learning|
# runtime_disposition.
# ---------------------------------------------------------------------------

TYPE_RULES: Tuple[Tuple["re.Pattern[str]", str], ...] = (
    (
        re.compile(
            r"\bOTEL\b|\bOpenTelemetry\b|\bspan\b|\btelemetry\b|\btrace_id\b",
            re.IGNORECASE,
        ),
        "otel",
    ),
    (re.compile(r"\breplay\b", re.IGNORECASE), "replay"),
    (
        re.compile(
            r"\bnegative test\b|\banti[-\s]?bypass\b|\bmust fail\b",
            re.IGNORECASE,
        ),
        "negative_test",
    ),
    (
        re.compile(
            r"\btest requirements?\b|\bunit test\b|\bintegration test\b|\be2e test\b",
            re.IGNORECASE,
        ),
        "test",
    ),
    (
        re.compile(r"\bacceptance criteria\b|\bdone criteria\b", re.IGNORECASE),
        "acceptance",
    ),
    (re.compile(r"\bschema\b|\brequired attributes?\b", re.IGNORECASE), "schema"),
    (re.compile(r"\begress\b", re.IGNORECASE), "egress"),
    (
        re.compile(r"\bdurable write\b|\bUWG\b|\bsole durable write path\b", re.IGNORECASE),
        "write",
    ),
    (re.compile(r"\blearning\b|\bpromotion\b", re.IGNORECASE), "learning"),
    (
        re.compile(
            r"\bauthority\b|\bsovereignty\b|\bsovereign\b",
            re.IGNORECASE,
        ),
        "authority",
    ),
    (re.compile(r"\blineage\b", re.IGNORECASE), "lineage"),
    (
        re.compile(r"\bruntime disposition\b|\bdisposition\b", re.IGNORECASE),
        "runtime_disposition",
    ),
    (re.compile(r"\bevidence\b", re.IGNORECASE), "evidence"),
    (
        re.compile(
            r"\bgate\b|\bfail condition\b|\bfails? closed\b|\bblocked\b",
            re.IGNORECASE,
        ),
        "gate",
    ),
    (re.compile(r"\bcontract\b|\binvariant\b", re.IGNORECASE), "contract"),
    (
        re.compile(
            r"\bMUST\b|\bREQUIRED\b|\bFORBIDDEN\b|\bNEVER\b|\bHARD LAW\b|\bHARD NO\b"
        ),
        "boundary",
    ),
)


# Verification dossier per requirement type — minimum evidence categories
# that must be supplied before a record can ever flip out of UNMAPPED.
def verification_needed_for_type(req_type: str) -> Tuple[str, ...]:
    base = ("implementation_symbol", "proof_report_entry")
    if req_type == "otel":
        return base + ("otel_span", "unit_test")
    if req_type == "replay":
        return base + ("replay_artifact", "integration_test")
    if req_type == "negative_test":
        return base + ("negative_bypass_test",)
    if req_type == "test":
        return base + ("unit_test",)
    if req_type in ("gate", "boundary"):
        return base + ("unit_test", "negative_bypass_test")
    if req_type in ("contract", "schema"):
        return base + ("unit_test",)
    if req_type == "acceptance":
        return base + ("e2e_test",)
    if req_type in ("write", "authority"):
        return base + ("integration_test", "negative_bypass_test")
    return base + ("unit_test",)


# Markdown fenced-code-block delimiters.
FENCE_RE: "re.Pattern[str]" = re.compile(r"^\s*```")
