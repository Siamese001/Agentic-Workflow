"""Validator for the 2026-04-26 parent-thinning refactor.

Checks:
  1. Child-map link integrity: every child referenced in a parent exists on disk.
  2. No-overlap grep assertions: forbidden ownership claims are absent.
  3. Key-phrase preservation: canonical phrases discoverable.
  4. Zip round-trip: extract-and-diff against source.

Exit code: 0 on PASS, 1 on any FAIL.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REF = REPO / "docs" / "reference"
ZIP_PATH = REF / "Agentic_Requirements_MECE_ParentThinned_ZeroLoss.zip"

RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"


def ok(msg: str) -> None:
    print(f"{GREEN}[PASS]{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}[FAIL]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}[WARN]{RESET} {msg}")


def section(title: str) -> None:
    print(f"\n{BOLD}=== {title} ==={RESET}")


# ---------------------------------------------------------------------------
# Check 1: Child-map link integrity
# ---------------------------------------------------------------------------
# For each thinned parent, verify every referenced child (.md) exists.
THINNED_PARENTS = [
    REF / "03A_C0_Context_Engine" / "C0_Context_Engine.md",
    REF / "04_L2_Execute" / "04_L2_Execute.md",
    REF / "05_Exit_Evaluation_and_Control" / "05_Live_Runtime_Exit_Control_&_Evaluation.md",
]

CHILD_REF_RE = re.compile(r"(?<![A-Za-z0-9_])([0-9A-Za-z]+(?:\.[0-9A-Za-z_]+)+\.md)")


def check_child_links() -> int:
    section("1. Child-map link integrity")
    failures = 0
    for parent in THINNED_PARENTS:
        if not parent.is_file():
            fail(f"parent missing: {parent.relative_to(REF)}")
            failures += 1
            continue
        text = parent.read_text(encoding="utf-8")
        folder = parent.parent
        referenced = set(CHILD_REF_RE.findall(text))
        # Filter to plausible same-folder children only (skip cross-folder and MANIFEST.json)
        child_like = {r for r in referenced if r.endswith(".md") and not r.startswith("MANIFEST")}
        missing = [c for c in sorted(child_like) if not (folder / c).is_file()]
        if missing:
            fail(f"{parent.name}: {len(missing)} referenced child(ren) not on disk:")
            for m in missing:
                print(f"       - {m}")
            failures += len(missing)
        else:
            ok(f"{parent.name}: all {len(child_like)} child refs resolve")
    return failures


# ---------------------------------------------------------------------------
# Check 2: No-overlap grep assertions
# ---------------------------------------------------------------------------
# Forbidden ownership claims that MUST NOT appear as authoritative statements.
NO_OVERLAP_ASSERTIONS = [
    # (description, folder, regex_to_forbid)
    ("C0 does not decide runtime dispositions",
     REF / "03A_C0_Context_Engine",
     re.compile(r"(?i)C0\s+(?:emits|decides|approves)\s+(?:ALLOW|DENY|REROUTE|ESCALATE_HITL|COMMIT_REQUEST|BLOCK_COMMIT|ALLOW_FINISH)")),
    ("Prompt Assembly does not retrieve",
     REF / "03B_PA_Prompt_Assembly",
     re.compile(r"(?i)Prompt\s+Assembly\s+(?:retrieves|fetches)\s+evidence")),
    ("L2 does not mutate L4",
     REF / "04_L2_Execute",
     re.compile(r"(?i)L2\s+(?:mutates|writes\s+to)\s+L4")),
    ("L6 does not mutate current run",
     REF / "06_L6_Shadow_Evaluation_System_Learning",
     re.compile(r"(?i)L6\s+(?:mutates|rescues)\s+(?:the\s+)?current\s+run")),
    ("Exit does not execute tools",
     REF / "05_Exit_Evaluation_and_Control",
     re.compile(r"(?i)Exit\s+(?:executes|invokes|calls)\s+(?:tools?|models?)")),
    ("L0 does not execute",
     REF / "03_L0_Route_Decision_and_L3_Orchestration",
     re.compile(r"(?i)L0\s+(?:executes|runs\s+the\s+script|calls\s+the\s+tool)")),
]


def check_no_overlap() -> int:
    section("2. No-overlap grep assertions")
    failures = 0
    for desc, folder, pat in NO_OVERLAP_ASSERTIONS:
        if not folder.is_dir():
            fail(f"folder missing: {folder.relative_to(REF)}")
            failures += 1
            continue
        hits: list[tuple[Path, int, str]] = []
        for md in folder.rglob("*.md"):
            for i, line in enumerate(md.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pat.search(line):
                    # Filter: "does not" / "must not" / "never" / "FORBIDDEN" negate the match
                    if re.search(r"(?i)(?:does\s+not|must\s+not|never|forbid|cannot|may\s+not|MUST\s+NOT)", line):
                        continue
                    hits.append((md.relative_to(REF), i, line.strip()[:120]))
        if hits:
            fail(f"{desc}: {len(hits)} unguarded claim(s):")
            for h in hits[:3]:
                print(f"       {h[0]}:{h[1]}  {h[2]}")
            failures += len(hits)
        else:
            ok(desc)
    return failures


# ---------------------------------------------------------------------------
# Check 3: Key-phrase preservation
# ---------------------------------------------------------------------------
KEY_PHRASES = [
    ("Retrieved text is data, not instruction", REF / "03A_C0_Context_Engine"),
    ("FinalEvidenceContract", REF / "03A_C0_Context_Engine"),
    ("HYDRATE", REF / "03A_C0_Context_Engine"),
    ("CONTRADICTION", REF / "03A_C0_Context_Engine"),
    ("proposed_state_diff", REF / "04_L2_Execute"),
    ("sealed_l2_artifact", REF / "04_L2_Execute"),
    ("same-authority", REF / "04_L2_Execute"),
    ("PTC", REF / "04_L2_Execute"),
    ("ExitReviewPacket", REF / "05_Exit_Evaluation_and_Control"),
    ("X1J", REF / "05_Exit_Evaluation_and_Control"),
    ("X3C", REF / "05_Exit_Evaluation_and_Control"),
    ("HITL freeze", REF / "05_Exit_Evaluation_and_Control"),
    ("exactly one X3", REF / "05_Exit_Evaluation_and_Control"),
    ("UWG", REF / "05_Exit_Evaluation_and_Control"),
    ("GateVerdict", REF / "00C_Runtime_Gates_Current_Run_Mesh"),
]


def check_key_phrases() -> int:
    section("3. Key-phrase preservation")
    failures = 0
    for phrase, folder in KEY_PHRASES:
        if not folder.is_dir():
            fail(f"folder missing: {folder.relative_to(REF)}")
            failures += 1
            continue
        hit_count = 0
        for md in folder.rglob("*.md"):
            hit_count += md.read_text(encoding="utf-8", errors="replace").count(phrase)
        if hit_count == 0:
            fail(f"phrase lost: '{phrase}' not found in {folder.name}")
            failures += 1
        else:
            ok(f"'{phrase}' preserved ({hit_count} hits in {folder.name})")
    return failures


# ---------------------------------------------------------------------------
# Check 4: Zip round-trip
# ---------------------------------------------------------------------------
def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_zip_roundtrip() -> int:
    section("4. Zip round-trip extract-and-diff")
    if not ZIP_PATH.is_file():
        fail(f"zip not found: {ZIP_PATH.relative_to(REF)}")
        return 1
    # Integrity
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad:
            fail(f"zip integrity: bad entry {bad}")
            return 1
        ok(f"zip integrity: {len(zf.namelist())} entries, no corruption")
        names = zf.namelist()

    # Extract to temp and diff hashes
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        extract_root = Path(td) / "extract"
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(extract_root)

        checked = 0
        mismatches: list[str] = []
        for name in names:
            src = REF / name
            dst = extract_root / name
            if not src.is_file() or not dst.is_file():
                mismatches.append(f"missing: {name}")
                continue
            if file_sha256(src) != file_sha256(dst):
                mismatches.append(f"hash mismatch: {name}")
            checked += 1

        if mismatches:
            fail(f"zip round-trip: {len(mismatches)} discrepancies")
            for m in mismatches[:5]:
                print(f"       - {m}")
            failures += len(mismatches)
        else:
            ok(f"zip round-trip: {checked}/{len(names)} files byte-identical")

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    total_failures = 0
    total_failures += check_child_links()
    total_failures += check_no_overlap()
    total_failures += check_key_phrases()
    total_failures += check_zip_roundtrip()

    print()
    if total_failures == 0:
        print(f"{BOLD}{GREEN}VALIDATION: PASS (0 failures){RESET}")
        return 0
    print(f"{BOLD}{RED}VALIDATION: FAIL ({total_failures} failures){RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
