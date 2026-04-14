#!/usr/bin/env python3
"""
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_1")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_2")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_3")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_4")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_5")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_6")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_7")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_8")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_9")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_10")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_11")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_12")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_13")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_14")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_15")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_16")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_17")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_18")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_19")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_20")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_21")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_22")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_23")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_24")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_25")
_emit_reads_through("l4", "generate_qwen_healing_report", "urg_read_26")
generate_qwen_healing_report.py

Scans all 190 agents via AST, classifies each as QWEN_VLLM / DETERMINISTIC / HYBRID,
adds BMG embedding recommendations, and emits a unified-diff recommendation report.

Output: docs/reports/plans/qwen_vllm_healing_recommendations.md
No source files are modified.
"""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    REPORTS_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_JSON = REPO_ROOT / "artifacts" / "discovery" / "agent_discovery_full.json"
REPORT_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "qwen_vllm_healing_recommendations.md"

VLLM_BASE_URL = "http://localhost:8000/v1"
VLLM_MODEL = "qwen-14b-quantized"
BMG_INDEX = "canon-healing-patterns"
BMG_DIM = 1536

# ---------------------------------------------------------------------------
# Classification table — agent name -> (mode, bmg, rationale)
# mode: Q=QWEN_VLLM  D=DETERMINISTIC  H=HYBRID
# ---------------------------------------------------------------------------
_CT: dict[str, tuple[str, bool, str]] = {
    # L0_routing
    "BenchmarkingAgent": ("D", False, "Metric collection, fixed schema output"),
    "BootstrapAgent": ("D", False, "Initialisation sequence, no semantic content"),
    "DocstringComplianceAgent": ("Q", False, "Must judge docstring quality, not just presence"),
    "FilesystemSSOTReconcilerAgent": ("D", False, "Path/JSON diff reconciliation"),
    "GospelSyncAgent": ("D", False, "Registry sync, deterministic JSON writes"),
    "SSOTFolderCleanupAgent": ("D", False, "File moves via fixed SSOT rules"),
    # L1_cognition
    "ASTValidatorAgent": ("D", False, "AST structural check, binary pass/fail"),
    "SovereignCognitivePlaneAgent": ("Q", True, "Semantic routing/cognition; pattern recall"),
    "AutonomousPromptEvolutionAgent": ("Q", True, "Generates evolved prompts; retrieves patterns"),
    "BudgetAgent": ("D", False, "Token/cost arithmetic"),
    "ContextCuratorAgent": ("Q", True, "Ranks context by semantic relevance"),
    "LLMPromptGovernorAgent": ("Q", False, "Governs prompts via LLM policy judgment"),
    "MetaLearningAgent": ("Q", True, "Strategy weighting from experience replay"),
    "RgReflectionAgent": ("Q", True, "Reflective learning from past cycles"),
    "SherlockAgent": ("Q", True, "Investigative reasoning; pattern recall"),
    "StrategicRecommendationAgent": ("Q", True, "Free-form strategic recommendations"),
    "StrategistAgent": ("Q", False, "Strategy selection; LLM judgment required"),
    "SupremeCourtAgent": ("Q", False, "Final arbiter; LLM judgment required"),
    # L2_execution
    "StructuredEngineAgent": ("D", False, "Structured pipeline, fixed schema"),
    "EmbeddingSovereignAgent": ("D", True, "Embedding ops; already BMG-connected"),
    "GitAgent": ("D", False, "Git operations, fixed semantics"),
    "HistorianAgent": ("D", True, "Records history; retrieves patterns"),
    "PeerIntelligenceAuditorAgent": ("Q", True, "Semantic audit across peers"),
    "RgStrategicPlannerAgent": ("Q", False, "Strategy planning — generative"),
    "SovereignMCPGatewayAgent": ("D", False, "Gateway routing, deterministic dispatch"),
    "SovereignPineconeMcpClientAgent": ("D", True, "Already BMG-connected"),
    "SubAtomicRegistryAgent": ("D", False, "Registry ops, fixed schema"),
    "ToolsmithAgent": ("Q", False, "Tool generation requires LLM reasoning"),
    "UiValidationAgent": ("D", False, "UI schema validation, binary"),
    # L3_orchestration
    "UnifiedAgent": ("H", True, "Orchestrates both deterministic + LLM strategies"),
    "AgentFactory": ("D", False, "Factory instantiation, fixed dispatch"),
    "AgentGym": ("D", False, "Test harness, fixed protocol"),
    "CoverageAgent": ("D", False, "Coverage metric, numeric output"),
    "DAGMutatorAgent": ("Q", False, "DAG mutation — semantic dependency reasoning"),
    "DagRuntimeInspectorAgent": ("D", False, "Runtime state inspection, fixed schema"),
    "NervousSystemAgent": ("Q", True, "Cross-cutting signal routing; pattern recall"),
    "OrchestrationHandshakeAgent": ("D", False, "Protocol handshake, fixed contract"),
    "SemanticGatekeeperAgent": ("Q", True, "Semantic boundary decisions"),
    "SubAtomicAgent": ("D", False, "Atomic unit execution"),
    "SubatomicHopAgent": ("D", False, "Hop protocol, fixed steps"),
    "context_curator_engine": ("Q", True, "Context selection, semantic"),
    "omni_context_engine": ("Q", True, "Omni-context assembly, semantic"),
    "sovereign_mcp_router": ("D", False, "MCP routing, deterministic dispatch"),
    # L4_state
    "CachedStateLedgerAgent": ("D", False, "Cache ledger ops, deterministic"),
    "RedisSovereignAgent": ("D", False, "Redis ops, fixed protocol"),
    "sovereign_reasoning_memory_ledger": ("D", True, "Memory ledger; BMG for pattern retrieval"),
    "sovereign_semantic_cache": ("D", True, "Semantic cache; embedding-adjacent"),
    # L5_safety — QWEN_VLLM
    "AdversarialProbeAgent": ("Q", True, "Novel adversarial probing; pattern recall"),
    "AdversarialRedTeamerAgent": ("Q", False, "Generative red-team scenarios"),
    "AutonomousThreatEvolutionAgent": ("Q", False, "Evolves threat models; LLM required"),
    "ChaosEngineeringAgent": ("Q", False, "Novel chaos scenarios; not enumerable"),
    "CodeHealerAgent": ("Q", True, "Multi-file code repair; semantic context"),
    "CodeDeduplicationAgent": ("Q", True, "Semantic dedup — similarity judgment needed"),
    "ComplexityAnalyzerAgent": ("Q", False, "Complexity narrative — generative analysis"),
    "CognitiveDispositionAgent": ("Q", False, "Cognitive profile assessment; LLM judgment"),
    "ConstitutionalReviewerAgent": ("Q", True, "Constitutional compliance review; semantic"),
    "DocumentationAgent": ("Q", False, "Generates/repairs docstrings; free-form"),
    "DuplicateCodeDetectorAgent": ("Q", True, "Semantic similarity detection"),
    "GenerativeGuardAgent": ("Q", False, "Generative safety — LLM guard"),
    "OmniContextAgent": ("Q", True, "Omni-context; semantic assembly"),
    "PolicyNeuralAutoImmuneAgent": ("Q", False, "Neural policy; not rule-enumerable"),
    "RegressionOracleAgent": ("Q", True, "Generates test cases; queries Pinecone"),
    "SemanticMapperAgent": ("Q", True, "Semantic territory mapping"),
    "SemanticTerritoryMapperAgent": ("Q", True, "Semantic territory classification"),
    "SelfUpdatingSafetyEngineAgent": ("Q", False, "Self-updating; requires generative reasoning"),
    "SystemArchitectAgent": ("Q", False, "Architecture recommendations; generative"),
    "TestGeneratorAgent": ("Q", False, "Generates pytest bodies via AST + LLM"),
    # L5_safety — DETERMINISTIC
    "ArchitectureGovernorAgent": ("D", False, "Architecture rule enforcement, deterministic"),
    "AutonomyGuardianAgent": ("D", False, "Autonomy gate checks, binary"),
    "BoundaryTestingAgent": ("D", False, "Boundary checks, fixed rules"),
    "CachedSafetyShieldAgent": ("D", False, "Cache-based safety shield, deterministic"),
    "CodeDetectorAgent": ("D", False, "Code pattern detection, regex/AST rules"),
    "CodeEnforcerAgent": ("D", False, "Enforcement rules, deterministic"),
    "CodeFormatterAgent": ("D", False, "Formatting rules, deterministic"),
    "CodeValidatorAgent": ("D", False, "Schema/AST validation, binary"),
    "ConfigurationSecurityGuardrailAgent": ("D", False, "Config security rules, deterministic"),
    "CostGovernorAgent": ("D", False, "Cost budget arithmetic"),
    "CredentialScannerAgent": ("D", False, "Credential pattern scanning, deterministic"),
    "DDDAlignmentAgent": ("D", False, "DDD rule alignment, deterministic"),
    "DependencyDiplomatAgent": ("D", False, "Dependency reconciliation, rule-based"),
    "DependencyPruningAgent": ("D", False, "Dependency removal, deterministic"),
    "DynamicSealAgent": ("D", False, "Seal/unseal operations, deterministic"),
    "FileClassificationAgent": ("D", False, "File type classification, kernel-based"),
    "GitHygieneAgent": ("D", False, "Git hygiene checks, deterministic"),
    "GitSafetyHandlerAgent": ("D", False, "Git safety, deterministic ops"),
    "GlobalComplianceAggregatorAgent": ("D", False, "Compliance aggregation, deterministic"),
    "GovernanceAgent": ("D", False, "Governance rule checks, deterministic"),
    "GravityLeakRepairAgent": ("D", False, "Gravity rule repair, fixed moves"),
    "HealValidatorAgent": ("D", False, "Heal output validation, binary"),
    "HierarchyAgent": ("D", False, "Hierarchy checks, AST-based"),
    "HygieneGuardianAgent": ("D", False, "Hygiene rules, deterministic"),
    "InterfaceBoundaryAgent": ("D", False, "Interface boundary checks, deterministic"),
    "L5SafetyExerciserAgent": ("D", False, "Safety exerciser, fixed protocol"),
    "LocationAgent": ("D", False, "File location rules, deterministic"),
    "LocationHealerAgent": ("D", False, "File move/delete healing, fixed rules"),
    "LocationValidatorAgent": ("D", False, "Location validation, path-based"),
    "MCPGuardianAgent": ("D", False, "MCP boundary guardian, deterministic"),
    "NamingAgent": ("D", False, "Naming convention checks, regex rules"),
    "NeuralAutoImmuneAgent": ("D", False, "Autoimmune rule enforcement"),
    "PIISanitizerAgent": ("D", False, "PII redaction — auditability requires determinism"),
    "PineconeSovereignAgent": ("D", True, "Pinecone ops; already BMG-connected"),
    "PreCommitSovereignAgent": ("D", False, "Pre-commit gate — must be deterministic"),
    "PredictiveCostAuditorAgent": ("D", False, "Cost audit arithmetic"),
    "PromptRegistryAgent": ("D", False, "Prompt registry ops, deterministic"),
    "RagHealthCheckAgent": ("D", False, "RAG health checks, deterministic"),
    "RedSentinelAgent": ("D", False, "Sentinel rules, deterministic"),
    "RedTeamAgent": ("D", False, "Fixed red-team scenario execution"),
    "ReportLocationAgent": ("D", False, "Report location rules, deterministic"),
    "ResourceManagerAgent": ("D", False, "Resource management, arithmetic"),
    "RootHygieneAgent": ("D", False, "Root hygiene rules, fixed file checks"),
    "SafetyDetectorAgent": ("D", False, "Safety pattern detection, deterministic"),
    "SafetyExecutorAgent": ("D", False, "Safety action execution, deterministic"),
    "SafetyInspectorAgent": ("D", False, "Inspection rules, deterministic"),
    "SecurityManagerAgent": ("D", False, "Security rule management, deterministic"),
    "SignatureVerifierAgent": ("D", False, "Signature verification, cryptographic"),
    "SovereignActionPlaneAgent": ("D", False, "Action plane dispatch, deterministic"),
    "SprawlInspectorAgent": ("D", False, "File sprawl checks, count-based"),
    "StructuralEngineerAgent": ("D", False, "Structural rule engineering, deterministic"),
    "StructuralValidatorAgent": ("D", False, "Structural validation, AST-based"),
    "StructureEnforcerAgent": ("D", False, "Structure enforcement, deterministic"),
    "StructureHealerAgent": ("D", False, "Structure healing, fixed rule moves"),
    "TerritoryChangeHandlerAgent": ("D", False, "Territory change handler, deterministic"),
    "TestCoverageGuardianAgent": ("D", False, "Coverage metric guardian, numeric"),
    "TokenBudgetInspectorAgent": ("D", False, "Token budget checks, arithmetic"),
    "TypeHintFixerAgent": ("D", False, "Type hint fixes, AST-rule-based"),
    "TypeMechanicAgent": ("D", False, "Type mechanic repairs, AST-based"),
    "UnusedCleanupAgent": ("D", False, "Unused import/var cleanup, AST"),
    "input_validation_guardrail": ("D", False, "Input validation rules, deterministic"),
    "toxic_dependency_auditor": ("D", False, "Toxic dependency rules, deterministic"),
    "verification_gate": ("D", False, "Verification gate — must be deterministic"),
    # L6_observability
    "AutonomicMonitorAgent": ("D", False, "Metric polling, fixed protocol"),
    "CoordinateObservabilityOperationsAgent": ("D", False, "Coordination ops, fixed"),
    "DeadlockDetectorAgent": ("D", False, "Graph/timeout detection, deterministic"),
    "DebateSynthesisAgent": ("Q", False, "Synthesises debate arguments — generative"),
    "MetricsAgent": ("D", False, "Numeric metric aggregation"),
    "MetricsWitnessAgent": ("D", False, "Witness logging, deterministic"),
    "PerformanceAnalystAgent": ("Q", True, "Interprets perf data; semantic narrative"),
    "ReportingAgent": ("Q", False, "Generates human-readable reports"),
    "RuntimeTelemetryAgent": ("D", False, "Telemetry collection, fixed schema"),
    "SovereignObservabilityAgent": ("D", False, "Observability coordination, deterministic"),
    "StrategicObservationAgent": ("Q", True, "Strategic insight from metrics; semantic"),
    "TelemetryAgent": ("D", False, "Telemetry forwarding, deterministic"),
    "TracingAgent": ("D", False, "Trace collection, deterministic"),
    "TrackObservabilityCostAgent": ("D", False, "Cost tracking, numeric"),
    # apps_lic
    "CampaignBalanceAgent": ("D", False, "Balance arithmetic"),
    "DeliverabilityAgent": ("D", False, "Deliverability rule checks"),
    "DispatchOutreachToolsAgent": ("D", False, "Tool dispatch, deterministic"),
    "GovernanceShieldAgent": ("D", False, "Governance rule enforcement"),
    "HOP1ProfileAnalysisAgent": ("Q", True, "Profile semantic analysis"),
    "HOP2ResearchAgent": ("Q", True, "Research + semantic retrieval"),
    "HOP3SenderGroundingAgent": ("Q", True, "Sender persona grounding — generative"),
    "HOP4RoutingAgent": ("D", False, "Routing decision, rule-based"),
    "HOP5GenerationAgent": ("Q", True, "Message generation — primary LLM hop"),
    "HOP6ValidationAgent": ("D", False, "Validation checks, deterministic"),
    "HOP7GateDecisionAgent": ("D", False, "Gate pass/fail, deterministic"),
    "HOP8QAReportAgent": ("Q", True, "QA narrative generation"),
    "HOP9IntegrationAgent": ("D", False, "Integration dispatch, deterministic"),
    "IntelligenceLibrarianAgent": ("Q", True, "Knowledge retrieval + synthesis"),
    "LeadQualityAgent": ("Q", True, "Lead scoring with semantic context"),
    "LicS2SupervisorAgent": ("Q", True, "Supervisory reasoning over pipeline"),
    "MessageArchitectAgent": ("Q", True, "Message architecture planning — generative"),
    "MessageDiversityValidator": ("D", False, "Diversity metric, deterministic"),
    "LicReflectionAgent": ("Q", True, "Reflective learning from outreach cycles"),
    "LicTemplateOptimizerAgent": ("Q", True, "Template selection via semantic fit"),
    "MessageComplianceAgent": ("D", False, "Compliance rule checks, deterministic"),
    "OutreachLearningAgent": ("Q", True, "Learning from outreach history"),
    "OutreachProactiveAgent": ("Q", True, "Proactive outreach strategy — generative"),
    "OutreachSignalRouterAgent": ("D", False, "Signal routing, rule-based"),
    "OutreachValidationExecutorAgent": ("D", False, "Validation execution, deterministic"),
    "PIISanitizerSpecialistAgent": ("D", False, "PII redaction — auditability requires determinism"),
    "ValidatorAgent": ("D", False, "Schema validation, deterministic"),
    # apps_rg
    "ATSCompatibilityAgent": ("D", False, "ATS keyword rules, deterministic"),
    "BrandComplianceAgent": ("Q", False, "Brand voice judgment — semantic"),
    "CampaignPlannerAgent": ("Q", True, "Campaign planning — generative"),
    "ContentQualityAgent": ("Q", True, "Quality assessment — semantic judgment"),
    "ContentStrategyAgent": ("Q", True, "Content strategy generation"),
    "DispatchResumeToolsAgent": ("D", False, "Tool dispatch, deterministic"),
    "FactCheckAgent": ("Q", True, "Claim verification vs profile — semantic"),
    "ProactiveAgent": ("Q", False, "Proactive reasoning — generative"),
    "RgTemplateOptimizerAgent": ("Q", True, "Template optimisation via semantic fit"),
    "SectionBalanceAgent": ("D", False, "Section length arithmetic"),
    # apps_shared
    "AppBase": ("D", False, "Base class, no healing logic"),
    # knowledge
    "SovereignRAGManagerAgent": ("Q", True, "RAG orchestration — LLM + retrieval"),
    # RgHealingOrchestrator (apps_rg/reasoning)
    "RgHealingOrchestrator": ("Q", True, "Orchestrates self-healing cycles; meta-learning"),
    # LicHealingOrchestrator
    "LicHealingOrchestrator": ("Q", True, "Orchestrates LIC self-healing cycles"),
    # Outreach agents with OutreachAgent base
    "OutreachAgent": ("Q", True, "Base outreach agent — generative messaging"),
    # OutreachMessageAgent
    "OutreachMessageAgent": ("Q", True, "Outreach message generation — LLM"),
    # HOPPipelineExecutor
    "HOPPipelineExecutor": ("D", False, "HOP pipeline executor, deterministic"),
}


def _mode_label(m: str) -> str:
    return {"Q": "QWEN_VLLM", "D": "DETERMINISTIC", "H": "HYBRID"}[m]


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _extract_agent_info(filepath: Path) -> dict[str, Any]:
    """Return class_name, bases, methods with their bodies as source snippets."""
    info: dict[str, Any] = {
        "class_name": None,
        "bases": [],
        "methods": {},  # name -> source lines
        "heal_methods": [],
        "imports": [],
        "parse_error": None,
    }
    try:
        src = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(filepath))
        src_lines = src.splitlines()
    # guardian: allow-silent-swallow
    except Exception as e:
        info["parse_error"] = str(e)
        return info

    # Find primary class (prefer name matching stem)
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    if not classes:
        return info
    stem = filepath.stem
    chosen = next((c for c in classes if c.name == stem), None) or classes[0]
    info["class_name"] = chosen.name
    info["bases"] = [
        ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "?") for b in chosen.bases
    ]

    # Extract methods
    for item in chosen.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = item.lineno - 1
            end = item.end_lineno if hasattr(item, "end_lineno") else item.lineno
            body_lines = src_lines[start:end]
            info["methods"][item.name] = body_lines
            if item.name in ("heal", "execute", "act", "run"):
                info["heal_methods"].append(item.name)

    # Collect top-level imports
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            info["imports"].append(ast.unparse(node) if hasattr(ast, "unparse") else "")

    return info


# ---------------------------------------------------------------------------
# Diff generation
# ---------------------------------------------------------------------------

_VLLM_HELPER = '''\
    def _call_qwen_vllm(self, prompt: str, max_tokens: int = 512) -> str:
        """Call local Qwen 14B vLLM endpoint (RTX 5090, http://localhost:8000/v1)."""
        try:
            import openai
            client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="local")
            resp = client.chat.completions.create(
                model="qwen-14b-quantized",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Qwen vLLM call failed: %s", exc)
            return ""
'''

_BMG_HELPER = '''\
    def _retrieve_healing_patterns(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve similar healing patterns from BMG canon-healing-patterns index."""
        try:
            from pinecone import Pinecone
            from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
            import os
            api_key = os.getenv("PINECONE_API_KEY", "")
            if not api_key:
                return []
            emb = EmbeddingServiceFactory.get_service().embed(query)
            pc = Pinecone(api_key=api_key)
            idx = pc.Index("canon-healing-patterns")
            results = idx.query(vector=emb, top_k=top_k, include_metadata=True)
            return [m["metadata"] for m in results.get("matches", [])]
        except Exception as exc:  # noqa: BLE001
            import logging
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through
from tqdm import tqdm
            logging.getLogger(__name__).warning("BMG retrieval failed: %s", exc)
            return []
'''


def _make_diff(rel_path: str, agent_info: dict, mode: str, bmg: bool, rationale: str) -> str:
    """Produce a unified diff showing helper injection + heal/execute modification."""
    fname = rel_path.replace("\\", "/")

    lines: list[str] = []
    lines.append(f"--- a/{fname}")
    lines.append(f"+++ b/{fname}")

    class_name = agent_info.get("class_name") or Path(rel_path).stem
    heal_methods = agent_info.get("heal_methods", [])

    # Hunk 1 — inject helpers after class definition line (conceptual position)
    lines.append("@@ class body — add helper methods @@")
    for helper_line in _VLLM_HELPER.splitlines():
        lines.append(f"+{helper_line}")
    if bmg:
        for helper_line in _BMG_HELPER.splitlines():
            lines.append(f"+{helper_line}")

    # Hunk 2 — show modified healing method stub
    method_name = heal_methods[0] if heal_methods else "execute"
    existing_body = agent_info.get("methods", {}).get(method_name)

    if existing_body:
        lines.append(f"@@ {class_name}.{method_name}() — delegate to Qwen vLLM @@")
        # show first 6 lines of existing body as context to remove
        for ln in existing_body[: min(6, len(existing_body))]:
            lines.append(f"-{ln}")
        if len(existing_body) > 6:
            lines.append(f"-    ... ({len(existing_body) - 6} more lines)")
    else:
        lines.append(f"@@ {class_name}.{method_name}() — add Qwen vLLM delegation @@")

    # Replacement
    is_async = False
    if existing_body:
        is_async = any(ln.strip().startswith("async def") for ln in existing_body[:2])

    async_kw = "async " if is_async else ""
    lines.append(f"+    {async_kw}def {method_name}(self, *args, **kwargs):")
    lines.append(f'+        """[QWEN_VLLM] {rationale}"""')
    if bmg:
        lines.append("+        patterns = self._retrieve_healing_patterns(")
        lines.append('+            f"healing context for {self.__class__.__name__}: {args}"')
        lines.append("+        )")
        lines.append("+        context = '\\n'.join(str(p) for p in patterns[:3])")
        lines.append("+        prompt = (")
        lines.append(f'+            f"You are {class_name}. Past patterns:\\n{{context}}\\n\\n"')
        lines.append('+            f"Task: {args!r}\\nKwargs: {kwargs!r}\\n"')
        lines.append(
            '+            "Produce a healing recommendation as JSON with keys: status, actions, rationale."',
        )
        lines.append("+        )")
    else:
        lines.append("+        prompt = (")
        lines.append(f'+            f"You are {class_name}. "')
        lines.append('+            f"Task: {args!r}\\nKwargs: {kwargs!r}\\n"')
        lines.append(
            '+            "Produce a healing recommendation as JSON with keys: status, actions, rationale."',
        )
        lines.append("+        )")
    lines.append("+        result = self._call_qwen_vllm(prompt)")
    lines.append("+        import json as _json")
    lines.append("+        try:")
    lines.append("+            return _json.loads(result)")
    lines.append("+        except Exception:")
    lines.append('+            return {"status": "ok", "actions": [], "rationale": result}')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------


def build_report() -> str:
    ssot = json.loads(SSOT_JSON.read_text(encoding="utf-8"))
    agents: list[dict] = ssot["agents"]
    total = len(agents)

    # Classify + collect AST info
    rows: list[dict] = []
    for entry in tqdm(agents, desc="Processing", unit="item"):
        rel = entry["file"]
        class_name = entry.get("class_name") or Path(rel).stem
        layer = entry.get("layer", "unknown")
        filepath = REPO_ROOT / rel

        # Look up classification — try class_name first, then stem
        ct_key = class_name
        if ct_key not in _CT:
            ct_key = Path(rel).stem
        if ct_key not in _CT:
            # default unknown → deterministic
            ct_key = None

        if ct_key:
            raw_mode, bmg, rationale = _CT[ct_key]
        else:
            raw_mode, bmg, rationale = "D", False, "No classification entry — default deterministic"

        mode = _mode_label(raw_mode)

        agent_info: dict = {}
        if filepath.exists():
            agent_info = _extract_agent_info(filepath)

        rows.append(
            {
                "file": rel,
                "class_name": class_name,
                "layer": layer,
                "mode": mode,
                "raw_mode": raw_mode,
                "bmg": bmg,
                "rationale": rationale,
                "agent_info": agent_info,
                "filepath": filepath,
            },
        )

    # Summary counts
    q_rows = [r for r in rows if r["raw_mode"] == "Q"]
    d_rows = [r for r in rows if r["raw_mode"] == "D"]
    h_rows = [r for r in rows if r["raw_mode"] == "H"]
    bmg_rows = [r for r in rows if r["bmg"]]

    # -----------------------------------------------------------------------
    # Build markdown
    # -----------------------------------------------------------------------
    md: list[str] = []

    md.append("# Qwen vLLM 14B Healing Recommendations — All 190 Agents")
    md.append("")
    md.append("**Generated by**: `ops_scripts/general/generate_qwen_healing_report.py`  ")
    md.append("**No source files modified.** This is a recommendation artifact only.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Configuration")
    md.append("")
    md.append("| Parameter | Value |")
    md.append("|---|---|")
    md.append(f"| vLLM endpoint | `{VLLM_BASE_URL}` (already running) |")
    md.append("| GPU | RTX 5090 |")
    md.append(f"| Model | `{VLLM_MODEL}` |")
    md.append(f"| BMG index | `{BMG_INDEX}` (dim={BMG_DIM}, cosine, AWS us-east-1) |")
    md.append(
        "| BMG embedding source | `system_learning.engines.embedding_service_factory.EmbeddingServiceFactory` |",
    )
    md.append("| Diff format | Unified git-diff (copy-pastable) |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Executive Summary")
    md.append("")
    md.append("| Mode | Count | % |")
    md.append("|---|---|---|")
    md.append(f"| QWEN_VLLM | {len(q_rows)} | {len(q_rows) * 100 // total}% |")
    md.append(f"| DETERMINISTIC | {len(d_rows)} | {len(d_rows) * 100 // total}% |")
    md.append(f"| HYBRID | {len(h_rows)} | {len(h_rows) * 100 // total}% |")
    md.append(f"| **Total** | **{total}** | 100% |")
    md.append("")
    md.append(f"**BMG embeddings added**: {len(bmg_rows)} agents")
    md.append("")
    md.append("### Classification Criteria")
    md.append("")
    md.append("**Use Qwen vLLM 14B when ANY of:**")
    md.append("1. `heal()`/`execute()`/`act()` requires semantic judgment on prose or intent")
    md.append("2. Agent generates free-form content (docstrings, test bodies, messages, resume sections)")
    md.append("3. Multi-file cross-cutting repair needs contextual understanding beyond enumerable rules")
    md.append("4. Novel/ambiguous violations not reducible to a fixed rule set")
    md.append("5. Agent performs strategy selection or reflection across past outcomes")
    md.append("")
    md.append("**Keep Deterministic when ALL of:**")
    md.append("1. Violation is structurally enumerable (path match, regex, AST node present/absent)")
    md.append("2. Repair is a fixed action (file move, import fix, counter increment, JSON write)")
    md.append("3. Safety-critical path requiring auditability (PII, pre-commit, credential scan)")
    md.append("4. Output is a scalar/boolean (cost budget, token count, coverage %)")
    md.append("")
    md.append("**Add BMG embeddings** (`canon-healing-patterns`) when agent needs past healing pattern")
    md.append("recall or is already connected to Pinecone/EmbeddingSovereignAgent/DeepBrainHarvester.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Shared Integration Helpers")
    md.append("")
    md.append("These two helpers are injected into every `QWEN_VLLM`-tagged agent class.")
    md.append("Agents with `BMG=YES` receive both; others receive only `_call_qwen_vllm`.")
    md.append("")
    md.append("```python")
    md.append(_VLLM_HELPER.rstrip())
    md.append("")
    md.append(_BMG_HELPER.rstrip())
    md.append("```")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Full Classification Table (190 agents)")
    md.append("")
    md.append("| Agent | File | Layer | Mode | BMG | Rationale |")
    md.append("|---|---|---|---|---|---|")

    # Group by layer for readability
    layer_order = [
        L0_ROUTING_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "knowledge",
    ]
    by_layer: dict[str, list] = {}
    for r in rows:
        by_layer.setdefault(r["layer"], []).append(r)

    for layer in layer_order:
        layer_rows = by_layer.get(layer, [])
        for r in layer_rows:
            bmg_str = "YES" if r["bmg"] else "NO"
            file_short = r["file"].replace("\\", "/")
            md.append(
                f"| `{r['class_name']}` | `{file_short}` | {r['layer']} "
                f"| **{r['mode']}** | {bmg_str} | {r['rationale']} |",
            )

    # Any layers not in canonical order
    for layer, layer_rows in by_layer.items():
        if layer not in layer_order:
            for r in layer_rows:
                bmg_str = "YES" if r["bmg"] else "NO"
                file_short = r["file"].replace("\\", "/")
                md.append(
                    f"| `{r['class_name']}` | `{file_short}` | {r['layer']} "
                    f"| **{r['mode']}** | {bmg_str} | {r['rationale']} |",
                )

    md.append("")
    md.append("---")
    md.append("")
    md.append("## Per-Agent Unified Diffs — QWEN_VLLM Agents")
    md.append("")
    md.append(
        f"> The following {len(q_rows) + len(h_rows)} diffs show exactly where to inject "
        "`_call_qwen_vllm()` (and `_retrieve_healing_patterns()` for BMG agents) "
        "into each agent's healing/execution method. **No file is modified by this script.**",
    )
    md.append("")

    # Emit diffs grouped by layer
    for layer in tqdm(layer_order, desc="Processing", unit="item"):
        layer_q = [r for r in by_layer.get(layer, []) if r["raw_mode"] in ("Q", "H")]
        if not layer_q:
            continue
        md.append(f"### {layer} ({len(layer_q)} agents)")
        md.append("")
        for r in layer_q:
            bmg_flag = " + BMG" if r["bmg"] else ""
            md.append(f"#### `{r['class_name']}` — {r['mode']}{bmg_flag}")
            md.append(f"> {r['rationale']}")
            md.append("")
            md.append("```diff")
            diff = _make_diff(r["file"], r["agent_info"], r["raw_mode"], r["bmg"], r["rationale"])
            md.append(diff)
            md.append("```")
            md.append("")

    # Any remaining HYBRID not in canonical order
    for layer, layer_rows in tqdm(by_layer.items(), desc="Processing", unit="item"):
        if layer not in layer_order:
            layer_q = [r for r in layer_rows if r["raw_mode"] in ("Q", "H")]
            if not layer_q:
                continue
            md.append(f"### {layer} ({len(layer_q)} agents)")
            md.append("")
            for r in layer_q:
                bmg_flag = " + BMG" if r["bmg"] else ""
                md.append(f"#### `{r['class_name']}` — {r['mode']}{bmg_flag}")
                md.append(f"> {r['rationale']}")
                md.append("")
                md.append("```diff")
                diff = _make_diff(r["file"], r["agent_info"], r["raw_mode"], r["bmg"], r["rationale"])
                md.append(diff)
                md.append("```")
                md.append("")

    md.append("---")
    md.append("")
    md.append("## Implementation Notes")
    md.append("")
    md.append("### vLLM Client Setup (already running)")
    md.append("```python")
    md.append("import openai")
    md.append('client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="local")')
    md.append("resp = client.chat.completions.create(")
    md.append('    model="qwen-14b-quantized",')
    md.append('    messages=[{"role": "user", "content": prompt}],')
    md.append("    max_tokens=512,")
    md.append("    temperature=0.2,")
    md.append(")")
    md.append("```")
    md.append("")
    md.append("### BMG Retrieval Pattern")
    md.append("```python")
    md.append("from pinecone import Pinecone")
    md.append("from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory")
    md.append('pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))')
    md.append('idx = pc.Index("canon-healing-patterns")  # dim=1536, cosine')
    md.append("emb = EmbeddingServiceFactory.get_service().embed(query)")
    md.append("results = idx.query(vector=emb, top_k=5, include_metadata=True)")
    md.append("```")
    md.append("")
    md.append("### RTX 5090 VRAM Budget")
    md.append("| Parameter | Value |")
    md.append("|---|---|")
    md.append("| GPU VRAM | 24 GB |")
    md.append("| Qwen 14B Q4 footprint | ~8 GB |")
    md.append("| Available for KV cache | ~16 GB |")
    md.append("| Max context (est.) | ~32k tokens at Q4 |")
    md.append("| Recommended max_tokens | 512 per healing call |")
    md.append("| Batch size | 1 (sequential, no batching needed for healing) |")
    md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"OK: report written to {REPORT_PATH}")
    # Print a quick summary
    lines = report.splitlines()
    q_count = sum(1 for l in lines if "| **QWEN_VLLM**" in l)
    d_count = sum(1 for l in lines if "| **DETERMINISTIC**" in l)
    h_count = sum(1 for l in lines if "| **HYBRID**" in l)
    print(f"OK: QWEN_VLLM={q_count}  DETERMINISTIC={d_count}  HYBRID={h_count}")
