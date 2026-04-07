"""Add missing 'import pytest' to stub test files that call pytest.skip without importing pytest."""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FILES = [
    "tests/unit/agentic_core/config/core/test_config_loader.py",
    "tests/unit/agentic_core/config/core/test_sovereign_config.py",
    "tests/unit/test_FileClassificationAgent.py",
    "tests/unit/test_HOPPipelineExecutor.py",
    "tests/unit/test_IOrchestratorProtocol.py",
    "tests/unit/test_IValidatorProtocol.py",
    "tests/unit/test_L1CognitionBase.py",
    "tests/unit/test_L2ExecutionBase.py",
    "tests/unit/test_L3OrchestrationBase.py",
    "tests/unit/test_L4StateBase.py",
    "tests/unit/test_L5SafetyBase.py",
    "tests/unit/test_L6ObservabilityBase.py",
    "tests/unit/test_RGStrategyExecutor.py",
    "tests/unit/test_RGValidationExecutor.py",
]


def find_insert_position(lines: list[str]) -> int:
    """Return line index after which to insert 'import pytest'."""
    i = 0
    n = len(lines)

    # Skip shebang
    if n > 0 and lines[0].startswith("#!"):
        i = 1

    # Skip leading blanks / comments before docstring
    while i < n and lines[i].strip() == "":
        i += 1

    # Skip module docstring (triple-quoted)
    if i < n:
        stripped = lines[i].strip()
        for q in ('"""', "'''"):
            if stripped.startswith(q):
                # single-line docstring?
                rest = stripped[3:]
                if q in rest:
                    i += 1  # past the single-line docstring
                else:
                    # multi-line: scan for closing
                    i += 1
                    while i < n and q not in lines[i]:
                        i += 1
                    i += 1  # past closing line
                break

    # Skip any trailing blank lines after docstring
    while i < n and lines[i].strip() == "":
        i += 1

    return i


for rel in FILES:
    p = REPO / rel
    if not p.exists():
        print(f"SKIP (not found): {rel}")
        continue
    src = p.read_text(encoding="utf-8")
    if "import pytest" in src:
        print(f"ALREADY OK: {rel}")
        continue
    lines = src.splitlines(keepends=True)
    pos = find_insert_position(lines)
    lines.insert(pos, "import pytest\n")
    p.write_text("".join(lines), encoding="utf-8")
    print(f"FIXED: {rel}")

print("Done.")
