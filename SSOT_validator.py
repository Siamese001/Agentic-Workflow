# -*- coding: utf-8 -*-
"""
===============================================================================
Static SSoT Validator v4.2 — unified_structure_subatomic.yaml + META YAML
Fast, deterministic, zero side-effects. Designed for Agentic-Workflow.
===============================================================================

Validates the LIVE repository structure (no phases, no rewrites) against:

  - unified_structure_subatomic.yaml       (SSoT v4.2 – main)
  - unified_structure_subatomic_meta.yaml  (META v4.2 – invariants)

Enforced invariants (partial list):
  - K1–K2: YAML parse
  - K3: Domain roots exist
  - K4–K5: Domain modes and canonical keys
  - K6: Max depth
  - K7: Forbidden patterns per domain (main + META)
  - K8: Filename prefixes (top-level only)
  - K9: No L*/P* in support domains
  - K10: Test taxonomy high-level structure
  - K11: shared_engine_ops immutability
  - K12: L5_safety is flat (subatomic canon 2025)
  - K13: DISABLED — semantic_cache migrated to durable knowledge plane
  - K14: NO GHOST FILES — empty/stub files banned
  - K15: Protected paths respected (no spurious errors)
  - Engine separation (LIC vs RG)
  - Low-signal names
  - YAML ↔ filesystem shape (warnings)

Output: ssot_validation_report.json at repo root.
===============================================================================
"""

from pathlib import Path
import yaml
import json
import fnmatch
import re
from typing import Dict, Any, List

# ── Config ─────────────────────────────────────────────────────────────

REPO = Path("C:/Git/Agentic-Workflow").resolve()
MAIN = REPO / "unified_structure_subatomic.yaml"
META = REPO / "unified_structure_subatomic_meta.yaml"

for p in (MAIN, META):
    if not p.exists():
        raise FileNotFoundError(f"Missing SSoT file: {p}")

main: Dict[str, Any] = yaml.safe_load(MAIN.read_text(encoding="utf-8"))
meta: Dict[str, Any] = yaml.safe_load(META.read_text(encoding="utf-8"))

# Domain root mapping: logical name -> actual filesystem folder
# Updated 2025-12-08: apps_lic and apps_rg are now top-level (prefix purge complete)
DOMAIN_ROOT_MAP: Dict[str, str] = {
    "agentic_core": "agentic_core",
    "schemas": "schemas",
    "runtime": "runtime",
    "prompt_governance": "prompt_governance",
    "config": "config",
    "data": "06_data",
    "observability": "observability",
    "scripts": "scripts",
    "apps_lic": "apps_lic",
    "apps_rg": "apps_rg",
    "tests": "tests",
    "shared": "shared",
    "shared_engine_ops": "shared_engine_ops",
}

def get_domain_root(domain: str) -> Path:
    """Get the actual filesystem path for a logical domain name."""
    mapped = DOMAIN_ROOT_MAP.get(domain, domain)
    return REPO / mapped

errors: List[str] = []
warnings: List[str] = []
ok: List[str] = ["K1/K2: YAML parsed successfully."]

def err(msg: str) -> None:
    errors.append(msg)

def warn(msg: str) -> None:
    warnings.append(msg)

def ok_msg(msg: str) -> None:
    ok.append(msg)

# ── Helpers ────────────────────────────────────────────────────────────

def rel(p: Path) -> Path:
    return p.relative_to(REPO)

def rel_str(p: Path) -> str:
    return str(rel(p)).replace("\\", "/")

def depth(p: Path) -> int:
    return len(p.parts)

def has_token(name: str, tokens: List[str]) -> bool:
    lower = name.lower()
    return any(t.lower() in lower for t in tokens)

def matches_pattern(name: str, pattern: str) -> bool:
    """
    Pattern helper for 'forbidden' like 'L[0-9]_*', 'P[0-9]_*', 'resume', etc.
    Uses regex if pattern contains brackets, otherwise fnmatch-style semantics.
    """
    if '[' in pattern and ']' in pattern:
        # Treat as regex pattern (e.g., "L[0-9]_*" matches L1_cognition but not "Language")
        # The pattern should match layer/phase names like L1_, L2_, P1_, P2_ etc.
        regex_pattern = f"^{pattern}"
        return bool(re.match(regex_pattern, name))
    return fnmatch.fnmatch(name, pattern)

def is_protected(p: Path) -> bool:
    """
    True if path is under any protected_paths glob in META.
    Used to AVOID flagging depth / shape issues on things like .git, .venv, caches.
    (We still allow special rules like K11 to examine protected regions explicitly.)
    """
    relpath = rel_str(p)
    for pat in meta.get("protected_paths", []):
        if fnmatch.fnmatch(relpath, pat):
            return True
    return False

# Precompute path list once for speed
all_paths: List[Path] = [p for p in REPO.rglob("*")]

# ── Basic structural invariants (K3, K4, K5, K6) ───────────────────────

# K3 – domain roots exist
domain_modes = main["domain_modes"]
for domain in domain_modes:
    root = get_domain_root(domain)
    if not root.exists():
        err(f"K3: Missing domain root for '{domain}': {root}")
    else:
        ok_msg(f"K3: Domain root exists: {rel(root)}")

# Optional K4/K5 – domain modes validity (light check)
valid_models = {"cognitive_engine", "operational_support", "library_support", "test_taxonomy"}
for domain, mode in domain_modes.items():
    if domain == "tests":
        # tests domain uses test_taxonomy model; checked in META
        continue
    # Cross-check with META invariants if present
    inv = meta["domain_invariants"].get(domain)
    if inv:
        model = inv.get("model")
        if model and model not in valid_models:
            err(f"K5: Invalid model '{model}' for domain '{domain}' in META.")
        elif model:
            ok_msg(f"K5: Domain '{domain}' model '{model}' valid.")
    # mode in main is conceptual, not enforced further here

# K6 – max depth (skip obvious non-code/protected noise)
max_depth = meta["structural_rules"]["max_depth"]
for p in all_paths:
    # skip non-code/protected spaces to avoid noise
    if any(part in {".git", ".venv"} for part in p.parts):
        continue
    if any(part in {".pytest_cache", ".mypy_cache", ".ruff_cache"} for part in p.parts):
        continue
    # Skip 06_data entirely - it's a curated knowledge plane with its own depth rules
    if "06_data" in p.parts:
        continue
    # also skip paths that META marks protected, except we still
    # allow shared_engine_ops to be depth-checked
    if is_protected(p) and "shared_engine_ops" not in p.parts:
        continue

    d = depth(rel(p))
    if d > max_depth:
        err(f"K6: Depth {d} exceeds max {max_depth}: {rel(p)}")

# ── K7 – Forbidden patterns per domain (META + main.hierarchy) ────────

domain_invariants = meta["domain_invariants"]
hierarchy = main.get("hierarchy", {})

for domain, inv in domain_invariants.items():
    # Skip 06_data - curated knowledge plane has its own rules
    if domain == "data":
        continue
    
    root = get_domain_root(domain)
    if not root.exists():
        continue

    # Collect forbidden from META + main.hierarchy[domain].forbidden
    forbidden_meta = inv.get("forbidden_patterns", []) or []
    forbidden_main = hierarchy.get(domain, {}).get("forbidden", []) or []
    forbidden = list(set(forbidden_meta) | set(forbidden_main))

    if not forbidden:
        continue

    for p in root.rglob("*"):
        if is_protected(p):
            continue
        name = p.name
        for pattern in forbidden:
            if matches_pattern(name, pattern):
                err(f"K7: Forbidden pattern '{pattern}' in {rel(p)}")

# ── K9 – No L*/P* in support domains ──────────────────────────────────

support_domains = meta["domain_overrides"]["support_domains"]["domains"]
L_or_P_re = re.compile(r"^[LP]\d+_")

for domain in support_domains:
    # Skip 06_data - curated knowledge plane has archived code with L/P structure
    if domain == "data":
        continue
    
    root = get_domain_root(domain)
    if not root.exists():
        continue
    for p in root.rglob("*"):
        if is_protected(p):
            continue
        name = p.name
        if L_or_P_re.match(name):
            err(f"K9: L/P layer name in support domain '{domain}': {rel(p)}")

# ── K8 – Filename prefix enforcement (top-level only) ──────────────────

naming = main["naming_conventions"]
prefixes = naming["filename_prefixes"]
exempt = naming["prefix_exemptions"]

for domain, pattern in prefixes.items():
    if not pattern:
        continue  # no enforced prefix (e.g., agentic_core)

    prefix = pattern.split("*")[0]
    domain_root = get_domain_root(domain)
    if not domain_root.exists():
        continue

    # Only enforce on files directly under domain root
    for p in domain_root.iterdir():
        if not p.is_file():
            continue
        if is_protected(p):
            continue

        name = p.name
        # skip exempt patterns (e.g. L*, P*, etc.)
        if any(fnmatch.fnmatch(name, ex) for ex in exempt.get(domain, [])):
            continue
        # skip __init__.py, .json metadata files, and engine entry point files
        if name == "__init__.py" or name.endswith(".json") or name.endswith("_engine.py") or name.endswith("_engine_v560.py"):
            continue

        if not name.startswith(prefix):
            err(f"K8: File '{rel(p)}' in domain '{domain}' does not start with '{prefix}'")

# ── K11 – shared_engine_ops immutability ──────────────────────────────

shared_root = REPO / "shared_engine_ops"
if shared_root.exists():
    allowed_shared = set(domain_invariants["shared_engine_ops"]["allowed_roots"])
    for child in shared_root.iterdir():
        if child.is_dir() and child.name not in allowed_shared:
            err(f"K11: Unauthorized folder in shared_engine_ops: {rel(child)}")
    ok_msg("K11: shared_engine_ops structure checked.")

# ── K12 – L5_safety must be flat (subatomic canon 2025) ──────────────
# L5_safety no longer has P4_safety subfolder - files are directly in L5_safety/

cognitive_domains = ["agentic_core", "apps_lic", "apps_rg"]
for domain in cognitive_domains:
    root = get_domain_root(domain)
    if not root.exists():
        continue
    l5 = root / "L5_safety"
    if not l5.exists():
        continue
    # L5_safety should be flat - no P* subfolders allowed (subatomic canon 2025)
    for child in l5.iterdir():
        if child.is_dir() and child.name.startswith("P") and "_" in child.name:
            err(f"K12: L5_safety must be flat - found phase folder '{child.name}' in {domain}: {rel(child)}")
    ok_msg(f"K12: L5_safety is flat in {domain}")

# ── K13 – DISABLED: semantic_cache migrated to durable knowledge plane ────────
# K13: semantic_cache is now a durable curated asset under 06_data/semantic_cache/v*_curated/
# Runtime checks removed as semantic_cache is no longer runtime-coupled.
ok_msg("K13: semantic_cache migrated to durable knowledge plane — runtime checks removed")

# ── K14 – NO GHOST FILES (eternal law 2025) ────────────────────────────
# A .py file (excluding __init__.py) must have real executable logic.
# Empty files and stub files with only 'pass' are banned.
# Files with actual code (functions, classes, assignments) are allowed.

def is_ghost_file(file_path: Path) -> tuple:
    """Check if a file is a ghost/stub file. Returns (is_ghost, reason)."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore").strip()
        
        # Empty file
        if not content:
            return True, "empty"
        
        # Very short file check
        if len(content) < 50:
            if content in ["pass", "..."]:
                return True, "minimal_stub"
        
        # Check for actual code patterns (not just imports/docstrings)
        has_function = "def " in content
        has_class = "class " in content
        has_assignment = " = " in content and not content.strip().startswith("#")
        has_return = "return " in content
        has_dict_or_list = "{" in content or "[" in content
        
        # If file has any real code structure, it's not a ghost
        if has_function or has_class or has_assignment or has_return or has_dict_or_list:
            return False, "has_content"
        
        # Count non-empty, non-comment, non-import lines
        lines = content.split("\n")
        code_lines = []
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith("from ") or stripped.startswith("import "):
                continue
            if stripped in ["pass", "..."]:
                continue
            code_lines.append(stripped)
        
        # If no real code lines after filtering, it's a ghost
        if len(code_lines) == 0:
            return True, "imports_only"
        
        return False, "has_content"
    except Exception:
        return False, "read_error"

ghost_file_count = 0
for p in all_paths:
    if not p.is_file() or not p.suffix == ".py":
        continue
    if p.name == "__init__.py" or p.name == "conftest.py":
        continue
    if is_protected(p):
        continue
    # Skip 06_data (curated knowledge plane)
    if "06_data" in p.parts:
        continue
    
    is_ghost, reason = is_ghost_file(p)
    if is_ghost:
        ghost_file_count += 1
        err(f"K14: Ghost file detected ({reason}): {rel(p)}")

if ghost_file_count == 0:
    ok_msg("K14: No ghost files detected — repo is honest")
else:
    err(f"K14: {ghost_file_count} ghost files detected — see errors above")

# ── Engine separation rules (LIC ↔ RG) ────────────────────────────────

sep = meta["engine_separation"]

lic_forbidden = sep["outreach_engine"]["forbidden_tokens"]
rg_forbidden = sep["resume_engine"]["forbidden_tokens"]

lic_root = get_domain_root("apps_lic")
rg_root = get_domain_root("apps_rg")

if lic_root.exists():
    for p in lic_root.rglob("*"):
        if is_protected(p):
            continue
        if has_token(p.name, lic_forbidden):
            err(f"Engine separation violation (LIC contains RG concepts): {rel(p)}")

if rg_root.exists():
    for p in rg_root.rglob("*"):
        if is_protected(p):
            continue
        if has_token(p.name, rg_forbidden):
            err(f"Engine separation violation (RG contains LIC concepts): {rel(p)}")

# ── Low-signal names ──────────────────────────────────────────────────

low_signal = meta["validation_invariants"]["disallowed_low_signal_names"]
for p in all_paths:
    if is_protected(p):
        continue
    # Skip 06_data - curated knowledge plane has its own naming conventions
    if "06_data" in p.parts:
        continue
    if has_token(p.name, low_signal):
        err(f"Low-signal name detected: {rel(p)}")

# ── Support-domain allowed_layers enforcement (light) ─────────────────

support_allowed_layers = set(meta["validation_invariants"]["allowed_support_layers"])

for domain in support_domains:
    root = get_domain_root(domain)
    if not root.exists():
        continue
    for child in root.iterdir():
        if not child.is_dir():
            continue
        if child.name not in support_allowed_layers:
            # Only warn here to avoid over-strict breakage in legacy trees
            warn(f"Support domain '{domain}' has unexpected top-level dir '{child.name}' (not in allowed_support_layers).")

# ── Forbidden layer/phase combinations ────────────────────────────────

forbidden_combos = meta["validation_invariants"]["forbidden_phase_layer_combinations"]
for domain in cognitive_domains:
    root = get_domain_root(domain)
    if not root.exists():
        continue
    for combo in forbidden_combos:
        layer, phase = combo.split("/")
        combo_path = root / layer / phase
        if combo_path.exists():
            err(f"Forbidden layer/phase combo {combo} present in {domain}: {rel(combo_path)}")

# ── Test taxonomy high-level enforcement (K10) ────────────────────────

tests_root = get_domain_root("tests")
tests_inv = domain_invariants.get("tests", {})
allowed_test_structure = tests_inv.get("allowed_structure", {})

if tests_root.exists():
    # required top-level groups
    required_groups = set(allowed_test_structure.keys())
    existing_groups = {p.name for p in tests_root.iterdir() if p.is_dir()}

    missing_groups = required_groups - existing_groups
    extra_groups = existing_groups - required_groups - {"__pycache__"}  # logic folder removed per YAML compliance

    for g in missing_groups:
        err(f"K10: Missing top-level tests group '{g}' under tests/")

    for g in extra_groups:
        warn(f"K10: Extra top-level tests group '{g}' under tests/ not in META.allowed_structure.")

    ok_msg("K10: Test taxonomy high-level groups checked.")
else:
    warn("K10: tests/ root does not exist; test taxonomy not enforced.")

# ── YAML ↔ filesystem shape (warnings-only) ───────────────────────────

# Keys to skip (metadata, not structure)
SKIP_SHAPE_KEYS = {
    "meta_sidecar", "canonical_definition", "structure_version",
    "description", "binds_to", "canonical_role", "global",
    "domains", "domain_modes", "naming_conventions",
    "engine_namespaces", "hierarchy", "enforcement",
    # Skip metadata within hierarchy entries
    "mode", "structure_type", "max_depth", "allowed_layers",
    "allowed_phases", "forbidden", "protected",
    "auto_generate_missing_paths", "enforce_allowed_structure",
    "allowed_structure_governed_by"
}

def resolve_yaml_path(yaml_path: Path) -> Path:
    """
    Resolve a YAML-defined path to actual filesystem path.
    Handles domain name mapping (e.g., agentic_core -> 01_agentic_core).
    """
    parts = yaml_path.parts
    if not parts:
        return REPO
    
    first_part = parts[0]
    
    # Check if first part is a domain name that needs mapping
    if first_part in DOMAIN_ROOT_MAP:
        mapped = DOMAIN_ROOT_MAP[first_part]
        if len(parts) > 1:
            return REPO / mapped / Path(*parts[1:])
        return REPO / mapped
    
    return REPO / yaml_path

def check_shape(node: Any, prefix: Path = Path(".")) -> None:
    """
    Ensure: dict => directory, None => file, aligned with YAML.
    Emits warnings only (shape drift), no hard errors.
    Uses DOMAIN_ROOT_MAP to resolve logical domain names to filesystem paths.
    """
    if node is None:
        return

    if isinstance(node, dict):
        for key, value in node.items():
            # Skip non-structural keys
            if key in SKIP_SHAPE_KEYS:
                continue

            # Build YAML path and resolve to filesystem path
            yaml_path = (prefix / key) if str(prefix) != "." else Path(key)
            path = resolve_yaml_path(yaml_path)
            
            if value is None:
                # expected file
                if not path.is_file():
                    # skip if protected or clearly non-code (like notes)
                    if not is_protected(path):
                        warnings.append(f"Shape: Expected file missing for YAML node: {rel(path)}")
            elif isinstance(value, dict):
                # expected directory (even empty dict {})
                if not path.is_dir():
                    if not is_protected(path):
                        warnings.append(f"Shape: Expected directory missing for YAML node: {rel(path)}")
                # recurse into non-empty dicts
                if value:
                    check_shape(value, yaml_path)

check_shape(main)

# ── Final report ──────────────────────────────────────────────────────

report = {
    "errors": errors,
    "warnings": warnings,
    "ok": ok,
}

REPORT_FILE = REPO / "ssot_validation_report.json"
REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("=" * 70)
print("STATIC SSoT VALIDATION COMPLETE — SSoT v4.2 / META v4.2")
print("=" * 70)
print(f"Errors:   {len(errors)}")
print(f"Warnings: {len(warnings)}")
print(f"OK notes: {len(ok)}")
print("-" * 70)
print(f"Full report written to: {REPORT_FILE}")
print("-" * 70)
print("VALIDATION " + ("FAILED" if errors else "PASSED"))
