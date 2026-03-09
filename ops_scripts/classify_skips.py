"""Classify all skip sites by legitimacy category."""

from pathlib import Path

lines = Path("c:/Git/Agentic-Workflow/skip_audit.txt").read_text(encoding="utf-8").splitlines()

# Categories
LEGITIMATE_EXTERNAL = []  # Redis, Playwright — genuinely optional infra
LEGITIMATE_ENV_FLAG = []  # Opt-in tamper/negative-control tests
LEGITIMATE_PLATFORM = []  # Platform-specific (read-only dir on Windows)
LEGITIMATE_CONDITIONAL = []  # faiss-gpu installed → skip cpu-only path (correct logic)

ILLEGITIMATE_MODULE_MISSING = []  # Module not importable → should be hard fail
ILLEGITIMATE_FILE_MISSING = []  # Source file not found → should be hard fail
ILLEGITIMATE_NOT_IMPLEMENTED = []  # "not yet implemented" → dead test
ILLEGITIMATE_IMPORTORSKIP = []  # pytest.importorskip
ILLEGITIMATE_ARTIFACT_MISSING = []  # Generated artifact not found → should fail
ILLEGITIMATE_OTHER = []

for line in lines:
    parts = line.split("|", 3)
    kind, f, lineno, reason = parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else ""
    r = reason.lower()
    entry = (f, lineno, reason)

    if kind == "importorskip":
        ILLEGITIMATE_IMPORTORSKIP.append(entry)
        continue

    # Legitimately optional external services
    if any(
        k in r
        for k in [
            "redis not running",
            "playwright not installed",
            "playwright visual tests should be run separately",
        ]
    ):
        LEGITIMATE_EXTERNAL.append(entry)
        continue

    # Opt-in negative control / tamper env vars
    if "ssot_orch_negctrl_tamper" in r or "activate tamper" in r:
        LEGITIMATE_ENV_FLAG.append(entry)
        continue

    # Platform-specific skip (cannot create read-only dir on Windows)
    if "read-only directory" in r or "platform" in r:
        LEGITIMATE_PLATFORM.append(entry)
        continue

    # Conditional: faiss-gpu installed so cpu-only path not applicable
    if "faiss-gpu" in r:
        LEGITIMATE_CONDITIONAL.append(entry)
        continue

    # Illegitimate: module/class/function not importable or not found
    if any(
        k in r
        for k in [
            "cannot import",
            "not importable",
            "not found in module",
            "not available (import commented out)",
            "not available",
            "module not available",
            "scanner not available",
        ]
    ):
        ILLEGITIMATE_MODULE_MISSING.append(entry)
        continue

    # Illegitimate: source file / directory not found
    if any(
        k in r
        for k in [
            "not found",
            "not present",
            "does not exist",
            "directory not found",
            "not found at",
        ]
    ):
        ILLEGITIMATE_FILE_MISSING.append(entry)
        continue

    # Illegitimate: test not yet written
    if any(
        k in r
        for k in [
            "not yet implemented",
            "using mock for tests",
            "method not implemented yet",
            "should be run separately",
        ]
    ):
        ILLEGITIMATE_NOT_IMPLEMENTED.append(entry)
        continue

    # Illegitimate: generated artifact not found
    if any(
        k in r
        for k in [
            "dashboard html not found",
            "discovery artifact not found",
            "discovery output not found",
            "no snapshot yet",
        ]
    ):
        ILLEGITIMATE_ARTIFACT_MISSING.append(entry)
        continue

    ILLEGITIMATE_OTHER.append(entry)

total_legit = (
    len(LEGITIMATE_EXTERNAL)
    + len(LEGITIMATE_ENV_FLAG)
    + len(LEGITIMATE_PLATFORM)
    + len(LEGITIMATE_CONDITIONAL)
)
total_illegit = (
    len(ILLEGITIMATE_IMPORTORSKIP)
    + len(ILLEGITIMATE_MODULE_MISSING)
    + len(ILLEGITIMATE_FILE_MISSING)
    + len(ILLEGITIMATE_NOT_IMPLEMENTED)
    + len(ILLEGITIMATE_ARTIFACT_MISSING)
    + len(ILLEGITIMATE_OTHER)
)

print(f"TOTAL: {len(lines)}  |  LEGITIMATE: {total_legit}  |  ILLEGITIMATE: {total_illegit}")
print()


def show(label, items):
    print(f"=== {label} ({len(items)}) ===")
    for f, l, r in items:
        print(f"  tests/{f}:{l}  {r[:120]}")
    print()


show("LEGITIMATE: external service", LEGITIMATE_EXTERNAL)
show("LEGITIMATE: opt-in env flag", LEGITIMATE_ENV_FLAG)
show("LEGITIMATE: platform-specific", LEGITIMATE_PLATFORM)
show("LEGITIMATE: conditional (faiss-gpu)", LEGITIMATE_CONDITIONAL)
show("ILLEGITIMATE: importorskip", ILLEGITIMATE_IMPORTORSKIP)
show("ILLEGITIMATE: module/symbol not importable", ILLEGITIMATE_MODULE_MISSING)
show("ILLEGITIMATE: file/dir not found", ILLEGITIMATE_FILE_MISSING)
show("ILLEGITIMATE: not yet implemented", ILLEGITIMATE_NOT_IMPLEMENTED)
show("ILLEGITIMATE: generated artifact missing", ILLEGITIMATE_ARTIFACT_MISSING)
show("ILLEGITIMATE: other", ILLEGITIMATE_OTHER)
