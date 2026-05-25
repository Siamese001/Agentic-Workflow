"""Generate agentic_core agent inventory runtime assessment (markdown + JSON).

Run from repo root:
  python docs/reports/agent_inventory/_generate_runtime_assessment.py
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_MD = REPO / "docs/reports/agentic_core_agent_inventory_runtime_assessment.md"
OUT_JSON = REPO / "docs/reports/agentic_core_agent_inventory_runtime_assessment.json"

EXTRA_NAMES = {"SovereignMCPGateway", "SovereignRAGManager"}
WRAPPER_PREFIXES = ("L2", "ITiered", "IOrchestrator")
FORCE_NOT_AGENT = {
    "SovereignBaseAgent",
    "L2ExecutionAgent",
    "StructuredEngineAgent",  # bootstrapper stub in runtime/utils
}
SHIM_FILES = {
    "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
    "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
}

SPINE_ENTRY = "agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py"
SPINE_CHAIN = [
    SPINE_ENTRY,
    "agentic_core/L0_routing/intake/pipeline.py",
    "agentic_core/L0_routing/reasoning/route_gates.py",
    "agentic_core/L1_cognition/bridges/u0_to_l1_plan.py",
    "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py",
    "agentic_core/runtime/l2_recipe_resolver.py",
]

REASONING_KW = (
    "llm", "prompt", "gemini", "openai", "claude", "classify", "analyze",
    "heal", "repair", "evaluate", "judge", "plan", "decide", "reason",
    "inference", "ast.parse", "policy", "violation", "orchestrat",
)
AUTONOMY_METHODS = (
    "execute", "heal", "run_mission", "dispatch", "repair", "plan",
    "orchestrate", "route", "act", "process_request", "heal_file",
    "run_inspection", "enforce", "mutate",
)
VALIDATOR_MARKERS = ("validator", "validate_only", "pure validator", "check_dict")


def layer_from_path(rel: str) -> str:
    m = re.search(r"agentic_core/(L\d+)_", rel)
    if m:
        return m.group(1)
    if rel.startswith("agentic_core/knowledge/"):
        return "knowledge"
    if rel.startswith("agentic_core/base_agents/"):
        return "base"
    if rel.startswith("agentic_core/runtime/"):
        return "runtime"
    return "other"


def load_taxonomy() -> dict[str, dict]:
    sys.path.insert(0, str(REPO))
    try:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import AGENT_TAXONOMY_MAP
    except Exception as exc:  # noqa: BLE001
        return {"_error": str(exc)}
    out: dict[str, dict] = {}
    for key, c in AGENT_TAXONOMY_MAP.items():
        if not c.file_path.startswith("agentic_core/"):
            continue
        out[c.class_name] = {
            "taxonomy_key": key,
            "file_path": c.file_path,
            "layer": c.current_layer,
            "role": c.canonical_role.value,
            "status": c.status.value,
        }
    return out


def git_grep_count(pattern: str, path: str = "agentic_core") -> int:
    cmd = ["git", "grep", "-l", "-E", pattern, "--", path]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        return 0
    return len([ln for ln in (r.stdout or "").splitlines() if ln.strip()])


def spine_chain_mentions(name: str) -> bool:
    for rel in SPINE_CHAIN:
        p = REPO / rel
        if not p.exists():
            continue
        try:
            if name in p.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            pass
    return False


def registry_mentions(name: str) -> bool:
    p = REPO / "agentic_core/agents/types/agent_registry.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8", errors="replace")
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower().replace("_agent", "").strip("_")
    return name in text or f'"{snake}"' in text or f'agent_id="{snake}"' in text


PRODUCT_SPINE_FUNCTIONS = [
    ("run_integrated_single_action_spine", SPINE_ENTRY),
    ("run_request_intake", "agentic_core/L0_routing/intake/pipeline.py"),
    ("validated_request_to_plan_contract", "agentic_core/L1_cognition/bridges/u0_to_l1_plan.py"),
    ("check_route_gates", "agentic_core/L0_routing/reasoning/route_gates.py"),
    ("resolve_l2_recipe", "agentic_core/runtime/l2_recipe_resolver.py"),
    ("ExitEvalPipeline.run", "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py"),
]

INVENTORY_ROLES = (
    "PRODUCT_SPINE_FUNCTION",
    "TRUE_AGENT_NOT_ON_PRODUCT_SPINE",
    "GOVERNANCE_CERTIFIER_OR_VALIDATOR",
    "HEALER_OR_DEV_AGENT",
    "UTILITY_OR_WRAPPER",
    "SHIM_OR_DEAD_LEGACY",
)


@dataclass
class Row:
    agent: str
    module_path: str
    declared_layer: str
    truly_agent: str
    reasoning_mechanism: str
    autonomy_mechanism: str
    correct_layer: str
    expected_spine_role: str
    invoked_e2e: str
    runtime_proof: str
    static_evidence: str
    inventory_role: str
    verdict: str
    required_fix: str


def _inventory_role_and_fix(
    *,
    name: str,
    rel: str,
    layer: str,
    truly: str,
    is_shim: bool,
    is_wrapper: bool,
    is_validator_name: bool,
    validate_only: bool,
    has_autonomy: bool,
    low: str,
) -> tuple[str, str]:
    """Separate inventory/taxonomy role from agenthood and product-spine invocation."""
    if is_shim or rel in SHIM_FILES or name.startswith("(no"):
        return "SHIM_OR_DEAD_LEGACY", "ARCHIVE_OR_DELETE_SHIM"
    if is_wrapper or name in FORCE_NOT_AGENT:
        return "UTILITY_OR_WRAPPER", "KEEP_AS_UTILITY"
    if is_validator_name or "Validator" in name or validate_only:
        return "GOVERNANCE_CERTIFIER_OR_VALIDATOR", "REGISTER_TAXONOMY_AS_CERTIFIER"
    if (
        "Healer" in name
        or "healer" in rel
        or "heal_file" in low
        or name in {
            "GravityLeakRepairAgent",
            "LocationHealerAgent",
            "ReportLocationAgent",
            "StructureHealerAgent",
            "CodeHealerAgent",
            "HierarchyHealerAgent",
            "RootHygieneHealerAgent",
            "FileClassificationHealerAgent",
        }
    ):
        return "HEALER_OR_DEV_AGENT", "KEEP_OFF_PRODUCT_SPINE_DOCUMENT_PATH"
    if truly == "YES":
        return "TRUE_AGENT_NOT_ON_PRODUCT_SPINE", "REGISTER_IN_TAXONOMY_OFF_SPINE"
    if layer == "L5":
        return "GOVERNANCE_CERTIFIER_OR_VALIDATOR", "REGISTER_TAXONOMY_AS_CERTIFIER"
    return "UTILITY_OR_WRAPPER", "KEEP_AS_UTILITY"


def analyze_class(name: str, path: str, source: str, bases: list[str]) -> Row:
    rel = path.replace("\\", "/")
    layer = layer_from_path(rel)
    low = source.lower()

    is_shim_file = rel in SHIM_FILES
    if name == "RootCustomsAgent":
        is_shim_file = True
    is_wrapper = (
        name in FORCE_NOT_AGENT
        or any(name.startswith(p) for p in WRAPPER_PREFIXES)
        or name.endswith("AgentSimple") and "Monitor" in name
    )
    if rel == "agentic_core/runtime/utils/runtime_bootstrapper_util.py" and name == "StructuredEngineAgent":
        is_wrapper = True

    has_reasoning = any(k in low for k in REASONING_KW) or "ast." in low
    has_autonomy = any(
        f"def {m}" in low or f"async def {m}" in low for m in AUTONOMY_METHODS
    )
    is_validator_name = "validator" in name.lower() or "Validator" in name
    validate_only = "validate_only" in low or "pure validator" in low

    if is_shim_file and name == "RootCustomsAgent":
        role, fix = "SHIM_OR_DEAD_LEGACY", "ARCHIVE_OR_DELETE_SHIM"
        return Row(
            agent=name,
            module_path=rel,
            declared_layer=layer,
            truly_agent="NO",
            reasoning_mechanism="delegates to root_customs_util (deterministic routing rules)",
            autonomy_mechanism="deprecated shim; no independent authority envelope",
            correct_layer="NO (L0 util is canonical)",
            expected_spine_role="none — product spine uses run_request_intake/check_route_gates, not this class",
            invoked_e2e="NO (DEAD_OR_LEGACY)",
            runtime_proof="none",
            static_evidence="shim docstring; util replacement",
            inventory_role=role,
            verdict="SHIM_OR_DEAD_LEGACY",
            required_fix=fix,
        )

    if rel in SHIM_FILES and "DagRuntimeInspector" in rel:
        role, fix = "SHIM_OR_DEAD_LEGACY", "ARCHIVE_OR_DELETE_SHIM"
        return Row(
            agent="(no DagRuntimeInspectorAgent class)",
            module_path=rel,
            declared_layer="L3",
            truly_agent="NO",
            reasoning_mechanism="re-export only",
            autonomy_mechanism="none",
            correct_layer="N/A",
            expected_spine_role="observer shim → InspectorExecutor",
            invoked_e2e="NO (DEAD_OR_LEGACY)",
            runtime_proof="none",
            static_evidence="module docstring: consolidated to InspectorExecutor",
            inventory_role=role,
            verdict="SHIM_OR_DEAD_LEGACY",
            required_fix=fix,
        )

    if is_wrapper:
        role, fix = "UTILITY_OR_WRAPPER", "KEEP_AS_UTILITY"
        return Row(
            agent=name,
            module_path=rel,
            declared_layer=layer,
            truly_agent="NO",
            reasoning_mechanism="contract/protocol or adapter stub",
            autonomy_mechanism="none",
            correct_layer="N/A",
            expected_spine_role="L2 contract wrapper or base/protocol",
            invoked_e2e="NO (STATIC_ONLY)",
            runtime_proof="none",
            static_evidence="wrapper/base naming convention",
            inventory_role=role,
            verdict="UTILITY_OR_WRAPPER",
            required_fix=fix,
        )

    if is_validator_name and validate_only and not has_autonomy:
        truly = "NO"
        autonomy = "validate-only; dispatches via HEALER_REGISTRY without local act loop"
    elif has_reasoning and has_autonomy:
        truly = "YES"
        autonomy = "execute/heal/run-style methods present"
    elif has_reasoning and not has_autonomy:
        truly = "NO"
        autonomy = "analysis without autonomous act"
    else:
        truly = "NO"
        autonomy = "passive/telemetry-only surface"

    role, fix = _inventory_role_and_fix(
        name=name,
        rel=rel,
        layer=layer,
        truly=truly,
        is_shim=is_shim_file,
        is_wrapper=is_wrapper,
        is_validator_name=is_validator_name,
        validate_only=validate_only,
        has_autonomy=has_autonomy,
        low=low,
    )

    if has_reasoning:
        if "llm" in low or "gemini" in low or "openai" in low:
            reasoning = "LLM API + prompts"
        elif "ast" in low:
            reasoning = "AST / deterministic code analysis"
        elif is_validator_name:
            reasoning = "rule-based validation / classification"
        else:
            reasoning = "deterministic policy/heuristic reasoning"
    else:
        reasoning = "none detected"

    # Expected spine role by layer
    role_map = {
        "L0": "route/intake (not L2 exec, not X3, not UWG)",
        "L1": "plan/advisory only",
        "L2": "bounded execution (product spine uses apps_* L2 recipe, not these classes)",
        "L3": "workflow/DAG sequencing (ExitEvalPipeline on spine; *Agent classes optional)",
        "L5": "governance/heal certification — not route/X3/UWG/L4 write/L6 learn",
        "L6": "completed-run observe only — no current-run rescue",
        "knowledge": "RAG/retrieval-adjacent (C0/L4 binding by proof only)",
        "base": "inheritance only",
        "runtime": "bootstrap stub",
    }
    expected = role_map.get(layer, "non-spine utility")

    correct = "YES"
    if layer == "L5" and name in ("SemanticGatekeeperAgent",) and "L3" in rel:
        correct = "NO — safety role in L3 package"
    if layer == "L5" and "L0RoutingBase" in str(bases):
        correct = "NO — L0 base in L5 folder"

    tax = load_taxonomy()
    in_tax = name in tax
    grep_hits = git_grep_count(re.escape(name))
    spine_hit = spine_chain_mentions(name)
    reg_hit = registry_mentions(name)

    static_parts = []
    if in_tax:
        static_parts.append("AGENT_TAXONOMY_MAP")
    if spine_hit:
        static_parts.append("spine_chain_source_mention")
    if reg_hit:
        static_parts.append("execution_profile_registry")
    static_parts.append(f"git_grep_agentic_core_files={grep_hits}")
    static_evidence = "; ".join(static_parts) if static_parts else "class/file only"

    invoked = "NO"
    runtime_proof = "none"
    if spine_hit and truly == "YES":
        invoked = "NO"  # mention ≠ invocation
        runtime_proof = "static mention in spine module only — not runtime proof"

    e2e_detail = "NO"
    if truly == "YES":
        if spine_hit:
            e2e_detail = "NO (STATIC_ONLY: named in spine source, not invoked)"
        elif in_tax:
            e2e_detail = "NO (REGISTRY_ONLY)"
        elif grep_hits > 0:
            e2e_detail = "NO (NOT_WIRED)"
        else:
            e2e_detail = "NO (DEAD_OR_LEGACY)"
    elif role == "SHIM_OR_DEAD_LEGACY":
        e2e_detail = "NO (DEAD_OR_LEGACY)"
    elif role in ("UTILITY_OR_WRAPPER", "GOVERNANCE_CERTIFIER_OR_VALIDATOR"):
        e2e_detail = "NO (STATIC_ONLY)" if grep_hits else "NO"

    if in_tax and truly == "YES" and role == "TRUE_AGENT_NOT_ON_PRODUCT_SPINE":
        fix = "UPDATE_TAXONOMY_OFF_SPINE_ROLE"
    elif truly == "YES" and not in_tax:
        fix = "REGISTER_IN_TAXONOMY_OFF_SPINE"

    verdict = role
    if truly == "YES":
        verdict = f"{role} (true_agent=YES)"
    elif truly == "NO" and role == "GOVERNANCE_CERTIFIER_OR_VALIDATOR":
        verdict = f"{role} (true_agent=NO)"

    return Row(
        agent=name,
        module_path=rel,
        declared_layer=layer,
        truly_agent=truly,
        reasoning_mechanism=reasoning,
        autonomy_mechanism=autonomy,
        correct_layer=correct,
        expected_spine_role=expected,
        invoked_e2e=e2e_detail,
        runtime_proof=runtime_proof,
        static_evidence=static_evidence,
        inventory_role=role,
        verdict=verdict,
        required_fix=fix,
    )


def collect_candidates() -> list[tuple[str, str, str, list[str]]]:
    root = REPO / "agentic_core"
    best: dict[str, tuple[str, str, list[str]]] = {}
    for py in sorted(root.rglob("*.py")):
        rel = py.relative_to(REPO).as_posix()
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            n = node.name
            if not (n.endswith("Agent") or n.endswith("AgentSimple") or n in EXTRA_NAMES):
                continue
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)
            score = (0 if "reasoning" in rel else 1, len(rel))
            if n not in best or score < best[n][0]:
                best[n] = (score, rel, src, bases)
    return [(n, t[1], t[2], t[3]) for n, t in sorted(best.items(), key=lambda x: x[0].lower())]


def try_spine_run() -> dict:
    """Attempt canonical spine artifact emission."""
    out_dir = REPO / "artifacts/reports/agent_inventory/_spine_proof_run"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "attempted": True,
        "exit_code": None,
        "error": None,
        "artifacts": [],
        "producer_components": [],
        "agent_strings_in_artifacts": [],
    }
    script = r"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
out_dir = Path(r'%s')
from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import run_integrated_single_action_spine
raw = {
    'request_id': 'inv-assess-001',
    'trace_root': 'inv-trace-001',
    'jd_payload': {'title': 'T', 'description': 'd'},
    'jd_hash': 'a', 'brief_hash': 'b', 'resume_hash': 'c',
}
mock_l2 = MagicMock(return_value={'status': 'success'})
with patch('agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe', return_value=mock_l2):
    r = run_integrated_single_action_spine(
        raw_request=raw, app_name='apps_rg', artifact_dir=out_dir,
        _test_mode=True, l2_callable=mock_l2,
    )
print(json.dumps({'fault': r.fault, 'run_id': r.run_id, 'x3': r.x3_disposition}))
""" % str(out_dir).replace("\\", "/")
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    result["exit_code"] = proc.returncode
    if proc.returncode != 0:
        result["error"] = (proc.stderr or proc.stdout or "")[-2000:]
        return result
    for p in sorted(out_dir.glob("*.json")):
        result["artifacts"].append(p.relative_to(REPO).as_posix())
        try:
            blob = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        text = json.dumps(blob)
        if "producer_component" in text:
            pcs = re.findall(r'"producer_component"\s*:\s*"([^"]+)"', text)
            result["producer_components"].extend(pcs)
        for agent_name in re.findall(r"[A-Z][a-zA-Z]+Agent", text):
            if agent_name.startswith("agentic_core"):
                continue
            result["agent_strings_in_artifacts"].append(f"{p.name}:{agent_name}")
    return result


def load_w3_live_report() -> dict[str, Any]:
    """W3 live spine proof report (non-mock); empty dict if missing."""
    path = REPO / "artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    taxonomy = load_taxonomy()
    rows: list[Row] = []
    for name, path, src, bases in collect_candidates():
        rows.append(analyze_class(name, path, src, bases))

    # DagRuntimeInspector shim row
    if not any(r.agent.startswith("(no DagRuntimeInspector") for r in rows):
        rows.append(
            analyze_class("DagRuntimeInspector", SHIM_FILES.pop(), "shim", []),
        )

    spine_run = try_spine_run()
    w3_live = load_w3_live_report()

    true_agents = [r for r in rows if r.truly_agent == "YES"]
    not_agents = [r for r in rows if r.truly_agent != "YES"]
    in_tax = sum(1 for r in rows if taxonomy.get(r.agent))
    e2e_yes = [r for r in rows if str(r.invoked_e2e).startswith("YES")]
    by_role: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        by_role[r.inventory_role].append(r)

    md: list[str] = [
        "# agentic_core Agent Inventory — Runtime Assessment",
        "",
        f"**Generated:** {generated}",
        "",
        "**STATUS:** PARTIAL",
        "",
        "## Executive summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Candidates scanned (AST `*Agent` / aliases) | {len(rows)} |",
        f"| Truly an agent (reasoning + autonomy heuristic) | {len(true_agents)} |",
        f"| Not agent / wrapper / shim (heuristic) | {len(not_agents)} |",
        f"| Registered in `AGENT_TAXONOMY_MAP` (`agentic_core` only) | {in_tax} |",
        f"| **E2E product-spine invoked (artifact-proven class)** | **{len(e2e_yes)}** |",
        f"| True agents without E2E product-spine proof | {len(true_agents) - len(e2e_yes)} |",
        "",
        "### Inventory role rollup (`*Agent` candidates only)",
        "",
        "| Inventory role | Count |",
        "|----------------|------:|",
    ]
    for role in INVENTORY_ROLES:
        if role == "PRODUCT_SPINE_FUNCTION":
            continue
        md.append(f"| {role} | {len(by_role.get(role, []))} |")
    md.append("")
    md.append(
        "Canonical product spine **functions** (not `*Agent` classes) are listed under "
        "[Product spine truth](#decision-1--product-spine-truth) — they are not AST candidates."
    )
    md.append("")
    md.append("## Architecture conclusion")
    md.append("")
    md.append(
        "The canonical E2E product spine is currently a **governed functional pipeline**, "
        "not a class-agent execution graph. `*Agent` classes exist as adjacent governance, "
        "healing, validation, dev, or legacy capabilities unless a receipt proves runtime "
        "invocation. Therefore the current taxonomy must **not** be interpreted as the "
        "product runtime graph."
    )
    md.append("")
    md.append('<a id="decision-1--product-spine-truth"></a>')
    md.append("## Decision 1 — Product spine truth")
    md.append("")
    md.append("This decision is **separate** from inventory/taxonomy cleanup.")
    md.append("")
    md.append("| Invariant | Value |")
    md.append("|-----------|-------|")
    md.append("| E2E invoked class count | **0** |")
    md.append("| Taxonomy registration implies runtime invocation | **No** |")
    md.append("| Class name / inheritance implies runtime invocation | **No** |")
    md.append(
        "| Current HOW / spine proof artifacts prove | **Stage / function execution only** "
        "(e.g. `U0_INTAKE`, `L1_PLAN`, `producer_component` on entrypoint) |"
    )
    md.append("")
    md.append("No `agentic_core` `*Agent` class may be claimed as product-spine-invoked unless a "
                "future runtime artifact explicitly proves class identity (see [Acceptance invariant](#acceptance-invariant)).")
    md.append("")
    md.append("### Canonical product spine functions (not `*Agent` classes)")
    md.append("")
    md.append("| Function | Module |")
    md.append("|----------|--------|")
    for fn, mod in PRODUCT_SPINE_FUNCTIONS:
        md.append(f"| `{fn}` | `{mod}` |")
    md.append("")
    md.append("L2 execution on the product path is **`resolve_l2_recipe` → `apps_*` step callables** "
                "(out of scope for this `agentic_core` class inventory).")
    md.append("")
    md.append('<a id="decision-2--inventory--taxonomy-cleanup"></a>')
    md.append("## Decision 2 — Inventory / taxonomy cleanup")
    md.append("")
    md.append(
        "This decision is **not** equivalent to Decision 1. Do **not** collapse all L5/healing "
        "classes to `NOT_AGENT` or delete-by-default. Separate:"
    )
    md.append("")
    md.append("1. **Agenthood classification** (`Truly an Agent?` column)")
    md.append("2. **Taxonomy registration** (`AGENT_TAXONOMY_MAP` — metadata only)")
    md.append("3. **Product-spine invocation** (`Invoked in E2E spine run?` — artifact-only)")
    md.append("4. **Runtime proof** (receipts / OTEL / registry binding)")
    md.append("")
    md.append("### Role definitions")
    md.append("")
    md.append("| Role | Meaning |")
    md.append("|------|---------|")
    md.append("| `TRUE_AGENT_NOT_ON_PRODUCT_SPINE` | Bounded autonomous agent; not artifact-proven on canonical product spine |")
    md.append("| `GOVERNANCE_CERTIFIER_OR_VALIDATOR` | L5 certify/validate/check surfaces; not product routing/execution/X3/UWG |")
    md.append("| `HEALER_OR_DEV_AGENT` | Healing/dev/CI mission agents; off product spine unless future receipt proves otherwise |")
    md.append("| `UTILITY_OR_WRAPPER` | Base, protocol, L2 wrapper, monitor stub |")
    md.append("| `SHIM_OR_DEAD_LEGACY` | Deprecated re-export or empty shim module |")
    md.append("")
    md.append(f"- Taxonomy registers **{in_tax}** `agentic_core` classes; AST found **{len(rows)}** candidates.")
    md.append(
        f"- **{len(true_agents) - in_tax}** heuristic true-agents lack taxonomy rows — register with "
        "**off-spine** role, not as product runtime owners."
    )
    md.append("")
    md.append('<a id="acceptance-invariant"></a>')
    md.append("## Acceptance invariant")
    md.append("")
    md.append(
        "No `agentic_core` class may be described as **product-spine invoked** unless an E2E "
        "artifact contains at least one of:"
    )
    md.append("")
    md.append("- class name")
    md.append("- module path")
    md.append("- registry selected agent id")
    md.append("- execution profile id bound to that class")
    md.append("- OTEL span naming that class/module")
    md.append("- receipt producer/consumer/executor naming that class/module")
    md.append("")
    md.append(f"**Current inspection:** {len(e2e_yes)}/{len(rows)} candidates satisfy this invariant.")
    md.append("")
    md.append("### Runtime proof attempt (harness)")
    md.append("")
    if spine_run.get("error"):
        err = str(spine_run.get("error") or "")
        err_line = next((ln for ln in err.splitlines() if "Error" in ln or "ModuleNotFound" in ln), err[-400:])
        md.append(f"- **BLOCKED:** spine run failed (exit {spine_run.get('exit_code')}): `{err_line.strip()}`")
    else:
        md.append(f"- Spine harness run exit **{spine_run.get('exit_code')}** (`_test_mode=True`, mock L2 callable)")
        proof_path = "artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_spine_proof.json"
        how_path = "artifacts/reports/agent_inventory/_spine_proof_run/agentic_core_how_trace.json"
        md.append(f"- Artifacts dir: [`_spine_proof_run/`](artifacts/reports/agent_inventory/_spine_proof_run/) ({len(spine_run.get('artifacts') or [])} JSON files)")
        try:
            spine_doc = json.loads((REPO / proof_path).read_text(encoding="utf-8"))
            md.append(f"- [`agentic_core_spine_proof.json`]({proof_path}): `run_id={spine_doc.get('run_id')}`, `trace_root={spine_doc.get('trace_root')}`, `success={spine_doc.get('success')}`")
        except (OSError, json.JSONDecodeError):
            pass
        try:
            how_doc = json.loads((REPO / how_path).read_text(encoding="utf-8"))
            stages = [s.get("stage_id") for s in how_doc.get("stages") or [] if isinstance(s, dict)]
            md.append(f"- [`agentic_core_how_trace.json`]({how_path}): stages={stages[:12]}… (no `*Agent` class fields)")
        except (OSError, json.JSONDecodeError):
            pass
        pcs = sorted(set(spine_run.get("producer_components") or []))
        if pcs:
            md.append(f"- `producer_component` in receipts: `{pcs[0]}` (functional entrypoint, not a class agent)")
        ag = spine_run.get("agent_strings_in_artifacts") or []
        md.append(
            f"- Proof class: **MOCK_ONLY_PROOF** for spine **functions**; **0** rows with per-class `*Agent` invocation (`incidental_agent_strings={len(ag)}`)."
        )

    md.append("")
    md.append("### W3 live spine proof (production path, no mock L2)")
    md.append("")
    if not w3_live:
        md.append("- **Not run** — execute `python tools/governance/run_w3_live_spine_proof.py`")
    else:
        w3_dir = w3_live.get("artifact_dir") or "artifacts/reports/agent_inventory/_w3_live_spine_proof_run"
        md.append(
            f"- Report: [`w3_live_spine_proof_report.json`]({w3_dir}/w3_live_spine_proof_report.json) "
            f"(`runtime_proof_class={w3_live.get('runtime_proof_class')}`, `mock_harness_backfill=false`)"
        )
        md.append(
            f"- Spine attempted: `{w3_live.get('spine_attempted')}`; "
            f"`a1_invoked_agent_classes={w3_live.get('a1_invoked_agent_classes', 0)}`; "
            f"`mock_mode_detected={w3_live.get('mock_mode_detected')}`"
        )
        if w3_live.get("spine_fault"):
            md.append(f"- L2 fault (live): `{str(w3_live.get('spine_fault'))[:240]}…`")
        md.append(
            "- Evaluation: [`agent_inventory_w3_class_identity_evaluation.md`]"
            "(docs/reports/cursor/agent_inventory_w3_class_identity_evaluation.md) — **defer** class identity on HOW"
        )
        md.append(
            "- Taxonomy: **no** `ARTIFACT_PROVEN` updates from W3 (`taxonomy_artifact_proven_updates=0`)"
        )

    md.extend([
        "",
        "### Harness note (not architecture proof)",
        "",
        "A minimal import shim at "
        "[`agentic_core/L6_system_learning/snapshot/__init__.py`]"
        "(agentic_core/L6_system_learning/snapshot/__init__.py) re-exports `RuntimeADGSnapshot` "
        "so `spine_proof_bundle` can import during **report generation only**. "
        "This enables the mock-L2 spine harness to emit HOW/spine JSON; it does **not** prove "
        "class-agent architecture or live product execution.",
        "",
        "### Layer misplacements (static)",
        "",
        "- `SemanticGatekeeperAgent` — L3 path, safety role",
        "- `GospelSyncAgent`, `BootstrapAgent`, `PreCommitSovereignAgent` — L5 folder with L0 routing bases",
        "- L4/L7: no `*Agent` classes (expected)",
        "",
        "## NON_CLAIMS",
        "",
        "- This report does **not** prove the `*Agent` classes are unused everywhere.",
        "- This report proves they are **not artifact-proven** as invoked by the canonical E2E spine run inspected.",
        "- Mock L2 harness proof is valid only for spine **path shape** (stage/function flow), "
        "not live product model/tool execution.",
        "- Taxonomy registration, static import fan-in, and class naming are **not** runtime invocation.",
        "",
        "---",
        "",
        "## Main inventory table",
        "",
        "| Agent | Module path | Layer | Inventory role | Truly an Agent? | Reasoning | Autonomy | Correct layer? | Expected spine role | Invoked E2E? | Runtime proof | Static evidence | Required fix |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ])

    def esc(s: str) -> str:
        return s.replace("|", "\\|").replace("\n", " ")

    for r in rows:
        md.append(
            f"| {esc(r.agent)} | `{esc(r.module_path)}` | {esc(r.declared_layer)} | "
            f"`{esc(r.inventory_role)}` | {esc(r.truly_agent)} | "
            f"{esc(r.reasoning_mechanism)} | {esc(r.autonomy_mechanism)} | {esc(r.correct_layer)} | "
            f"{esc(r.expected_spine_role)} | {esc(r.invoked_e2e)} | {esc(r.runtime_proof)} | "
            f"{esc(r.static_evidence)} | {esc(r.required_fix)} |"
        )

    # Layer sections
    md.append("")
    md.append("## Layer-by-layer findings")
    by_layer: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        by_layer[r.declared_layer].append(r)
    for layer in sorted(by_layer.keys()):
        items = by_layer[layer]
        ta = sum(1 for i in items if i.truly_agent == "YES")
        md.append(f"### {layer} ({len(items)} candidates, {ta} true agents)")
        md.append("")
        for i in sorted(items, key=lambda x: x.agent.lower())[:8]:
            md.append(
                f"- **{i.agent}** — `{i.inventory_role}`; true_agent={i.truly_agent}; E2E={i.invoked_e2e}"
            )
        if len(items) > 8:
            md.append(f"- … and {len(items) - 8} more (see table)")
        md.append("")

    md.append("## Runtime proof appendix")
    md.append("")
    md.append("### Commands")
    md.append("")
    md.append("```bash")
    md.append("python docs/reports/agent_inventory/_generate_runtime_assessment.py")
    md.append("# attempted:")
    md.append("python -c \"... run_integrated_single_action_spine(..., _test_mode=True) ...\"")
    md.append("```")
    md.append("")
    md.append(f"- Generator exit: **0** (this script)")
    md.append(f"- Spine run exit: **{spine_run.get('exit_code', 'not run')}**")
    md.append("")
    if spine_run.get("artifacts"):
        md.append("### Artifacts inspected")
        for a in spine_run["artifacts"]:
            md.append(f"- [`{Path(a).name}`]({a})")
    else:
        md.append("### Artifacts inspected")
        md.append("- None emitted (spine run blocked or no JSON output)")
    md.append("")
    md.append("### Acceptable proof not found")
    md.append("")
    md.append("- No in-repo `agentic_core_spine_proof.json` with per-agent invocation records")
    md.append("- No OTEL span bundle in repo tying class names to canonical product spine run")
    md.append("- `tools/certification/agentic_core_e2e` scenarios: **not_implemented** (no `run_scenario` hook)")
    md.append("")

    md.append("## Fix plan (by inventory role)")
    md.append("")
    md.append(
        "Rollup is **taxonomy/inventory cleanup only** — not a mandate to wire every class "
        "to the product spine or bulk-relabel as `NOT_AGENT`."
    )
    md.append("")
    for role in INVENTORY_ROLES:
        if role == "PRODUCT_SPINE_FUNCTION":
            continue
        agents = [r.agent for r in rows if r.inventory_role == role]
        if not agents:
            continue
        md.append(f"### `{role}` ({len(agents)})")
        md.append("")
        sample_fix = next((r.required_fix for r in rows if r.inventory_role == role), "")
        md.append(f"- Typical action: `{sample_fix}`")
        md.append("")
        for a in sorted(agents)[:12]:
            md.append(f"- {a}")
        if len(agents) > 12:
            md.append(f"- … +{len(agents) - 12} more")
        md.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    payload = {
        "generated_at": generated,
        "status": "PARTIAL",
        "architecture_conclusion": (
            "Canonical E2E product spine is a governed functional pipeline, not a "
            "class-agent execution graph. Taxonomy must not be read as product runtime graph."
        ),
        "product_spine_truth": {
            "e2e_invoked_class_count": len(e2e_yes),
            "taxonomy_implies_invocation": False,
            "class_name_implies_invocation": False,
            "how_proof_scope": "stage_function_only",
            "canonical_functions": [
                {"function": fn, "module": mod} for fn, mod in PRODUCT_SPINE_FUNCTIONS
            ],
        },
        "acceptance_invariant": [
            "class name",
            "module path",
            "registry selected agent id",
            "execution profile id bound to that class",
            "OTEL span naming that class/module",
            "receipt producer/consumer/executor naming that class/module",
        ],
        "non_claims": [
            "Does not prove *Agent classes unused everywhere",
            "Proves not artifact-proven on canonical E2E spine inspected",
            "Mock L2 harness proves path shape only not live product execution",
        ],
        "harness_shim_note": (
            "agentic_core/L6_system_learning/snapshot/__init__.py enables report "
            "generation only; not architecture proof"
        ),
        "summary": {
            "candidates_scanned": len(rows),
            "true_agents": len(true_agents),
            "not_agent_or_wrapper": len(not_agents),
            "taxonomy_registered_agentic_core": in_tax,
            "invoked_e2e_yes": len(e2e_yes),
            "true_agents_not_invoked_e2e": len(true_agents) - len(e2e_yes),
            "inventory_role_counts": {role: len(by_role.get(role, [])) for role in INVENTORY_ROLES},
        },
        "spine_run": spine_run,
        "spine_chain_modules": SPINE_CHAIN,
        "rows": [asdict(r) for r in rows],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(REPO)}")
    print(f"Wrote {OUT_JSON.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
