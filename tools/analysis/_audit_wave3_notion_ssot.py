"""Wave 3 — replace NOTION literals in remaining 7 files."""
import re
import subprocess
import sys
from pathlib import Path

# Files still needing the SSOT replacement
TARGETS = [
    Path(".claude/governance/scripts/_legacy_windsurf/post_agent_deferred_scope_capture.py"),
    Path(".claude/governance/scripts/_legacy_windsurf/post_agent_adr_registry_capture.py"),
    Path("ops_scripts/ci/check_notion_plan_file_drift.py"),
    Path("tools/migration/notion_create_plans_db.py"),
    Path("tools/notion/snapshot_renderer.py"),
    Path("tools/reports/recover_deferred_scope_pendings.py"),
]

# All inline literal patterns we want to remove and the SSOT name to import
LITERAL_REPLACEMENTS = [
    (r'^NOTION_API_VERSION\s*=\s*"2025-09-03"\s*$', "NOTION_API_VERSION"),
    (r'^NOTION_BASE\s*=\s*"https://api\.notion\.com/v1"\s*$', "NOTION_BASE"),
    (r'^NOTION_POST_URL\s*=\s*"https://api\.notion\.com/v1/pages"\s*$', "NOTION_POST_URL"),
    (r'^NOTION_HTTP_TIMEOUT_S\s*=\s*15\.0\s*$', "NOTION_HTTP_TIMEOUT_S"),
    (r'^WAVE_PHASE_DATA_SOURCE_ID\s*=\s*"fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"\s*$', "WAVE_PHASE_DATA_SOURCE_ID"),
    (r'^WAVE_PHASE_DS_ID\s*=\s*"fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"\s*$', "WAVE_PHASE_DATA_SOURCE_ID as WAVE_PHASE_DS_ID"),
    (r'^WAVE_PHASE_DB_ID\s*=\s*"aa8d2507-101e-4384-81d9-60ea3fe33876"\s*$', "WAVE_PHASE_DB_ID"),
    (r'^ADR_REGISTRY_DB_ID\s*=\s*"6ed25e12-bd92-4352-ac7a-3a971311f024"\s*$', "ADR_REGISTRY_DB_ID"),
    (r'^ADR_REGISTRY_DS_ID\s*=\s*"e59d7640-dc09-48f9-8bdc-b0c94bf98c2a"\s*$', "ADR_REGISTRY_DS_ID"),
]

# Bootstrap snippet — same for .claude/governance/scripts/_legacy_windsurf/* and other roots
BOOTSTRAP_WINDSURF = """\
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _notion_constants import (  # noqa: E402
{names}
)
"""
BOOTSTRAP_OUTSIDE = """\
import sys as _sys
_sys.path.insert(0, str(Path(REPO_ROOT) / ".claude" / "governance/scripts" / "_legacy_windsurf"))
from _notion_constants import (  # noqa: E402
{names}
)
"""


def find_repo_root_in_file(text: str) -> bool:
    return bool(re.search(r"^REPO_ROOT\s*=", text, re.MULTILINE))


def transform(path: Path) -> tuple[str, str, list[str]]:
    text = path.read_text(encoding="utf-8")
    new_text = text
    imports_needed: set[str] = set()
    for pat, name in LITERAL_REPLACEMENTS:
        compiled = re.compile(pat, re.MULTILINE)
        # Look line-by-line for matches; remove them
        if compiled.search(new_text):
            new_text = compiled.sub("", new_text)
            imports_needed.add(name)

    if not imports_needed:
        return text, text, []

    # Decide bootstrap flavor: if file path starts with .claude/governance/scripts/_legacy_windsurf, use WINDSURF; else OUTSIDE
    rel_posix = path.as_posix()
    is_windsurf = rel_posix.startswith(".claude/governance/scripts/_legacy_windsurf/")
    if not is_windsurf and not find_repo_root_in_file(new_text):
        # Need to add REPO_ROOT definition. Locate first `from pathlib import Path` and add after.
        m = re.search(r"^from pathlib import Path\s*$", new_text, re.MULTILINE)
        if m:
            insertion = "REPO_ROOT = Path(__file__).resolve().parents[2]\n"
            new_text = new_text[:m.end()] + "\n" + insertion + new_text[m.end():]

    name_lines = "\n".join(f"    {n}," for n in sorted(imports_needed))
    bootstrap = (BOOTSTRAP_WINDSURF if is_windsurf else BOOTSTRAP_OUTSIDE).format(names=name_lines)

    # Insert bootstrap block. For .claude/governance/scripts/_legacy_windsurf, after REPO_ROOT lines or after imports.
    # For simplicity: insert after the LAST occurrence of `from pathlib import Path` line (or `Path(__file__)` definition).
    # Actually best: insert after first blank-line-following-REPO_ROOT, or after imports block.

    lines = new_text.splitlines(keepends=True)
    insert_idx = 0
    paren_depth = 0
    in_doc = False
    quote = None
    for i, line in enumerate(lines):
        s = line.strip()
        if paren_depth > 0:
            paren_depth += line.count("(") - line.count(")")
            if paren_depth <= 0:
                paren_depth = 0
                insert_idx = i + 1
            continue
        if not in_doc and (s.startswith('"""') or s.startswith("'''")):
            q = s[:3]
            if s.count(q) >= 2 and len(s) > 3:
                insert_idx = i + 1
                continue
            in_doc = True; quote = q
            continue
        if in_doc:
            if quote in s:
                in_doc = False
                insert_idx = i + 1
            continue
        if s.startswith("import ") or s.startswith("from ") or s.startswith("from __future__"):
            opens = line.count("(") - line.count(")")
            if opens > 0:
                paren_depth = opens
                continue
            insert_idx = i + 1
            continue
        if s.startswith("REPO_ROOT") or s.startswith("AUDIT_LOG") or s.startswith("PLANS_DIR") or s.startswith("CAPTURE_LOG"):
            insert_idx = i + 1
            continue
        if not s or s.startswith("#"):
            continue
        break
    lines.insert(insert_idx, "\n" + bootstrap + "\n")
    return text, "".join(lines), sorted(imports_needed)


def main() -> int:
    changed = []
    for path in TARGETS:
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        old, new, names = transform(path)
        if old == new:
            print(f"NO-OP: {path}")
            continue
        path.write_text(new, encoding="utf-8")
        changed.append(path)
        print(f"WROTE: {path}  imports={names}")

    print()
    print(f"Verifying py_compile on {len(changed)} files...")
    fails = 0
    for path in changed:
        r = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            fails += 1
            print(f"  FAIL {path}")
            for line in r.stderr.splitlines()[:5]:
                print(f"     {line}")
    print(f"Compile failures: {fails}/{len(changed)}")
    return fails


if __name__ == "__main__":
    sys.exit(main())
