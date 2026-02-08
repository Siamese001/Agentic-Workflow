#!/usr/bin/env python3
"""
Agent Deduplication Analysis Pipeline — Phases 0-2

AST-based feature extraction, pairwise similarity, clustering, and
consolidation candidate identification for all ACTIVE agents.

Outputs:
  artifacts/dedup/active_agents_index.json
  artifacts/dedup/similarity/code_similarity.json
  artifacts/dedup/similarity/code_similarity.md
  artifacts/dedup/similarity/prompt_similarity.json
  artifacts/dedup/similarity/prompt_similarity.md
  artifacts/dedup/similarity/responsibility_similarity.md
  artifacts/dedup/similarity/dependency_overlap.md
  {DOCS_REPORTS_PLANS}/dedup_consolidation_plan.md   (SSOT Rule #0, ARTIFACT_ROUTING_MAP: plans)
  {DOCS_REPORTS_PLANS}/dedup_stop_sprawl_policy.md   (SSOT Rule #0, ARTIFACT_ROUTING_MAP: plans)

Path resolution: All paths imported from structure_blueprint_config.py.
No hardcoded docs/reports paths permitted.
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
Logger = logging.getLogger("dedup_analysis")

# ---------------------------------------------------------------------------
# SSOT Path Resolution (structure_blueprint_config.py)
# ---------------------------------------------------------------------------
# NO HARDCODED docs/reports PATHS — always import from blueprint.
try:
    from agentic_core.L5_safety.config.structure_blueprint_config import (
        AGENT_DISCOVERY_JSON,
        DOCS_REPORTS_PLANS,
        get_validated_project_root,
    )

    PROJECT_ROOT = get_validated_project_root()
    DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
except ImportError:
    # Fallback for standalone execution outside installed package
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"
    DOCS_REPORTS_PLANS = "docs/reports/plans"
    Logger.warning("[FALLBACK] Could not import structure_blueprint_config — using fallback paths")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEED = 42
OUT_DIR = PROJECT_ROOT / "artifacts" / "dedup"
SIM_DIR = OUT_DIR / "similarity"
# Constitutional Rule #0: plans/reports → DOCS_REPORTS_PLANS (from blueprint)
REPORTS_DIR = PROJECT_ROOT / DOCS_REPORTS_PLANS

CODE_SIM_THRESHOLD = 0.75
PROMPT_SIM_THRESHOLD = 0.80
RESPONSIBILITY_OVERLAP_THRESHOLD = 0.60

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentFeatures:
    """AST-extracted features for a single agent file."""
    agent_id: str
    class_name: str
    file_path: str
    layer: str
    # AST features
    imports: list[str] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    method_names: list[str] = field(default_factory=list)
    method_signatures: list[str] = field(default_factory=list)
    called_functions: list[str] = field(default_factory=list)
    class_attributes: list[str] = field(default_factory=list)
    # Prompt / responsibility
    docstring: str = ""
    prompt_strings: list[str] = field(default_factory=list)
    responsibility_keywords: list[str] = field(default_factory=list)
    # Metadata
    line_count: int = 0
    file_sha256: str = ""
    has_execute: bool = False
    has_heal: bool = False
    has_run: bool = False


# ---------------------------------------------------------------------------
# AST Feature Extraction
# ---------------------------------------------------------------------------

def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _extract_string_literals(tree: ast.Module) -> list[str]:
    """Extract all string literals longer than 40 chars (potential prompts)."""
    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if len(node.value) > 40:
                strings.append(node.value.strip())
    return strings


def _extract_call_names(tree: ast.Module) -> list[str]:
    """Extract all function/method call names from AST."""
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return sorted(set(calls))


def _extract_imports(tree: ast.Module) -> list[str]:
    """Extract all import paths."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    return sorted(set(imports))


def _extract_responsibility_keywords(docstring: str) -> list[str]:
    """Extract semantic responsibility keywords from docstring."""
    if not docstring:
        return []
    # Normalize
    text = docstring.lower()
    # Domain keyword extraction
    keywords = set()
    patterns = [
        r'\b(validat\w+)\b', r'\b(detect\w+)\b', r'\b(heal\w+)\b',
        r'\b(enforc\w+)\b', r'\b(scan\w+)\b', r'\b(monitor\w+)\b',
        r'\b(audit\w+)\b', r'\b(guard\w+)\b', r'\b(inspect\w+)\b',
        r'\b(analyz\w+)\b', r'\b(check\w+)\b', r'\b(test\w+)\b',
        r'\b(classif\w+)\b', r'\b(format\w+)\b', r'\b(clean\w+)\b',
        r'\b(fix\w+)\b', r'\b(repair\w+)\b', r'\b(generat\w+)\b',
        r'\b(red.?team\w*)\b', r'\b(adversar\w+)\b', r'\b(security\w*)\b',
        r'\b(safety\w*)\b', r'\b(complian\w+)\b', r'\b(governan\w+)\b',
        r'\b(observ\w+)\b', r'\b(metric\w+)\b', r'\b(telem\w+)\b',
        r'\b(trac\w+)\b', r'\b(location\w*)\b', r'\b(structur\w+)\b',
        r'\b(hierarch\w+)\b', r'\b(naming\w*)\b', r'\b(dedup\w+)\b',
        r'\b(duplicat\w+)\b', r'\b(code\w*)\b', r'\b(prompt\w*)\b',
        r'\b(cost\w*)\b', r'\b(budget\w*)\b', r'\b(token\w*)\b',
        r'\b(orchestrat\w+)\b', r'\b(pipeline\w*)\b', r'\b(dag\w*)\b',
        r'\b(memory\w*)\b', r'\b(state\w*)\b', r'\b(cache\w*)\b',
        r'\b(pinecone\w*)\b', r'\b(redis\w*)\b', r'\b(embed\w+)\b',
        r'\b(rag\w*)\b', r'\b(retriev\w+)\b',
        r'\b(attack\w*)\b', r'\b(vulnerab\w+)\b', r'\b(fuzz\w+)\b',
        r'\b(probe\w*)\b', r'\b(penetrat\w+)\b',
        r'\b(pii\w*)\b', r'\b(credential\w*)\b', r'\b(secret\w*)\b',
        r'\b(hygien\w+)\b', r'\b(sprawl\w*)\b',
    ]
    for pat in patterns:
        for match in re.finditer(pat, text):
            keywords.add(match.group(1))
    return sorted(keywords)


def extract_features(file_path: Path, agent_entry: dict) -> AgentFeatures | None:
    """Full AST-based feature extraction for one agent file."""
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    features = AgentFeatures(
        agent_id=agent_entry.get("class_name", file_path.stem),
        class_name=agent_entry.get("class_name", ""),
        file_path=str(file_path.relative_to(PROJECT_ROOT)),
        layer=agent_entry.get("layer", "unknown"),
        line_count=content.count("\n") + 1,
        file_sha256=hashlib.sha256(content.encode()).hexdigest(),
    )

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return features

    # Imports
    features.imports = _extract_imports(tree)

    # Calls
    features.called_functions = _extract_call_names(tree)

    # Prompt strings
    features.prompt_strings = _extract_string_literals(tree)

    # Find primary class
    class_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    if not class_nodes:
        return features

    # Pick class matching filename or class_name
    stem_clean = re.sub(r"[^a-zA-Z0-9]", "", file_path.stem.lower())
    chosen = class_nodes[0]
    for node in class_nodes:
        if re.sub(r"[^a-zA-Z0-9]", "", node.name.lower()) == stem_clean:
            chosen = node
            break
        if node.name == agent_entry.get("class_name"):
            chosen = node
            break

    # Base classes
    features.base_classes = [_safe_unparse(b) for b in chosen.bases if _safe_unparse(b)]

    # Decorators
    for dec in chosen.decorator_list:
        if isinstance(dec, ast.Name):
            features.decorators.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            features.decorators.append(dec.attr)
        elif isinstance(dec, ast.Call):
            func = dec.func
            if isinstance(func, ast.Name):
                features.decorators.append(func.id)
            elif isinstance(func, ast.Attribute):
                features.decorators.append(func.attr)

    # Docstring
    docstring = ast.get_docstring(chosen) or ""
    features.docstring = docstring
    features.responsibility_keywords = _extract_responsibility_keywords(docstring)

    # Methods
    for item in chosen.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features.method_names.append(item.name)
            # Build signature
            args = [a.arg for a in item.args.args if a.arg != "self"]
            sig = f"{item.name}({', '.join(args)})"
            features.method_signatures.append(sig)
            if item.name == "execute":
                features.has_execute = True
            elif item.name == "heal":
                features.has_heal = True
            elif item.name == "run":
                features.has_run = True

    # Class attributes
    for item in chosen.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            features.class_attributes.append(item.target.id)
        elif isinstance(item, ast.Assign):
            for t in item.targets:
                if isinstance(t, ast.Name):
                    features.class_attributes.append(t.id)

    return features


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------

def jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _normalize_import(imp: str) -> str:
    """Strip project-local prefix for comparison."""
    for prefix in ("agentic_core.", "apps_lic.", "apps_rg.", "apps_shared."):
        if imp.startswith(prefix):
            return imp[len(prefix):]
    return imp


def code_similarity(a: AgentFeatures, b: AgentFeatures) -> float:
    """Weighted composite code similarity."""
    # Imports (weight 0.25)
    imp_a = {_normalize_import(i) for i in a.imports}
    imp_b = {_normalize_import(i) for i in b.imports}
    sim_imports = jaccard(imp_a, imp_b)

    # Base classes (weight 0.15)
    sim_bases = jaccard(set(a.base_classes), set(b.base_classes))

    # Method names (weight 0.25)
    sim_methods = jaccard(set(a.method_names), set(b.method_names))

    # Called functions (weight 0.20)
    sim_calls = jaccard(set(a.called_functions), set(b.called_functions))

    # Decorators (weight 0.05)
    sim_decs = jaccard(set(a.decorators), set(b.decorators))

    # Class attributes (weight 0.10)
    sim_attrs = jaccard(set(a.class_attributes), set(b.class_attributes))

    return (
        0.25 * sim_imports
        + 0.15 * sim_bases
        + 0.25 * sim_methods
        + 0.20 * sim_calls
        + 0.05 * sim_decs
        + 0.10 * sim_attrs
    )


def _shingle(text: str, k: int = 5) -> set[str]:
    """Character-level k-shingling for text similarity."""
    text = re.sub(r'\s+', ' ', text.lower().strip())
    if len(text) < k:
        return {text}
    return {text[i:i+k] for i in range(len(text) - k + 1)}


def prompt_similarity(a: AgentFeatures, b: AgentFeatures) -> float:
    """Similarity of prompt strings using shingling."""
    text_a = " ".join(a.prompt_strings)
    text_b = " ".join(b.prompt_strings)
    if not text_a or not text_b:
        return 0.0
    return jaccard(_shingle(text_a), _shingle(text_b))


def responsibility_similarity(a: AgentFeatures, b: AgentFeatures) -> float:
    """Similarity of extracted responsibility keywords."""
    return jaccard(set(a.responsibility_keywords), set(b.responsibility_keywords))


def dependency_overlap(a: AgentFeatures, b: AgentFeatures) -> float:
    """Import-level dependency overlap."""
    return jaccard(set(a.imports), set(b.imports))


# ---------------------------------------------------------------------------
# Clustering (simple single-linkage with threshold)
# ---------------------------------------------------------------------------

def cluster_agents(
    features_list: list[AgentFeatures],
    sim_matrix: dict[tuple[str, str], float],
    threshold: float,
) -> list[list[str]]:
    """Single-linkage clustering above threshold."""
    # Build adjacency
    adj: dict[str, set[str]] = defaultdict(set)
    for (a_id, b_id), score in sim_matrix.items():
        if score >= threshold:
            adj[a_id].add(b_id)
            adj[b_id].add(a_id)

    # BFS to find connected components
    visited = set()
    clusters = []
    for f in features_list:
        if f.agent_id in visited:
            continue
        if f.agent_id not in adj:
            continue
        cluster = []
        queue = [f.agent_id]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            cluster.append(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        if len(cluster) > 1:
            clusters.append(sorted(cluster))

    return sorted(clusters, key=lambda c: (-len(c), c[0]))


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    Logger.info("=== Agent Deduplication Analysis Pipeline ===")
    Logger.info(f"Project root: {PROJECT_ROOT}")

    # Ensure output dirs
    SIM_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Phase 0: Load discovery
    # -----------------------------------------------------------------------
    Logger.info("[Phase 0] Loading discovery JSON...")
    with open(DISCOVERY_JSON, "r", encoding="utf-8") as f:
        discovery = json.load(f)

    agents_raw = discovery.get("agents", [])
    Logger.info(f"[Phase 0] {len(agents_raw)} agents in discovery JSON")

    # -----------------------------------------------------------------------
    # Feature extraction
    # -----------------------------------------------------------------------
    Logger.info("[Phase 1] AST-based feature extraction...")
    features_map: dict[str, AgentFeatures] = {}
    for entry in agents_raw:
        rel_path = entry.get("file", "")
        if not rel_path:
            continue
        full_path = PROJECT_ROOT / rel_path.replace("\\", "/")
        feat = extract_features(full_path, entry)
        if feat:
            # De-duplicate agent_id collisions (some share class_name like OutreachAgent)
            uid = feat.agent_id
            if uid in features_map:
                uid = f"{uid}__{Path(rel_path).stem}"
            feat.agent_id = uid
            features_map[uid] = feat

    Logger.info(f"[Phase 1] Extracted features for {len(features_map)} agents")

    # -----------------------------------------------------------------------
    # Produce active_agents_index.json
    # -----------------------------------------------------------------------
    index_entries = []
    for uid, feat in sorted(features_map.items()):
        index_entries.append({
            "agent_id": uid,
            "class_name": feat.class_name,
            "file_path": feat.file_path,
            "layer": feat.layer,
            "base_classes": feat.base_classes,
            "method_names": feat.method_names,
            "has_execute": feat.has_execute,
            "has_heal": feat.has_heal,
            "has_run": feat.has_run,
            "line_count": feat.line_count,
            "integrity_hash": feat.file_sha256,
            "responsibility_keywords": feat.responsibility_keywords,
            "import_count": len(feat.imports),
            "prompt_string_count": len(feat.prompt_strings),
            "decorator_count": len(feat.decorators),
        })

    index_path = OUT_DIR / "active_agents_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(index_entries), "agents": index_entries}, f, indent=2)
    Logger.info(f"[Phase 0] Wrote {index_path}")

    # -----------------------------------------------------------------------
    # Pairwise similarity
    # -----------------------------------------------------------------------
    Logger.info("[Phase 1] Computing pairwise similarities...")
    features_list = list(features_map.values())
    code_sim: dict[tuple[str, str], float] = {}
    prompt_sim: dict[tuple[str, str], float] = {}
    resp_sim: dict[tuple[str, str], float] = {}
    dep_sim: dict[tuple[str, str], float] = {}

    pairs = list(combinations(features_list, 2))
    Logger.info(f"[Phase 1] {len(pairs)} pairs to compare")

    for a, b in pairs:
        key = (a.agent_id, b.agent_id)
        code_sim[key] = code_similarity(a, b)
        prompt_sim[key] = prompt_similarity(a, b)
        resp_sim[key] = responsibility_similarity(a, b)
        dep_sim[key] = dependency_overlap(a, b)

    # -----------------------------------------------------------------------
    # Code similarity output
    # -----------------------------------------------------------------------
    high_code = sorted(
        [(k, v) for k, v in code_sim.items() if v >= 0.50],
        key=lambda x: -x[1],
    )

    code_sim_data = {
        "threshold": CODE_SIM_THRESHOLD,
        "total_pairs": len(pairs),
        "pairs_above_050": len(high_code),
        "pairs_above_075": len([x for x in high_code if x[1] >= 0.75]),
        "top_pairs": [
            {"agent_a": k[0], "agent_b": k[1], "score": round(v, 4)}
            for k, v in high_code[:100]
        ],
    }
    with open(SIM_DIR / "code_similarity.json", "w", encoding="utf-8") as f:
        json.dump(code_sim_data, f, indent=2)

    with open(SIM_DIR / "code_similarity.md", "w", encoding="utf-8") as f:
        f.write("# Code Similarity Analysis\n\n")
        f.write(f"- **Total agents**: {len(features_list)}\n")
        f.write(f"- **Total pairs**: {len(pairs)}\n")
        f.write(f"- **Pairs ≥ 0.50**: {len(high_code)}\n")
        f.write(f"- **Pairs ≥ 0.75**: {code_sim_data['pairs_above_075']}\n\n")
        f.write("## Top Code-Similar Pairs\n\n")
        f.write("| Agent A | Agent B | Score | Shared Bases | Shared Methods |\n")
        f.write("|---------|---------|-------|-------------|----------------|\n")
        for (a_id, b_id), score in high_code[:50]:
            fa, fb = features_map[a_id], features_map[b_id]
            shared_bases = set(fa.base_classes) & set(fb.base_classes)
            shared_methods = set(fa.method_names) & set(fb.method_names)
            f.write(f"| {a_id} | {b_id} | {score:.3f} | {', '.join(shared_bases) or '-'} | {len(shared_methods)} |\n")
    Logger.info(f"[Phase 1] Code similarity: {code_sim_data['pairs_above_075']} pairs ≥ 0.75")

    # -----------------------------------------------------------------------
    # Prompt similarity output
    # -----------------------------------------------------------------------
    high_prompt = sorted(
        [(k, v) for k, v in prompt_sim.items() if v >= 0.40],
        key=lambda x: -x[1],
    )
    prompt_sim_data = {
        "threshold": PROMPT_SIM_THRESHOLD,
        "total_pairs": len(pairs),
        "pairs_above_040": len(high_prompt),
        "pairs_above_080": len([x for x in high_prompt if x[1] >= 0.80]),
        "top_pairs": [
            {"agent_a": k[0], "agent_b": k[1], "score": round(v, 4)}
            for k, v in high_prompt[:100]
        ],
    }
    with open(SIM_DIR / "prompt_similarity.json", "w", encoding="utf-8") as f:
        json.dump(prompt_sim_data, f, indent=2)

    with open(SIM_DIR / "prompt_similarity.md", "w", encoding="utf-8") as f:
        f.write("# Prompt Similarity Analysis\n\n")
        f.write(f"- **Total agents**: {len(features_list)}\n")
        f.write(f"- **Pairs ≥ 0.40**: {len(high_prompt)}\n")
        f.write(f"- **Pairs ≥ 0.80**: {prompt_sim_data['pairs_above_080']}\n\n")
        f.write("## Top Prompt-Similar Pairs\n\n")
        f.write("| Agent A | Agent B | Score |\n")
        f.write("|---------|---------|-------|\n")
        for (a_id, b_id), score in high_prompt[:50]:
            f.write(f"| {a_id} | {b_id} | {score:.3f} |\n")
    Logger.info(f"[Phase 1] Prompt similarity: {prompt_sim_data['pairs_above_080']} pairs ≥ 0.80")

    # -----------------------------------------------------------------------
    # Responsibility similarity
    # -----------------------------------------------------------------------
    high_resp = sorted(
        [(k, v) for k, v in resp_sim.items() if v >= RESPONSIBILITY_OVERLAP_THRESHOLD],
        key=lambda x: -x[1],
    )

    with open(SIM_DIR / "responsibility_similarity.md", "w", encoding="utf-8") as f:
        f.write("# Responsibility Similarity Analysis\n\n")
        f.write(f"- **Threshold**: {RESPONSIBILITY_OVERLAP_THRESHOLD}\n")
        f.write(f"- **Pairs above threshold**: {len(high_resp)}\n\n")
        f.write("## Overlap Groups\n\n")
        f.write("| Agent A | Agent B | Overlap | Shared Keywords |\n")
        f.write("|---------|---------|---------|----------------|\n")
        for (a_id, b_id), score in high_resp[:80]:
            fa, fb = features_map[a_id], features_map[b_id]
            shared = sorted(set(fa.responsibility_keywords) & set(fb.responsibility_keywords))
            f.write(f"| {a_id} | {b_id} | {score:.3f} | {', '.join(shared[:5])} |\n")
    Logger.info(f"[Phase 1] Responsibility overlap: {len(high_resp)} pairs above threshold")

    # -----------------------------------------------------------------------
    # Dependency overlap
    # -----------------------------------------------------------------------
    high_dep = sorted(
        [(k, v) for k, v in dep_sim.items() if v >= 0.60],
        key=lambda x: -x[1],
    )

    with open(SIM_DIR / "dependency_overlap.md", "w", encoding="utf-8") as f:
        f.write("# Dependency Overlap Analysis\n\n")
        f.write(f"- **Pairs with ≥ 60% import overlap**: {len(high_dep)}\n\n")
        f.write("## Top Shared-Dependency Pairs\n\n")
        f.write("| Agent A | Agent B | Overlap | Shared Imports |\n")
        f.write("|---------|---------|---------|----------------|\n")
        for (a_id, b_id), score in high_dep[:60]:
            fa, fb = features_map[a_id], features_map[b_id]
            shared_imp = sorted(set(fa.imports) & set(fb.imports))
            f.write(f"| {a_id} | {b_id} | {score:.3f} | {len(shared_imp)} |\n")

    # -----------------------------------------------------------------------
    # Import Complexity (Blast Radius) Report
    # -----------------------------------------------------------------------
    Logger.info("[Phase 1] Computing import complexity (blast radius)...")

    def _classify_import(imp: str) -> str:
        """Classify an import as internal, stdlib, or third-party."""
        internal_prefixes = (
            "agentic_core.", "apps_lic.", "apps_rg.", "apps_shared.",
            "ops_scripts.", "tests.",
        )
        if any(imp.startswith(p) for p in internal_prefixes):
            return "internal"
        # Common stdlib modules (non-exhaustive but covers >95% of usage)
        stdlib = {
            "abc", "ast", "asyncio", "collections", "contextlib",
            "copy", "dataclasses", "datetime", "enum", "functools",
            "hashlib", "importlib", "inspect", "io", "itertools",
            "json", "logging", "math", "os", "pathlib", "platform",
            "re", "shutil", "signal", "socket", "subprocess", "sys",
            "tempfile", "textwrap", "threading", "time", "traceback",
            "typing", "unittest", "urllib", "uuid", "warnings",
        }
        top_module = imp.split(".")[0]
        if top_module in stdlib:
            return "stdlib"
        return "third_party"

    import_stats = []
    for feat in features_list:
        internal = [i for i in feat.imports if _classify_import(i) == "internal"]
        stdlib = [i for i in feat.imports if _classify_import(i) == "stdlib"]
        third_party = [i for i in feat.imports if _classify_import(i) == "third_party"]
        import_stats.append({
            "agent_id": feat.agent_id,
            "layer": feat.layer,
            "total_imports": len(feat.imports),
            "internal": len(internal),
            "stdlib": len(stdlib),
            "third_party": len(third_party),
            "blast_radius": len(internal),  # internal imports = blast radius
        })

    # Sort by blast radius descending
    import_stats.sort(key=lambda x: -x["blast_radius"])

    avg_blast = sum(s["blast_radius"] for s in import_stats) / max(len(import_stats), 1)
    max_blast = import_stats[0] if import_stats else {"agent_id": "-", "blast_radius": 0}

    with open(SIM_DIR / "import_complexity.md", "w", encoding="utf-8") as f:
        f.write("# Import Complexity (Blast Radius) Report\n\n")
        f.write("**Blast radius** = number of internal imports. A high blast radius means\n")
        f.write("changes to this agent ripple through more of the codebase.\n\n")
        f.write(f"- **Agents analyzed**: {len(import_stats)}\n")
        f.write(f"- **Average blast radius**: {avg_blast:.1f}\n")
        f.write(f"- **Max blast radius**: {max_blast['agent_id']} ({max_blast['blast_radius']})\n\n")
        f.write("## Per-Agent Breakdown\n\n")
        f.write("| Agent | Layer | Total | Internal | Stdlib | 3rd Party | Blast Radius |\n")
        f.write("|-------|-------|-------|----------|--------|-----------|-------------|\n")
        for s in import_stats:
            f.write(
                f"| {s['agent_id']} | {s['layer']} | {s['total_imports']} "
                f"| {s['internal']} | {s['stdlib']} | {s['third_party']} "
                f"| {s['blast_radius']} |\n"
            )

        # Layer-level summary
        f.write("\n## Layer Summary\n\n")
        f.write("| Layer | Agents | Avg Blast Radius | Max Blast Radius |\n")
        f.write("|-------|--------|-----------------|------------------|\n")
        layer_groups: dict[str, list[dict]] = defaultdict(list)
        for s in import_stats:
            layer_groups[s["layer"]].append(s)
        for layer in sorted(layer_groups):
            agents = layer_groups[layer]
            layer_avg = sum(a["blast_radius"] for a in agents) / len(agents)
            layer_max = max(a["blast_radius"] for a in agents)
            f.write(f"| {layer} | {len(agents)} | {layer_avg:.1f} | {layer_max} |\n")

    Logger.info(
        f"[Phase 1] Import complexity: avg_blast={avg_blast:.1f}, "
        f"max_blast={max_blast['blast_radius']} ({max_blast['agent_id']})"
    )

    # -----------------------------------------------------------------------
    # Phase 2: Clustering
    # -----------------------------------------------------------------------
    Logger.info("[Phase 2] Clustering agents...")

    # Composite similarity for clustering: max(code, prompt, resp)
    composite: dict[tuple[str, str], float] = {}
    for key in code_sim:
        composite[key] = max(
            code_sim.get(key, 0),
            prompt_sim.get(key, 0),
            resp_sim.get(key, 0) * 0.8,  # downweight pure keyword overlap
        )

    clusters_075 = cluster_agents(features_list, code_sim, 0.75)
    clusters_060 = cluster_agents(features_list, code_sim, 0.60)
    clusters_composite = cluster_agents(features_list, composite, 0.70)

    Logger.info(f"[Phase 2] Code clusters (≥0.75): {len(clusters_075)}")
    Logger.info(f"[Phase 2] Code clusters (≥0.60): {len(clusters_060)}")
    Logger.info(f"[Phase 2] Composite clusters (≥0.70): {len(clusters_composite)}")

    # -----------------------------------------------------------------------
    # Phase 2: Consolidation plan
    # -----------------------------------------------------------------------
    Logger.info("[Phase 2] Generating consolidation plan...")

    def _cluster_stats(cluster: list[str], sim_dict: dict) -> dict:
        scores = []
        for a, b in combinations(cluster, 2):
            key = (a, b) if (a, b) in sim_dict else (b, a)
            scores.append(sim_dict.get(key, 0))
        if not scores:
            return {"min": 0, "max": 0, "median": 0}
        scores.sort()
        return {
            "min": round(scores[0], 3),
            "max": round(scores[-1], 3),
            "median": round(scores[len(scores) // 2], 3),
        }

    def _classify_risk(cluster: list[str]) -> str:
        # High risk if any agent has state/memory/pinecone/redis keywords
        high_risk_kw = {"state", "memory", "pinecone", "redis", "cache"}
        for aid in cluster:
            feat = features_map.get(aid)
            if feat and high_risk_kw & set(feat.responsibility_keywords):
                return "high"
        # Medium if >3 agents or complex orchestration
        if len(cluster) > 3:
            return "medium"
        return "low"

    def _recommend_action(cluster: list[str], stats: dict) -> str:
        if stats["median"] >= 0.85:
            return "MERGE"
        if stats["median"] >= 0.70:
            return "SPLIT shared core into library + thin wrappers"
        if len(cluster) == 2:
            return "RETIRE redundant agent (if superseded)"
        return "RE-SCOPE agents (responsibilities ambiguous)"

    # Use composite clusters for the plan
    plan_clusters = clusters_composite if clusters_composite else clusters_060

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "dedup_consolidation_plan.md", "w", encoding="utf-8") as f:
        f.write("# Agent Consolidation Plan\n\n")
        f.write(f"**Generated from**: {len(features_list)} active agents\n")
        f.write(f"**Clusters identified**: {len(plan_clusters)}\n\n")

        if not plan_clusters:
            f.write("No clusters above threshold found. All agents appear sufficiently distinct.\n\n")
            f.write("## Nearest-Neighbor Analysis\n\n")
            f.write("Top 20 most similar pairs for manual review:\n\n")
            top_composite = sorted(composite.items(), key=lambda x: -x[1])[:20]
            f.write("| Agent A | Agent B | Code Sim | Prompt Sim | Resp Sim | Composite |\n")
            f.write("|---------|---------|----------|------------|----------|----------|\n")
            for (a_id, b_id), comp_score in top_composite:
                cs = code_sim.get((a_id, b_id), 0)
                ps = prompt_sim.get((a_id, b_id), 0)
                rs = resp_sim.get((a_id, b_id), 0)
                f.write(f"| {a_id} | {b_id} | {cs:.3f} | {ps:.3f} | {rs:.3f} | {comp_score:.3f} |\n")

        for idx, cluster in enumerate(plan_clusters, 1):
            stats_code = _cluster_stats(cluster, code_sim)
            stats_prompt = _cluster_stats(cluster, prompt_sim)
            stats_resp = _cluster_stats(cluster, resp_sim)
            risk = _classify_risk(cluster)
            action = _recommend_action(cluster, stats_code)

            f.write(f"## Cluster {idx}\n\n")
            f.write(f"- **Members** ({len(cluster)}): {', '.join(cluster)}\n")
            f.write(f"- **Code similarity**: min={stats_code['min']}, median={stats_code['median']}, max={stats_code['max']}\n")
            f.write(f"- **Prompt similarity**: min={stats_prompt['min']}, median={stats_prompt['median']}, max={stats_prompt['max']}\n")
            f.write(f"- **Responsibility overlap**: min={stats_resp['min']}, median={stats_resp['median']}, max={stats_resp['max']}\n")
            f.write(f"- **Risk**: {risk}\n")
            f.write(f"- **Recommendation**: {action}\n\n")

            f.write("### Member Details\n\n")
            f.write("| Agent | Layer | Lines | Base Classes | Key Methods | Responsibility Keywords |\n")
            f.write("|-------|-------|-------|-------------|-------------|------------------------|\n")
            for aid in cluster:
                feat = features_map.get(aid)
                if feat:
                    bases = ", ".join(feat.base_classes[:3]) or "-"
                    methods = ", ".join(feat.method_names[:5]) or "-"
                    kw = ", ".join(feat.responsibility_keywords[:5]) or "-"
                    f.write(f"| {aid} | {feat.layer} | {feat.line_count} | {bases} | {methods} | {kw} |\n")

            # Canonical target
            f.write(f"\n### Proposed Canonical Agent\n\n")
            # Pick the one with most methods / largest file
            canonical = max(cluster, key=lambda aid: (
                features_map[aid].line_count if aid in features_map else 0
            ))
            f.write(f"- **Target**: `{canonical}`\n")
            if canonical in features_map:
                f.write(f"- **File**: `{features_map[canonical].file_path}`\n")
                f.write(f"- **Layer**: {features_map[canonical].layer}\n")

            f.write(f"\n### Backward Compatibility\n\n")
            for aid in cluster:
                if aid != canonical:
                    f.write(f"- `{aid}` → redirect/shim to `{canonical}`\n")

            f.write(f"\n### Migration Steps\n\n")
            f.write(f"1. Extract shared logic into canonical agent `{canonical}`\n")
            f.write(f"2. Convert other members to thin shims importing from canonical\n")
            f.write(f"3. Update all imports/registry references\n")
            f.write(f"4. Add regression tests for merged behavior\n")
            f.write(f"5. Run `full_agent_discovery.py` to verify count reduction\n\n")
            f.write("---\n\n")

    Logger.info(f"[Phase 2] Wrote dedup_consolidation_plan.md -> {REPORTS_DIR}")

    # -----------------------------------------------------------------------
    # Stop sprawl policy
    # -----------------------------------------------------------------------
    with open(REPORTS_DIR / "dedup_stop_sprawl_policy.md", "w", encoding="utf-8") as f:
        f.write("# Agent Sprawl Prevention Policy\n\n")
        f.write("## Purpose\n\n")
        f.write("Prevent regression of agent count after consolidation by enforcing\n")
        f.write("uniqueness constraints on new agent creation.\n\n")
        f.write("## Rules\n\n")
        f.write("### 1. Single Responsibility Constraint\n\n")
        f.write("Every agent MUST have a clearly defined, non-overlapping responsibility.\n")
        f.write("The responsibility MUST be documented in the class docstring.\n\n")
        f.write("### 2. Uniqueness Proof Required\n\n")
        f.write("Before creating a new agent, the developer MUST:\n")
        f.write("1. Run `python artifacts/dedup/run_dedup_analysis.py` to check for existing overlap\n")
        f.write("2. Demonstrate that no existing agent covers >60% of the proposed responsibility\n")
        f.write("3. Document the uniqueness justification in the PR description\n\n")
        f.write("### 3. Cluster Check Gate\n\n")
        f.write("A CI gate MUST run similarity checks on every PR that adds a new agent:\n")
        f.write("```bash\n")
        f.write("python artifacts/dedup/run_dedup_analysis.py\n")
        f.write("# Fails if any new agent has code_similarity >= 0.75 with an existing agent\n")
        f.write("```\n\n")
        f.write("### 4. Shared Core Reuse\n\n")
        f.write("If a new agent shares >50% of its logic with an existing agent, the shared\n")
        f.write("logic MUST be extracted to a shared module and both agents must import from it.\n\n")
        f.write("### 5. Waiver Process\n\n")
        f.write("Exceptions require:\n")
        f.write("- Written justification explaining why the overlap is necessary\n")
        f.write("- Approval from project architect\n")
        f.write("- Documented in `artifacts/dedup/waivers/` with agent name and date\n\n")
        f.write("## CI Gate Invocation\n\n")
        f.write("```yaml\n")
        f.write("# .github/workflows/agent-sprawl-check.yml\n")
        f.write("name: Agent Sprawl Check\n")
        f.write("on: [pull_request]\n")
        f.write("jobs:\n")
        f.write("  sprawl-check:\n")
        f.write("    runs-on: ubuntu-latest\n")
        f.write("    steps:\n")
        f.write("      - uses: actions/checkout@v4\n")
        f.write("      - uses: actions/setup-python@v5\n")
        f.write("        with:\n")
        f.write("          python-version: '3.12'\n")
        f.write("      - run: python -m agentic_core.L0_maintenance.scripts.full_agent_discovery\n")
        f.write("      - run: python artifacts/dedup/run_dedup_analysis.py\n")
        f.write("      - run: python artifacts/dedup/sprawl_gate.py --max-similarity 0.75\n")
        f.write("```\n")

    Logger.info(f"[Phase 2] Wrote dedup_stop_sprawl_policy.md -> {REPORTS_DIR}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    Logger.info("=== Analysis Complete ===")
    Logger.info(f"Active agents: {len(features_list)}")
    Logger.info(f"Composite clusters (≥0.70): {len(clusters_composite)}")
    Logger.info(f"Code clusters (≥0.75): {len(clusters_075)}")
    Logger.info(f"Artifacts written to: {OUT_DIR}")

    # Print cluster summary to stdout
    print("\n=== CLUSTER SUMMARY ===")
    for idx, cluster in enumerate(plan_clusters, 1):
        stats = _cluster_stats(cluster, code_sim)
        print(f"  Cluster {idx} ({len(cluster)} agents, median_sim={stats['median']}): {', '.join(cluster)}")

    if not plan_clusters:
        print("\n  No high-overlap clusters found. Top 10 nearest pairs:")
        top10 = sorted(composite.items(), key=lambda x: -x[1])[:10]
        for (a_id, b_id), score in top10:
            print(f"    {a_id} <-> {b_id}: {score:.3f}")


if __name__ == "__main__":
    main()
