# -*- coding: utf-8 -*-
"""
===============================================================================
Static SSoT Validator v4.1 — unified_structure_subatomic.yaml + META YAML
Fast, deterministic, zero side-effects. Designed for Agentic-Workflow.
===============================================================================

Validates the LIVE repository structure (no phases, no rewrites) against:

  - unified_structure_subatomic.yaml       (SSoT v4.1 – main)
  - unified_structure_subatomic_meta.yaml  (META v4.1 – invariants)

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
  - K12: No cognitive fillers in L5_safety (only P4_safety)
  - K13: Semantic cache presence + forbidden locations
  - K14: Protected paths respected (no spurious errors)
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
DOMAIN_ROOT_MAP: Dict[str, str] = {
    "agentic_core": "01_agentic_core",
    "schemas": "02_schemas",
    "runtime": "03_runtime",
    "prompt_governance": "04_prompt_governance",
    "config": "05_config",
    "data": "06_data",
    "observability": "07_observability",
    "scripts": "08_scripts",
    "apps_lic": "09_apps/apps_lic",
    "apps_rg": "09_apps/apps_rg",
    "tests": "10_tests",
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

# ── K12 – No cognitive fillers in L5_safety (only P4_safety) ──────────

cognitive_domains = ["agentic_core", "apps_lic", "apps_rg"]
for domain in cognitive_domains:
    root = get_domain_root(domain)
    if not root.exists():
        continue
    l5 = root / "L5_safety"
    if not l5.exists():
        continue
    # Allowed: P4_safety phase + safety-specific folders (guardrails, pii)
    allowed_l5_children = {"P4_safety", "guardrails", "pii", "__init__.py", "__pycache__"}
    for child in l5.iterdir():
        if child.is_dir() and child.name not in allowed_l5_children:
            err(f"K12: Disallowed folder '{child.name}' under L5_safety in {domain}: {rel(child)}")

# ── K13 – Semantic cache rules: required + forbidden locations ────────

semantic_rules = meta["semantic_cache_rules"]
req_files = semantic_rules["required_files"]
req_locs = semantic_rules["required_locations"]
forbidden_locs = semantic_rules["forbidden_locations"]

# required locations & files
for domain in cognitive_domains:
    root = get_domain_root(domain)
    if not root.exists():
        continue

    for loc in req_locs:
        # Example loc: "L1_cognition/P1_retrieve"
        sc_dir = root / loc / "semantic_cache"
        if not sc_dir.exists():
            err(f"K13: Missing semantic_cache dir at {rel(sc_dir)}")
            continue

        for f in req_files:
            fpath = sc_dir / f
            if not fpath.exists():
                err(f"K13: Missing semantic_cache file '{f}' at {rel(sc_dir)}")

# forbidden locations (glob patterns)
for pattern in forbidden_locs:
    # Patterns are repo-relative
    for p in REPO.glob(pattern):
        # if a matching path (or its descendants) contains semantic_cache
        if "semantic_cache" in p.parts or any("semantic_cache" in c.parts for c in p.rglob("*")):
            err(f"K13: Forbidden semantic_cache location under '{pattern}': {rel(p)}")

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
    extra_groups = existing_groups - required_groups - {"__pycache__", "logic"}  # allow 'logic' as an extra bucket

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
print("STATIC SSoT VALIDATION COMPLETE — SSoT v4.1 / META v4.1")
print("=" * 70)
print(f"Errors:   {len(errors)}")
print(f"Warnings: {len(warnings)}")
print(f"OK notes: {len(ok)}")
print("-" * 70)
print(f"Full report written to: {REPORT_FILE}")
print("-" * 70)
print("VALIDATION " + ("FAILED" if errors else "PASSED"))
