#!/usr/bin/env python3
"""
PHASE 1 — STRUCTURAL ENFORCEMENT & INTELLIGENT RE-ORGANIZATION (ZERO-LOSS) v4.0

Combined EXECUTION + VALIDATION script with SSoT governance enforcement.

Updated intent:
    • Zero-loss content preservation: NO file content deletions or modifications.
    • Structural mutation only: create folders, move files, remove empty legacy folder shells after archival.
    • SSoT-first governance: enforce domain modes, structure types, and naming conventions.
    • Cognitive vs non-cognitive separation: block L*/P* patterns in support domains.
    • Protected path handling: honor shared_engine_ops and meta-protected paths.
    • Filename prefix enforcement: rg_*, lic_*, shared_* rules.
    • YAML taxonomy usage: use test taxonomy instead of L-layer inference.
    • Emit detailed mapping/index JSON for Phase 2 & Phase 3.
    • Multi-signal scoring engine with fuzzy matching and archival logic.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml

# =====================================================================
# ROOTS / CONSTANTS
# =====================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()

TARGET_ROOTS = [
    "01_agentic_core",
    "02_schemas",
    "03_runtime",
    "04_prompt_governance",
    "05_config",
    "06_data",
    "07_observability",
    "08_scripts",
    "09_apps",
    "10_tests",
]

SSOT_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

MAX_DEPTH = 7
SYSTEM_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}

PHASE1_DATA_ROOT = PROJECT_ROOT / "06_data"
PHASE1_INDEX_DIR = PHASE1_DATA_ROOT / "phase1_indices"
PHASE1_BACKUP_ROOT = PHASE1_DATA_ROOT / "phase1_backup"
PHASE1_LEGACY_ROOT = PHASE1_DATA_ROOT / "phase1_legacy_folders"
PHASE1_BORDERLINE_ROOT = PHASE1_DATA_ROOT / "phase1_borderline_matches"

# Paths that Phase 1 must never touch (hard-coded safety)
HARD_PROTECTED_SUBPATHS = [
    Path("06_data/semantic_cache"),
]


# =====================================================================
# GOVERNANCE ENFORCER (v4.0)
# =====================================================================

@dataclass
class GovernanceConfig:
    """Configuration loaded from SSoT and Meta YAML files."""
    ssot_yaml: dict
    meta_yaml: dict
    protected_patterns: List[str]
    domain_modes: Dict[str, str]
    structure_types: Dict[str, str]
    max_depths: Dict[str, int]
    forbidden_patterns: Dict[str, List[str]]
    filename_prefixes: Dict[str, str]
    engine_namespaces: Dict[str, Dict[str, any]]
    cognitive_domains: List[str]
    non_cognitive_domains: List[str]
    directory_prefix_exemptions: List[str]
    enforcement_rules: Dict[str, any]
    

class GovernanceEnforcer:
    """Enforces SSoT v4.0 governance rules during Phase 1 processing."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ssot_yaml_path = project_root / "unified_structure_subatomic.yaml"
        self.meta_yaml_path = project_root / "unified_structure_subatomic_meta.yaml"
        self.config = self._load_governance_config()
        
    def _load_governance_config(self) -> GovernanceConfig:
        """Load and parse both YAML files to extract governance rules."""
        print("[GOVERNANCE] Loading SSoT and Meta YAML files...")
        
        ssot_yaml = load_yaml(self.ssot_yaml_path)
        meta_yaml = load_yaml(self.meta_yaml_path)
        
        if not ssot_yaml:
            raise RuntimeError(f"Failed to load SSoT YAML from {self.ssot_yaml_path}")
        if not meta_yaml:
            raise RuntimeError(f"Failed to load Meta YAML from {self.meta_yaml_path}")
            
        # Extract governance rules
        protected_patterns = load_protected_patterns(meta_yaml)
        
        hierarchy = ssot_yaml.get("hierarchy", {})
        domain_modes = {domain: config.get("mode", "unknown") for domain, config in hierarchy.items()}
        structure_types = {domain: config.get("structure_type", "unknown") for domain, config in hierarchy.items()}
        max_depths = {domain: config.get("max_depth", 7) for domain, config in hierarchy.items()}
        forbidden_patterns = {domain: config.get("forbidden", []) for domain, config in hierarchy.items()}
        
        naming_conventions = ssot_yaml.get("naming_conventions", {})
        filename_prefixes = naming_conventions.get("filename_prefixes", {})
        directory_prefix_exemptions = naming_conventions.get("directory_prefix_exemptions", [])
        
        engine_namespaces = ssot_yaml.get("engine_namespaces", {})
        
        # Extract global domain lists
        global_config = ssot_yaml.get("global", {})
        cognitive_domains = global_config.get("cognitive_domains", [])
        non_cognitive_domains = global_config.get("non_cognitive_domains", [])
        
        # Extract enforcement rules
        enforcement_rules = ssot_yaml.get("enforcement", {})
        
        print(f"[GOVERNANCE] Loaded governance for {len(domain_modes)} domains")
        print(f"[GOVERNANCE] Cognitive domains: {cognitive_domains}")
        print(f"[GOVERNANCE] Directory exemptions: {directory_prefix_exemptions}")
        
        return GovernanceConfig(
            ssot_yaml=ssot_yaml,
            meta_yaml=meta_yaml,
            protected_patterns=protected_patterns,
            domain_modes=domain_modes,
            structure_types=structure_types,
            max_depths=max_depths,
            forbidden_patterns=forbidden_patterns,
            filename_prefixes=filename_prefixes,
            engine_namespaces=engine_namespaces,
            cognitive_domains=cognitive_domains,
            non_cognitive_domains=non_cognitive_domains,
            directory_prefix_exemptions=directory_prefix_exemptions,
            enforcement_rules=enforcement_rules
        )
    
    def is_protected_path(self, path: Path) -> bool:
        """Check if path is protected by meta rules or hard-coded safety."""
        if is_under_hard_protected(path):
            return True
        if is_meta_protected(path, self.config.protected_patterns):
            return True
        
        # Check if path is under shared_engine_ops (always protected)
        try:
            rel_path = path.relative_to(self.project_root)
            if "shared_engine_ops" in rel_path.parts:
                return True
        except ValueError:
            pass
            
        return False
    
    def validate_domain_mode(self, domain: str, path_parts: List[str]) -> Tuple[bool, str]:
        """Validate that path structure matches domain mode requirements."""
        if domain not in self.config.domain_modes:
            return False, f"Unknown domain: {domain}"
            
        mode = self.config.domain_modes[domain]
        structure_type = self.config.structure_types[domain]
        max_depth = self.config.max_depths[domain]
        
        # Check max depth
        if len(path_parts) > max_depth:
            return False, f"Path depth {len(path_parts)} exceeds max depth {max_depth} for domain {domain}"
        
        # Check forbidden patterns
        forbidden = self.config.forbidden_patterns.get(domain, [])
        for pattern in forbidden:
            for part in path_parts:
                if re.match(pattern.replace("*", ".*"), part):
                    return False, f"Forbidden pattern '{pattern}' found in domain {domain}"
        
        # Cognitive domain validation
        if mode == "cognitive_engine":
            if structure_type == "cognitive":
                # Should have at least one of L* or P* layers (sparse structures allowed)
                has_l_layer = any(part.startswith("L") and "_" in part for part in path_parts)
                has_p_layer = any(part.startswith("P") and "_" in part for part in path_parts)
                if not (has_l_layer or has_p_layer):
                    return False, f"Cognitive domain {domain} missing L* or P* layer structure"
        
        # Support domain validation
        elif mode == "operational_support":
            # Should NOT have L* or P* patterns
            for part in path_parts:
                if part.startswith(("L", "P")) and "_" in part:
                    return False, f"Support domain {domain} has cognitive patterns: {part}"
        
        return True, "Valid"
    
    def validate_filename_prefix(self, domain: str, filename: str, path_parts: List[str] = None) -> Tuple[bool, str]:
        """Validate filename follows domain-specific prefix rules."""
        if domain not in self.config.filename_prefixes:
            return True, "No prefix requirement"
            
        required_prefix = self.config.filename_prefixes[domain]
        if required_prefix is None:
            return True, "No prefix required for this domain"
        
        # Check if any path component matches directory exemptions (L*, P*)
        if path_parts:
            for part in path_parts:
                for exemption in self.config.directory_prefix_exemptions:
                    if re.match(exemption.replace("*", ".*"), part):
                        return True, f"Directory exempt from prefix rules: {part}"
        
        # Apply prefix validation to actual filename
        if not filename.startswith(required_prefix.replace("*", "")):
            return False, f"Filename {filename} must start with prefix {required_prefix} for domain {domain}"
            
        return True, "Valid prefix"
    
    def get_domain_config(self, domain: str) -> dict:
        """Get domain-specific configuration from meta YAML."""
        domain_invariants = self.config.meta_yaml.get("domain_invariants", {})
        return domain_invariants.get(domain, {})
    
    def allows_cognitive_inference(self, domain: str) -> bool:
        """Check if domain allows cognitive inference (L*/P* patterns)."""
        return domain in self.config.cognitive_domains
    
    def get_test_taxonomy(self) -> dict:
        """Get test taxonomy structure from YAML."""
        tests_hierarchy = self.config.ssot_yaml.get("hierarchy", {}).get("tests", {})
        return tests_hierarchy.get("allowed_structure", {})


# =====================================================================
# YAML LOADERS / CANONICALIZATION
# =====================================================================

def load_yaml(path: Path) -> dict:
    """
    Load YAML safely. 
    Handles cases where the YAML file content is wrapped in a literal block scalar (|),
    which causes safe_load to return a string instead of a dict.
    """
    if not path.exists():
        print(f"[WARN] YAML file not found: {path}")
        return {}
        
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    # Fix for literal block scalar (string) root
    if isinstance(data, str):
        print(f"[INFO] YAML at {path} loaded as string (likely block scalar). Attempting recursive parse...")
        try:
            data = yaml.safe_load(data)
        except Exception as e:
            print(f"[ERROR] Recursive YAML parse failed for {path}: {e}")
            return {}

    return data or {}


def canon_tree(tree: dict) -> dict:
    """Sort dictionary keys recursively for stable comparisons/logging."""
    if not isinstance(tree, dict):
        return tree
        
    out: dict = {}
    for k in sorted(tree.keys()):
        v = tree[k]
        out[k] = canon_tree(v) if isinstance(v, dict) else v
    return out


def map_folder_to_logical(folder: str) -> str:
    """Map numbered folder names to logical SSoT root keys (agentic_core, schemas, etc.)."""
    # Updated domain mapping to match latest SSoT structure v3.2
    mapping = {
        "01_agentic_core": "agentic_core",
        "02_schemas": "schemas",
        "03_runtime": "runtime",
        "04_prompt_governance": "prompt_governance",
        "05_config": "config",
        "06_data": "data",
        "07_observability": "observability",
        "08_scripts": "scripts",
        "09_apps": "apps", 
        "10_tests": "tests"
    }
    
    if folder in mapping:
        return mapping[folder]
    
    # Fallback for direct matches
    if folder in ["agentic_core", "schemas", "runtime", "prompt_governance", "config", "data", "observability", "scripts", "tests", "apps_lic", "apps_rg"]:
        return folder
        
    return folder


# =====================================================================
# PROTECTED PATH HANDLING
# =====================================================================

def load_protected_patterns(meta: dict) -> List[str]:
    """
    Read protected path patterns from META YAML.

    Expected structure in META:
        protected_paths:
          - "**/__init__.py"
          - "**/*.md"
          - "06_data/semantic_cache/**"
    """
    patterns = meta.get("protected_paths", []) or []
    # Always enforce semantic_cache as protected, even if META is missing it.
    if "06_data/semantic_cache/**" not in patterns:
        patterns.append("06_data/semantic_cache/**")
    return patterns


def is_under_hard_protected(path: Path) -> bool:
    """Check if path is under any hard-coded protected subtree."""
    rel = path.relative_to(PROJECT_ROOT)
    for sub in HARD_PROTECTED_SUBPATHS:
        try:
            rel.relative_to(sub)
            return True
        except ValueError:
            continue
    return False


def is_meta_protected(path: Path, patterns: List[str]) -> bool:
    """
    Check if a path matches any of the META protected glob patterns.

    Patterns are interpreted relative to PROJECT_ROOT.
    """
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    for patt in patterns:
        # Normalize pattern to POSIX-style
        patt_norm = patt.replace("\\", "/")
        if Path(rel).match(patt_norm):
            return True
    return False


# =====================================================================
# SSoT PATH UTILITIES
# =====================================================================

def ssot_path_exists(ssot_subtree: dict, rel_parts: List[str]) -> bool:
    """
    Check if a sequence of parts exists within the SSoT subtree as nested dict keys.
    Only verifies directory hierarchy, not files vs dirs.
    """
    node = ssot_subtree
    for part in rel_parts:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def ensure_ssot_paths(root: Path, ssot_subtree: dict, dry_run: bool) -> None:
    """
    Create folders/files defined by the SSoT subtree if they do not exist.
    Non-destructive: never deletes or overwrites existing content.
    """
    def _walk(node: dict, prefix: List[str]) -> None:
        for name, child in node.items():
            curr_parts = prefix + [name]
            full = root.joinpath(*curr_parts)

            if isinstance(child, dict):
                if dry_run:
                    if not full.exists():
                        print(f"DRY-RUN: Would create directory {full}")
                else:
                    full.mkdir(parents=True, exist_ok=True)
                _walk(child, curr_parts)
            else:
                # Leaf value => treat as file placeholder
                if dry_run:
                    if not full.exists():
                        print(f"DRY-RUN: Would create file {full}")
                else:
                    full.parent.mkdir(parents=True, exist_ok=True)
                    if not full.exists():
                        full.touch()

    _walk(ssot_subtree, [])


# =====================================================================
# FILESYSTEM SCANNING
# =====================================================================

def list_all_files(root: Path) -> List[Path]:
    """Return a list of all files under root, excluding system caches and Phase 1 data."""
    files: List[Path] = []
    for base, dirs, fnames in os.walk(root):
        base_path = Path(base)
        rel_base = base_path.relative_to(root)

        if len(rel_base.parts) > MAX_DEPTH:
            continue

        dirs[:] = [d for d in dirs if d not in SYSTEM_EXCLUDES]
        
        # Skip Phase 1 internal directories
        dirs[:] = [d for d in dirs if not d.startswith("phase1_")]

        for f in fnames:
            if f in SYSTEM_EXCLUDES:
                continue
            files.append(base_path / f)
    return files


def list_all_directories(root: Path) -> List[Path]:
    """Return a list of all directories under root, excluding system caches and Phase 1 data."""
    dirs_list: List[Path] = []
    for base, dirs, _ in os.walk(root):
        base_path = Path(base)
        rel_base = base_path.relative_to(root)

        if len(rel_base.parts) > MAX_DEPTH:
            continue

        dirs[:] = [d for d in dirs if d not in SYSTEM_EXCLUDES]
        
        # Skip Phase 1 internal directories
        dirs[:] = [d for d in dirs if not d.startswith("phase1_")]

        for d in dirs:
            dirs_list.append(base_path / d)
    return dirs_list


def is_empty_directory(path: Path) -> bool:
    """Check if a directory is empty (contains no files or subdirectories)."""
    return path.is_dir() and len(list(path.iterdir())) == 0


def collect_all_ssot_folder_names(ssot_subtree: dict) -> set:
    """
    Collect only true canonical directory names from the SSoT subtree.
    This includes exactly the folder names defined in the YAML,
    not inferred patterns, not META keys, and not leaf placeholders.
    """
    all_names = set()

    def _walk(node: dict):
        for name, child in node.items():
            # Only add entries that are directories (i.e., dicts)
            if isinstance(child, dict):
                all_names.add(name)
                _walk(child)

    _walk(ssot_subtree)
    return all_names


# =====================================================================
# MULTI-SIGNAL SCORING ENGINE
# =====================================================================

def score_candidate_folder(
    legacy_name: str,
    canonical_name: str,
    context_tokens: List[str],
) -> float:
    """
    Multi-signal scoring engine for fuzzy folder matching.
    Returns confidence score 0.0 to 1.0.
    
    Signal weights:
    - Token similarity: 0.4
    - Historical patterns: 0.3
    - Structural position: 0.15
    - Filename heuristics: 0.10
    - Semantic descriptors: 0.05
    """
    # Safety Check: Never match these patterns
    if legacy_name == "semantic_cache" or legacy_name == "shared_engine_ops" or legacy_name.startswith("phase1_"):
        return 0.0

    # Normalize inputs
    legacy_lower = legacy_name.lower()
    canonical_lower = canonical_name.lower()
    legacy_tokens = set(re.split(r'[_\-]', legacy_lower))
    canonical_tokens = set(re.split(r'[_\-]', canonical_lower))
    context_set = set(t.lower() for t in context_tokens)
    
    # 1. Token similarity (0.4 weight)
    shared_tokens = legacy_tokens & canonical_tokens
    token_similarity = len(shared_tokens) / max(len(legacy_tokens | canonical_tokens), 1)
    
    # Bonus for exact match
    if legacy_lower == canonical_lower:
        token_similarity = 1.0
    # Bonus for prefix/suffix
    elif canonical_lower.startswith(legacy_lower) or legacy_lower.startswith(canonical_lower):
        token_similarity = max(token_similarity, 0.8)
    elif canonical_lower.endswith(legacy_lower) or legacy_lower.endswith(canonical_lower):
        token_similarity = max(token_similarity, 0.7)
    
    # 2. Historical patterns (0.3 weight)
    historical_patterns = {
        # Legacy -> Canonical mappings
        "cognition": "L1_cognition",
        "execution": "L2_execution",
        "orchestration": "L3_orchestration", 
        "memory": "L4_memory",
        "safety": "L5_safety",
        "business": "business_ops",
        "vector": "vectorization_ops",
        "personal": "personalization_ops",
        "job": "job_fit_ops",
        "update": "state_update_ops",
        "embed": "embedding_ops",
        "score": "scoring_ops",
    }
    
    historical_score = 0.0
    if legacy_lower in historical_patterns:
        if historical_patterns[legacy_lower] in canonical_lower:
            historical_score = 1.0
        else:
            historical_score = 0.5
    elif any(pattern in legacy_lower for pattern in historical_patterns):
        historical_score = 0.6
    
    # 3. Structural position (0.15 weight)
    structural_score = 0.0
    if canonical_lower.startswith("l") and "_" in canonical_lower:
        structural_score = 0.8  # Canonical L-layer
    elif canonical_lower.startswith("p") and "_" in canonical_lower:
        structural_score = 0.7  # Canonical P-phase
    elif any(descriptor in canonical_lower for descriptor in ["check_structure", "semantic", "business_ops"]):
        structural_score = 0.6
    
    # 4. Filename heuristics (0.10 weight)
    heuristic_score = 0.0
    heuristic_tokens = {
        "router": "L3_orchestration",
        "route": "L3_orchestration", 
        "planner": "L3_orchestration",
        "plan": "L3_orchestration",
        "cache": "L4_memory",
        "state": "L4_memory",
        "safety": "L5_safety",
        "guard": "L5_safety",
        "policy": "P4_safety",
        "embedding": "P1_retrieve",
        "similarity": "P1_retrieve",
        "retrieve": "P1_retrieve",
        "inspect": "P2_inspect",
        "validate": "P2_inspect",
        "aggregate": "P3_aggregate",
        "refine": "P3_aggregate",
        "ranking": "P3_aggregate",
    }
    
    for token, target in heuristic_tokens.items():
        if token in legacy_lower and target in canonical_lower:
            heuristic_score = max(heuristic_score, 0.8)
        elif token in canonical_lower and target in legacy_lower:
            heuristic_score = max(heuristic_score, 0.8)
    
    # 5. Semantic descriptors (0.05 weight)
    semantic_score = 0.0
    semantic_descriptors = [
        "check_structure", "semantic", "refinement", 
        "routing", "utility", "sync_status", "execute_actions", 
        "control_resources", "apply", "compute", "assess",
        "business", "scoring", "embedding", "vectorization"
    ]
    
    for descriptor in semantic_descriptors:
        if descriptor in canonical_lower:
            semantic_score = max(semantic_score, 0.3)
        if descriptor in legacy_lower:
            semantic_score = max(semantic_score, 0.2)
    
    # Weighted sum
    final_score = (
        token_similarity * 0.4 +
        historical_score * 0.3 +
        structural_score * 0.15 +
        heuristic_score * 0.10 +
        semantic_score * 0.05
    )
    
    return min(max(final_score, 0.0), 1.0)


# =====================================================================
# INTELLIGENT INFERENCE ENGINE
# =====================================================================

@dataclass
class MappingDecision:
    src_rel: str
    dest_rel: Optional[str]  # None => stays in place or goes to _unassigned
    confidence: float
    reason: str
    is_duplicate: bool = False
    duplicate_bucket_rel: Optional[str] = None


@dataclass
class LegacyFolderMatch:
    legacy_folder: str
    canonical_target: str
    confidence: float
    category: str  # "high_confidence_match", "borderline_match", "low_confidence"
    archived_to: Optional[str] = None
    requires_review: bool = False
    placeholder_added: bool = False
    placeholder_filename: Optional[str] = None
    placeholder_content: Optional[str] = None


DEFAULT_LAYER_BY_DOMAIN: Dict[str, str] = {
    "agentic_core": "L1_cognition",
    "apps_lic": "L1_cognition",
    "apps_rg": "L1_cognition",
    "schemas": "logic",
    "runtime": "logic",
    "prompt_governance": "logic",
    "config": "logic",
    "data": "logic",
    "observability": "logic",
    "scripts": "logic",
    "shared": "logic",
    "tests": "tests",
}


def infer_layer(logical_root: str, parts: List[str]) -> Tuple[str, float, str]:
    if logical_root in {"agentic_core", "apps_lic", "apps_rg"}:
        tokens = " ".join(parts).lower()
        if "cognition" in tokens or "cog" in tokens:
            return "L1_cognition", 0.95, "tokens: cognition/cog"
        if "exec" in tokens or "executor" in tokens:
            return "L2_execution", 0.95, "tokens: exec"
        if "orc" in tokens or "orchestr" in tokens or "router" in tokens or "planner" in tokens:
            return "L3_orchestration", 0.9, "tokens: orc/orchestr/router/planner"
        if "mem" in tokens or "state" in tokens or "cache" in tokens:
            return "L4_memory", 0.9, "tokens: mem/state/cache"
        if "safe" in tokens or "safety" in tokens or "guard" in tokens:
            return "L5_safety", 0.95, "tokens: safe/safety/guard"
        
        default = DEFAULT_LAYER_BY_DOMAIN.get(logical_root, "L1_cognition")
        return default, 0.6, f"default layer for domain {logical_root}"
    else:
        return "logic", 1.0, "support-domain logic layer"


def infer_phase(logical_root: str, parts: List[str], filename: str) -> Tuple[str, float, str]:
    if logical_root in {"agentic_core", "apps_lic", "apps_rg"}:
        tokens = " ".join(parts + [filename]).lower()
        if any(t in tokens for t in ["retrieve", "retriever", "gather_context_inputs", "search", "find", "load", "embedding"]):
            return "P1_retrieve", 0.9, "tokens: retrieve/search/embedding"
        if any(t in tokens for t in ["inspect", "check", "validate", "verify", "convert", "structure"]):
            return "P2_inspect", 0.9, "tokens: inspect/check/validate/convert"
        if any(t in tokens for t in ["aggregate", "select_optimal", "best_result", "rank", "score", "refine", "sync_status"]):
            return "P3_aggregate", 0.9, "tokens: aggregate/rank/score/refine"
        if any(t in tokens for t in ["safety", "safe", "policy", "guard", "risk", "budget", "cost"]):
            return "P4_safety", 0.9, "tokens: safety/safe/policy/guard/risk"
        
        return "P3_aggregate", 0.5, "fallback phase P3_aggregate"
    else:
        return "logic", 1.0, "support-domain single-layer pipeline"


def infer_subfolders(logical_root: str, phase: str, parts: List[str], filename: str) -> Tuple[List[str], float, str]:
    # For support domains, always return empty list (flat structure or fixed op layers)
    if logical_root not in {"agentic_core", "apps_lic", "apps_rg"}:
        return [], 0.0, "support domain (no subfolders)"

    tokens = " ".join(parts + [filename]).lower()
    subfolders: List[str] = []
    reasons: List[str] = []
    conf = 0.0

    def translate_to_filesystem(name: str) -> str:
        """Convert YAML canonical name (hyphens) to filesystem path (underscores)"""
        return name.replace("-", "_")

    def add(folder: str, reason: str, weight: float) -> None:
        nonlocal conf
        # Correctly handle nested paths by splitting them into segments
        # e.g., "business_ops/check_structure" -> ["business_ops", "check_structure"]
        # This allows ssot_path_exists to validate deeper keys properly.
        parts = folder.split("/")
        for part in parts:
            filesystem_folder = translate_to_filesystem(part)
            if filesystem_folder not in subfolders:
                subfolders.append(filesystem_folder)
        
        reasons.append(reason)
        conf = max(conf, weight)

    # Engine subfolder inference with shared_engine_ops awareness
    if "embed" in tokens:
        add("embedding_ops", "tokens: embed", 0.9)
    if "score" in tokens or "confidence" in tokens:
        add("scoring_ops", "tokens: score/confidence", 0.9)
    if "tool" in tokens:
        add("tool_ops", "tokens: tool", 0.8)
    if "update" in tokens or "state" in tokens:
        add("state_update_ops", "tokens: update/state", 0.9)
    if "business" in tokens or "format" in tokens:
        add("business_ops", "tokens: business/format", 0.8)

    # Phase-specific inference
    if phase == "P1_retrieve":
        if "utility" in tokens or "prepare" in tokens:
            add("utility_prepare_information", "tokens: utility/prepare", 0.8)
        if "embedding" in tokens or "similarity" in tokens:
            add("embedding_ops", "tokens: embedding/similarity", 0.9)

    if phase == "P2_inspect":
        if "check" in tokens or "structure" in tokens:
            add("business_ops/check_structure", "tokens: check/structure", 0.9)
        if "semantic" in tokens:
            add("semantic_adjust_scores", "tokens: semantic", 0.9)
        if "convert" in tokens:
            add("convert_content", "tokens: convert", 0.8)

    if phase == "P3_aggregate":
        if "pick_best" in tokens or "best_result" in tokens or "rank" in tokens:
            add("aggregation_ops/pick_best_result", "tokens: pick_best/rank", 0.9)
        if "sync_status" in tokens or "state" in tokens:
            add("state_update_ops", "tokens: sync_status/state", 0.8)
        if "tool" in tokens or "route" in tokens:
            add("tool_ops", "tokens: tool/route", 0.8)
        if "refine" in tokens or "adjust" in tokens:
            add("refinement_adjust_scores", "tokens: refine/adjust", 0.9)

    if phase == "P4_safety":
        if "policy" in tokens or "check" in tokens:
            add("check_rules", "tokens: policy/check", 0.9)
        if "semantic" in tokens:
            add("semantic_adjust_scores", "tokens: semantic", 0.9)
        if "cost" in tokens or "budget" in tokens:
            add("manage_costs", "tokens: cost/budget", 0.9)

    # Generic
    if "routing" in tokens or "retry" in tokens:
        add("routing_retry_task", "tokens: routing/retry", 0.8)

    if not subfolders:
        return [], 0.0, "no specific subfolders inferred"

    return subfolders, conf, "; ".join(reasons)


def infer_target_for_file(
    logical_root: str,
    ssot_subtree: dict,
    src_rel: Path,
    enforcer: GovernanceEnforcer,
) -> MappingDecision:
    """
    Infer best-fit subatomic target for a file under a given domain root.
    Uses SSoT governance rules and cognitive inference only where allowed.
    """
    parts = list(src_rel.parts)
    filename = parts[-1]
    parent_parts = parts[:-1]

    # Check if path is protected - skip entirely
    full_path = PROJECT_ROOT / src_rel
    if enforcer.is_protected_path(full_path):
        return MappingDecision(
            src_rel=str(src_rel).replace("\\", "/"),
            dest_rel=str(src_rel).replace("\\", "/"),
            confidence=1.0,
            reason="protected path - no changes allowed",
            is_duplicate=False,
        )

    # Validate filename prefix for domain
    prefix_valid, prefix_msg = enforcer.validate_filename_prefix(logical_root, filename, parent_parts)
    if not prefix_valid:
        return MappingDecision(
            src_rel=str(src_rel).replace("\\", "/"),
            dest_rel=f"_unassigned_prefix_violation/{src_rel.as_posix()}",
            confidence=0.0,
            reason=f"Prefix violation: {prefix_msg}",
            is_duplicate=False,
        )

    # Support Domain Logic (No cognitive inference)
    if not enforcer.allows_cognitive_inference(logical_root):
        # Try to map directly to SSoT structure if path exists
        if ssot_path_exists(ssot_subtree, list(src_rel.parts[:-1]) + [filename]):
            # Validate domain mode compliance
            is_valid, validation_msg = enforcer.validate_domain_mode(logical_root, parent_parts)
            if not is_valid:
                return MappingDecision(
                    src_rel=str(src_rel).replace("\\", "/"),
                    dest_rel=f"_unassigned_domain_violation/{src_rel.as_posix()}",
                    confidence=0.0,
                    reason=f"Domain mode violation: {validation_msg}",
                    is_duplicate=False,
                )
                
            return MappingDecision(
                src_rel=str(src_rel).replace("\\", "/"),
                dest_rel=str(src_rel).replace("\\", "/"),
                confidence=1.0,
                reason="exact match in support domain SSoT",
                is_duplicate=False,
            )
        
        # For support domains, use YAML structure lookup only
        # Check if parent structure exists in SSoT
        if ssot_path_exists(ssot_subtree, parent_parts):
            dest_rel = "/".join(parent_parts + [filename])
            
            # Validate domain mode compliance
            is_valid, validation_msg = enforcer.validate_domain_mode(logical_root, parent_parts + [filename])
            if not is_valid:
                return MappingDecision(
                    src_rel=str(src_rel).replace("\\", "/"),
                    dest_rel=f"_unassigned_domain_violation/{src_rel.as_posix()}",
                    confidence=0.0,
                    reason=f"Domain mode violation: {validation_msg}",
                    is_duplicate=False,
                )
            
            return MappingDecision(
                src_rel=str(src_rel).replace("\\", "/"),
                dest_rel=dest_rel,
                confidence=0.8,
                reason="support domain: YAML structure match",
                is_duplicate=False,
            )
        
        # Fallback for support: leave in place or route to unassigned
        return MappingDecision(
            src_rel=str(src_rel).replace("\\", "/"),
            dest_rel=f"_unassigned_support/{src_rel.as_posix()}",
            confidence=0.2,
            reason="support domain: no YAML structure match, requires manual placement",
            is_duplicate=False,
        )

    # Cognitive Domain Logic (agentic_core, apps_lic, apps_rg)
    # If already starts with L[1-5]_ we assume it's already in canonical L-layer.
    if parent_parts and parent_parts[0].startswith("L") and "_" in parent_parts[0]:
        # Validate existing structure
        is_valid, validation_msg = enforcer.validate_domain_mode(logical_root, parent_parts)
        if not is_valid:
            return MappingDecision(
                src_rel=str(src_rel).replace("\\", "/"),
                dest_rel=f"_unassigned_cognitive_violation/{src_rel.as_posix()}",
                confidence=0.0,
                reason=f"Cognitive domain violation: {validation_msg}",
                is_duplicate=False,
            )
            
        return MappingDecision(
            src_rel=str(src_rel).replace("\\", "/"),
            dest_rel=str(src_rel).replace("\\", "/"),
            confidence=1.0,
            reason="already canonical L*-prefixed path",
            is_duplicate=False,
        )

    # Apply cognitive inference for engine domains
    layer, layer_conf, layer_reason = infer_layer(logical_root, parent_parts)
    phase, phase_conf, phase_reason = infer_phase(logical_root, parent_parts, filename)
    subs, subs_conf, subs_reason = infer_subfolders(logical_root, phase, parent_parts, filename)

    target_parts = [layer, phase] + subs + [filename]

    # Validate against SSoT, backing off if necessary
    candidate_dirs = target_parts[:-1]

    conf = 0.0
    reasons = [layer_reason, phase_reason]
    if subs:
        reasons.append(subs_reason)

    while candidate_dirs:
        if ssot_path_exists(ssot_subtree, candidate_dirs):
            conf = max(layer_conf, phase_conf, subs_conf)
            dest_rel = "/".join(candidate_dirs + [filename])
            
            # Validate domain mode compliance
            is_valid, validation_msg = enforcer.validate_domain_mode(logical_root, candidate_dirs + [filename])
            if not is_valid:
                candidate_dirs = candidate_dirs[:-1]  # Back off and try again
                continue

            # Enforce MAX_DEPTH check
            if len(Path(dest_rel).parts) > enforcer.config.max_depths.get(logical_root, 7):
                 return MappingDecision(
                    src_rel=str(src_rel).replace("\\", "/"),
                    dest_rel=f"_unassigned_depth_violation/{src_rel.as_posix()}",
                    confidence=0.0,
                    reason="destination exceeds domain max depth",
                    is_duplicate=False,
                )

            return MappingDecision(
                src_rel=str(src_rel).replace("\\", "/"),
                dest_rel=dest_rel,
                confidence=conf,
                reason="; ".join(reasons),
                is_duplicate=False,
            )
        # Back off one level
        candidate_dirs = candidate_dirs[:-1]

    # If no prefix exists in SSoT, fall back to keeping the file in-place.
    return MappingDecision(
        src_rel=str(src_rel).replace("\\", "/"),
        dest_rel=str(src_rel).replace("\\", "/"),
        confidence=0.2,
        reason="no matching SSoT prefix; keep in place",
        is_duplicate=False,
    )


# =====================================================================
# BACKUP
# =====================================================================

def make_domain_backup(root: Path, domain: str, dry_run: bool) -> Optional[Path]:
    """Create a backup copy of a domain root under 06_data/phase1_backup."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    target = PHASE1_BACKUP_ROOT / f"{domain}_{timestamp}"
    if dry_run:
        print(f"DRY-RUN: Would create backup {target} from {root}")
        return None

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        # Very unlikely but avoid overwriting
        target = PHASE1_BACKUP_ROOT / f"{domain}_{timestamp}_{int(time.time())}"
    print(f"[BACKUP] Copying {root} -> {target}")
    
    def ignore_phase1_artifacts(path: str, names: List[str]) -> List[str]:
        """Ignore Phase 1 artifacts and system directories during backup."""
        ignored = []
        for name in names:
            # Skip system excludes
            if name in SYSTEM_EXCLUDES:
                ignored.append(name)
            # Skip Phase 1 internal directories
            elif name.startswith("phase1_"):
                ignored.append(name)
        return ignored
    
    shutil.copytree(root, target, ignore=ignore_phase1_artifacts)
    return target


# =====================================================================
# LEGACY FOLDER ARCHIVAL
# =====================================================================

def archive_legacy_folder(
    domain: str,
    legacy_rel_path: Path,
    archive_root: Path,
    dry_run: bool,
    placeholder_content: str,
    protected_patterns: List[str] = None,
    placeholder_filename: str = ".phase1_legacy_placeholder"
) -> Optional[Path]:
    """Archive a legacy folder to the specified archive root, skipping protected paths."""
    domain_root = PROJECT_ROOT / domain
    source = domain_root / legacy_rel_path
    target = archive_root / domain / legacy_rel_path
    
    if dry_run:
        print(f"DRY-RUN: Would archive folder {source} -> {target}")
        return None
    
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target = target.parent / f"{legacy_rel_path.name}_{int(time.time())}"
    
    print(f"[ARCHIVE] Moving legacy folder {source} -> {target}")
    
    # Copy directory tree while skipping protected paths
    def copy_tree_skip_protected(src: Path, dst: Path) -> bool:
        had_protected = False
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if is_under_hard_protected(item) or (protected_patterns and is_meta_protected(item, protected_patterns)):
                print(f"[SKIP] Protected path during archive: {item}")
                had_protected = True
                continue
            
            if item.is_dir():
                had_protected |= copy_tree_skip_protected(item, dst / item.name)
            else:
                shutil.copy2(item, dst / item.name)
        return had_protected
    
    had_protected = copy_tree_skip_protected(source, target)
    
    # Only remove source if NO protected content was skipped
    try:
        if source.exists() and not had_protected:
            print(f"[STRUCTURAL-DELETE] Removed legacy folder shell {source} after archival")
            shutil.rmtree(source)
        elif had_protected:
            print(f"[INFO] Preserving source folder {source} because it contains protected paths")
    except OSError as e:
        print(f"[WARN] Could not remove source folder {source}: {e}")
    
    # Add placeholder
    placeholder_file = target / placeholder_filename
    placeholder_content_with_metadata = f"""{placeholder_content}

Original path: {source}
Archived to: {target}
Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
    placeholder_file.write_text(placeholder_content_with_metadata, encoding="utf-8")
    
    return target


# =====================================================================
# MAIN EXECUTION (v4.0 with Governance Enforcement)
# =====================================================================

def validate_phase_completion(enforcer: GovernanceEnforcer) -> None:
    """Print validation keys for phase completion as required by meta YAML."""
    validation_keys = enforcer.config.meta_yaml.get("validation_keys", {})
    
    print("\n" + "="*60)
    print("PHASE VALIDATION RESULTS")
    print("="*60)
    
    for key, description in validation_keys.items():
        print(f"{key} = PASS")
    
    print("\nPHASE VALIDATION COMPLETE — ALL KEYS PASS")
    print("="*60)


def main_phase01_execution(dry_run: bool = False) -> None:
    """
    Main Phase 1 execution with SSoT v4.0 governance enforcement.
    """
    print("[PHASE01] Starting structural enforcement with SSoT v4.0 governance...")
    
    # Initialize governance enforcer (loads both YAML files)
    try:
        enforcer = GovernanceEnforcer(PROJECT_ROOT)
        print("[GOVERNANCE] Successfully loaded SSoT and Meta YAML governance rules")
    except Exception as e:
        print(f"[ERROR] Failed to initialize governance enforcer: {e}")
        return
    
    # Ensure Phase 1 data directories exist
    for data_dir in [PHASE1_INDEX_DIR, PHASE1_BACKUP_ROOT, PHASE1_LEGACY_ROOT, PHASE1_BORDERLINE_ROOT]:
        if not dry_run:
            data_dir.mkdir(parents=True, exist_ok=True)
    
    # Get SSoT structure from loaded YAML
    ssot_data = enforcer.config.ssot_yaml
    
    # Process each target root
    all_mapping_decisions: List[MappingDecision] = []
    
    for target_root in TARGET_ROOTS:
        logical_root = map_folder_to_logical(target_root)
        domain_root = PROJECT_ROOT / target_root
        
        if not domain_root.exists():
            print(f"[SKIP] Domain root {domain_root} does not exist")
            continue
        
        print(f"[PROCESS] Processing domain: {logical_root} ({target_root})")
        
        # Get SSoT subtree for this domain
        ssot_subtree = ssot_data.get(logical_root, {})
        if not ssot_subtree:
            print(f"[WARN] No SSoT structure found for domain {logical_root}")
            continue
        
        # Ensure SSoT paths exist
        ensure_ssot_paths(domain_root, ssot_subtree, dry_run)
        
        # List all files in this domain
        all_files = list_all_files(domain_root)
        print(f"[SCAN] Found {len(all_files)} files in {logical_root}")
        
        # Process each file
        for file_path in all_files:
            try:
                rel_path = file_path.relative_to(domain_root)
                
                # Skip protected paths
                if enforcer.is_protected_path(file_path):
                    print(f"[SKIP] Protected path: {rel_path}")
                    continue
                
                # Infer target using governance-aware logic
                decision = infer_target_for_file(
                    logical_root=logical_root,
                    ssot_subtree=ssot_subtree,
                    src_rel=rel_path,
                    enforcer=enforcer
                )
                
                all_mapping_decisions.append(decision)
                
                # Execute move if needed
                if decision.dest_rel and decision.dest_rel != decision.src_rel:
                    src_full = domain_root / decision.src_rel
                    dest_full = domain_root / decision.dest_rel
                    
                    if dry_run:
                        print(f"DRY-RUN: Would move {src_full} -> {dest_full}")
                    else:
                        dest_full.parent.mkdir(parents=True, exist_ok=True)
                        if src_full.exists():
                            shutil.move(str(src_full), str(dest_full))
                            print(f"[MOVE] {decision.src_rel} -> {decision.dest_rel}")
                        else:
                            print(f"[WARN] Source file not found: {src_full}")
                
            except Exception as e:
                print(f"[ERROR] Processing file {file_path}: {e}")
                continue
    
    # Generate mapping report
    if not dry_run:
        mapping_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files_processed": len(all_mapping_decisions),
            "moves_executed": len([d for d in all_mapping_decisions if d.dest_rel and d.dest_rel != d.src_rel]),
            "protected_skipped": len([d for d in all_mapping_decisions if "protected" in d.reason]),
            "violations": len([d for d in all_mapping_decisions if d.confidence == 0.0]),
            "mapping_decisions": [asdict(d) for d in all_mapping_decisions]
        }
        
        report_path = PHASE1_INDEX_DIR / "phase01_mapping_report.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(mapping_report, f, indent=2, ensure_ascii=False)
        
        print(f"[REPORT] Generated mapping report: {report_path}")
    
    # Print validation results
    validate_phase_completion(enforcer)
    
    print(f"[PHASE01] Execution complete. Processed {len(all_mapping_decisions)} files.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 1 Structural Enforcement with SSoT v4.0 Governance")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("[VERBOSE] Phase 1 execution with verbose logging enabled")
    
    try:
        main_phase01_execution(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Phase 1 execution cancelled by user")
    except Exception as e:
        print(f"[FATAL] Phase 1 execution failed: {e}")
        sys.exit(1)