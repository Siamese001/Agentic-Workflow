from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_orchestrates_workflow,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,  # noqa: E402
)

_emit_routes_to_agent("p1", "knowledge_graph_healing_strategy", "L3")
_emit_orchestrates_workflow("p1", "knowledge_graph_healing_strategy", "L3")
_emit_dispatches_execution_plan("p1", "knowledge_graph_healing_strategy", "L3")
_emit_validates_agent_capability("p1", "knowledge_graph_healing_strategy", "L3")
_emit_checks_agent_registry("p1", "knowledge_graph_healing_strategy", "L3")

"\nSovereign Knowledge Graph Healing Strategy – Phase 17C (Dec 27, 2025)\nDetects and autonomously corrects structured memory drift.\nL4 state self-healing using official Memory MCP.\n"
import ast
import logging
import re
import uuid
from datetime import datetime
from typing import Any

from agentic_core.L0_routing.utils.filesystem_mcp_client import get_filesystem_client
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger: Any = logging.getLogger(__name__)


class KnowledgeGraphHealingStrategy:
    """
    Autonomous healing for knowledge graph drift.

    Detects and corrects KG inconsistencies by:
    - Re-extracting entities and relations from source content
    - Applying confidence thresholds for quality control
    - Using Memory MCP for all KG operations
    - Enforcing daily healing limits to prevent runaway operations
    """

    def __init__(self):
        """Initialize knowledge graph healing strategy with MCP clients."""
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

        self.name = "KnowledgeGraphHealing"
        self.priority = 2
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        self._bridge = GraphMemoryBridge.get_instance()
        Logger.info("[L0 KG HEALING] Strategy initialized")

    async def diagnose(self, issues: list[dict]) -> list[dict]:
        """
        Diagnose KG drift from auditor issues or proactive scan.

        Args:
            issues: List of issues from sovereignty auditor

        Returns:
            List of fix dictionaries with action details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "KnowledgeGraphHealingStrategy.diagnose",
        )

        fixes: Any = []
        if not config.KNOWLEDGE_GRAPH_HEALING_ENABLED:
            Logger.info("[L0 KG HEALING] Knowledge graph healing disabled in config")
            return fixes
        for issue in issues:
            desc: Any = issue.get("description", "").lower()
            message: Any = issue.get("message", "").lower()
            if any(
                keyword in desc or keyword in message
                for keyword in ["knowledge graph", "entity", "relation", "kg"]
            ):
                fixes.append(
                    {
                        "action": "re_extract_content",
                        "file": issue.get("file"),
                        "source_id": issue.get("source_id", issue.get("file")),
                        "reason": "Knowledge graph drift detected (Missing/Stale Entities)",
                        "priority": self.priority,
                        "strategy": self.name,
                    },
                )
        Logger.info(f"[L0 KG HEALING] Diagnosed {len(fixes)} knowledge graph drift issues")
        return fixes

    async def apply(self, fix: dict, ctx: Any = None) -> bool:
        """
        Apply KG healing via Sovereign Clients.

        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)

        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.KNOWLEDGE_GRAPH_HEALING_ENABLED:
            Logger.warning("[L0 KG HEALING] Knowledge graph healing disabled in config")
            return False
        if self.processed_today >= config.KG_HEALING_MAX_DAILY:
            Logger.warning("[L0 KG HEALING] Daily limit reached. Pausing for governance.")
            return False
        try:
            file_path: Any = fix.get("file")
            source_id: Any = fix.get("source_id", file_path)
            if not file_path:
                Logger.error("[L0 KG HEALING] No file path in fix")
                return False
            Logger.info(f"[L0 KG HEALING] Reading file: {file_path}")
            content: Any = await self.fs_client.read_text(file_path)
            if not content:
                Logger.warning(f"[L0 KG HEALING] Empty content for {file_path}")
                return False
            Logger.info(f"[L0 KG HEALING] Extracting entities/relations for {source_id}")
            result: Any = await self._extract_entities_relations(content, source_id)
            if not result:
                Logger.error(f"[L0 KG HEALING] Failed to extract entities/relations for {source_id}")
                return False
            entities: Any = [
                e
                for e in result.get("entities", [])
                if e.get("confidence", 0) >= config.KG_MIN_CONFIDENCE_FOR_HEALING
            ]
            relations: Any = [
                r
                for r in result.get("relations", [])
                if r.get("confidence", 0) >= config.KG_MIN_CONFIDENCE_FOR_HEALING
            ]
            if entities or relations:
                Logger.info(
                    f"[L0 KG HEALING] Persisting {len(entities)} entities and {len(relations)} relations",
                )
                persist_result: Any = await self._persist_kg_data(entities, relations, source_id)
                if persist_result:
                    self.processed_today += 1
                    Logger.info(
                        f"[L0 KG HEALING] KG Synchronized: {source_id} | {len(entities)}e, {len(relations)}r",
                    )
                    return True
                else:
                    Logger.error(f"[L0 KG HEALING] Failed to persist KG data for {source_id}")
                    return False
            else:
                Logger.warning(
                    f"[L0 KG HEALING] No entities/relations met confidence threshold for {source_id}",
                )
                return False
        except (RuntimeError, ValueError) as e:
            Logger.error(f"[L0 KG HEALING] KG healing failed for {fix.get('source_id', 'unknown')}: {e}")
            return False

    async def _extract_entities_relations(self, text: str, source_id: str) -> dict[str, Any]:
        """
        Extract entities and relations from text content.

        Parses Python source using AST to extract:
        - Class definitions → entities of type "Class"
        - Function/method definitions → entities of type "Function"
        - Import statements → IMPORTS_FROM relations between module and source

        Falls back to regex for non-Python content.

        Args:
            text: Text content to extract from
            source_id: Source identifier for tracking

        Returns:
            Dictionary with entities and relations or None if failed
        """
        try:
            Logger.info(f"[L0 KG HEALING] Extracting entities/relations from {source_id}")
            entities: list[dict] = []
            relations: list[dict] = []
            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        entities.append(
                            {
                                "name": node.name,
                                "entityType": "Class",
                                "observations": [f"Defined in {source_id} at line {node.lineno}"],
                                "confidence": 0.95,
                            },
                        )
                        relations.append(
                            {
                                "from": source_id,
                                "to": node.name,
                                "relationType": "DEFINES_CLASS",
                                "confidence": 0.95,
                            },
                        )
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        entities.append(
                            {
                                "name": node.name,
                                "entityType": "Function",
                                "observations": [f"Defined in {source_id} at line {node.lineno}"],
                                "confidence": 0.9,
                            },
                        )
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            relations.append(
                                {
                                    "from": source_id,
                                    "to": alias.name,
                                    "relationType": "IMPORTS",
                                    "confidence": 0.85,
                                },
                            )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        relations.append(
                            {
                                "from": source_id,
                                "to": node.module,
                                "relationType": "IMPORTS_FROM",
                                "confidence": 0.85,
                            },
                        )
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                for match in re.finditer("(?m)^class (\\w+)", text):
                    entities.append(
                        {
                            "name": match.group(1),
                            "entityType": "Class",
                            "observations": [f"Regex-extracted from {source_id}"],
                            "confidence": 0.7,
                        },
                    )
                for match in re.finditer("(?m)^def (\\w+)", text):
                    entities.append(
                        {
                            "name": match.group(1),
                            "entityType": "Function",
                            "observations": [f"Regex-extracted from {source_id}"],
                            "confidence": 0.65,
                        },
                    )
            result = {
                "entities": entities,
                "relations": relations,
                "source_id": source_id,
                "extracted_at": datetime.utcnow().isoformat(),
            }
            Logger.info(
                f"[L0 KG HEALING] Extraction complete for {source_id}: {len(entities)} entities, {len(relations)} relations",
            )
            return result
        except (RuntimeError, ValueError) as e:
            Logger.error(f"[L0 KG HEALING] Entity/relation extraction failed: {e}")
            return None

    async def _persist_kg_data(self, entities: list[dict], relations: list[dict], source_id: str) -> bool:
        """
        Persist entities and relations to L4 state via GraphMemoryBridge → mcp11.

        Args:
            entities: List of entity dictionaries
            relations: List of relation dictionaries
            source_id: Source identifier for tracking

        Returns:
            True if persistence succeeded, False otherwise
        """
        try:
            Logger.info(f"[L0 KG HEALING] Persisting KG data for {source_id}")
            self._bridge.create_agent_entity(
                agent_name=source_id,
                agent_type="SourceFile",
                observations=[f"Healed KG snapshot taken at {datetime.utcnow().isoformat()}"],
            )
            for entity in entities:
                self._bridge.create_agent_entity(
                    agent_name=entity["name"],
                    agent_type=entity.get("entityType", "Entity"),
                    observations=entity.get("observations"),
                )
            for rel in relations:
                self._bridge.create_relation(
                    from_entity=rel["from"], to_entity=rel["to"], relation_type=rel["relationType"],
                )
            Logger.info(
                f"[L0 KG HEALING] Persistence complete for {source_id}: {len(entities)} entities, {len(relations)} relations",
            )
            return True
        except (RuntimeError, ValueError) as e:
            Logger.error(f"[L0 KG HEALING] KG data persistence failed: {e}")
            return False

    def reset_daily_counter(self) -> Any:
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        Logger.info("[L0 KG HEALING] Daily counter reset")


async def create_kg_healing_strategy() -> KnowledgeGraphHealingStrategy:
    """
    Factory function to create a knowledge graph healing strategy.

    Returns:
        Initialized KnowledgeGraphHealingStrategy instance
    """
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module.create_kg_healing_strategy")
    return KnowledgeGraphHealingStrategy()
