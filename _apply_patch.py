"""Apply the lazy REPO_ROOT patch to execute_ssot.py directly on disk."""

import sys

p = r"agentic_core\L0_maintenance\scripts\execute_ssot.py"
with open(p, encoding="utf-8") as f:
    c = f.read()

# 1. Replace eager REPO_ROOT with lazy infrastructure
old_anchor = "REPO_ROOT = resolve_repo_root()  # noqa: N816\n\n\ndef _apply_v15_enforcement_flag"
new_anchor = (
    "_REPO_ROOT_CACHE: Path | None = None\n"
    "\n"
    "\n"
    "def get_repo_root() -> Path:\n"
    '    """Return (and cache) the deterministic repo root.  Import-safe."""\n'
    "    global _REPO_ROOT_CACHE  # noqa: PLW0603\n"
    "    if _REPO_ROOT_CACHE is None:\n"
    "        _REPO_ROOT_CACHE = resolve_repo_root()\n"
    "    return _REPO_ROOT_CACHE\n"
    "\n"
    "\n"
    "def __getattr__(name: str):\n"
    '    """Module-level lazy attribute -- resolves REPO_ROOT / PROJECT_ROOT on first access."""\n'
    '    if name in ("REPO_ROOT", "PROJECT_ROOT"):\n'
    "        return get_repo_root()\n"
    '    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")\n'
    "\n"
    "\n"
    "def _apply_v15_enforcement_flag"
)
assert old_anchor in c, "PATCH 1 ANCHOR NOT FOUND"
c = c.replace(old_anchor, new_anchor, 1)

# 2. Replace all internal REPO_ROOT references
replacements = [
    ("ASTCodeQualityValidator(REPO_ROOT)", "ASTCodeQualityValidator(get_repo_root())"),
    ('agents["reconciler"](project_root=REPO_ROOT)', 'agents["reconciler"](project_root=get_repo_root())'),
    ('agents["location"](project_root=REPO_ROOT)', 'agents["location"](project_root=get_repo_root())'),
    ('(REPO_ROOT / "agentic_core").resolve()', '(get_repo_root() / "agentic_core").resolve()'),
    (
        'agents["file_classification"](project_root=REPO_ROOT)',
        'agents["file_classification"](project_root=get_repo_root())',
    ),
    ('agents["hierarchy"](project_root=REPO_ROOT)', 'agents["hierarchy"](project_root=get_repo_root())'),
    (
        'agents["arch_governor"](project_root=REPO_ROOT)',
        'agents["arch_governor"](project_root=get_repo_root())',
    ),
    (
        'agents["system_architect"](project_root=REPO_ROOT)',
        'agents["system_architect"](project_root=get_repo_root())',
    ),
    (
        'agents["conversational_repair"](project_root=REPO_ROOT)',
        'agents["conversational_repair"](project_root=get_repo_root())',
    ),
    (
        'agents["root_hygiene"](project_root=REPO_ROOT)',
        'agents["root_hygiene"](project_root=get_repo_root())',
    ),
    ("_legacy_main(remaining, repo_root=REPO_ROOT)", "_legacy_main(remaining, repo_root=get_repo_root())"),
    (
        "repo_root if repo_root is not None else REPO_ROOT",
        "repo_root if repo_root is not None else get_repo_root()",
    ),
]
for old_s, new_s in replacements:
    count = c.count(old_s)
    if count == 0:
        print(f"WARNING: not found: {old_s[:60]}")
    c = c.replace(old_s, new_s)

# 3. Inside _legacy_main body: 3 agent calls should use project_root (local var)
# These were converted to get_repo_root() above but should use project_root since it's available
# They are deeply indented (inside _legacy_main's loop body)
c = c.replace(
    '                            pascal = agents["file_classification"](project_root=get_repo_root())',
    '                            pascal = agents["file_classification"](project_root=project_root)',
)
c = c.replace(
    '                            conversational_agent = agents["conversational_repair"](project_root=get_repo_root())',
    '                            conversational_agent = agents["conversational_repair"](project_root=project_root)',
)
c = c.replace(
    '                            hygiene_agent = agents["root_hygiene"](project_root=get_repo_root())',
    '                            hygiene_agent = agents["root_hygiene"](project_root=project_root)',
)

# 4. load_agents: project_root = REPO_ROOT -> project_root = get_repo_root()
old_la = "        project_root = REPO_ROOT"
if old_la in c:
    c = c.replace(old_la, "        project_root = get_repo_root()", 1)
else:
    print("WARNING: load_agents REPO_ROOT not found (may already be patched)")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

# Verify
with open(p, encoding="utf-8") as f:
    v = f.read()

print(f"has get_repo_root: {'def get_repo_root' in v}")
print(f"has _REPO_ROOT_CACHE: {'_REPO_ROOT_CACHE' in v}")
print(f"has __getattr__: {'def __getattr__' in v}")

remaining = 0
for i, line in enumerate(v.split("\n")):
    ln = i + 1
    s = line.strip()
    if s.startswith("#"):
        continue
    if (
        "REPO_ROOT" in line
        and "_REPO_ROOT_CACHE" not in line
        and "get_repo_root" not in line
        and "__getattr__" not in line
        and "resolved lazily" not in line
        and "__name__" not in line
    ):
        print(f"REMAINING L{ln}: {s}")
        remaining += 1

print(f"Remaining internal REPO_ROOT refs: {remaining}")
if remaining == 0:
    print("PATCH APPLIED SUCCESSFULLY")
    sys.exit(0)
else:
    print("PATCH INCOMPLETE")
    sys.exit(1)
