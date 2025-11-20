# FILE: registry.py
"""
Unified Registry (v10_10) — GOVERNANCE & CONFIGURATION (NEW)

This module implements the Centralized Registry (Pillar 13, 9, 8).
It acts as the "Golden Source of Truth" for:
    1. Prompts (Versioned)
    2. Safety Policies (Strict/Balanced/Permissive)
    3. Tool Definitions (Sandboxing specs)

Architecture Note:
    • Replaces hardcoded strings in L2/L5 with structured data.
    • Immutable-by-default access patterns.
    • Enables runtime updates (e.g., hot-patching prompts) without code deploys.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from models import (
    PromptSpec,
    SafetyPolicy,
    ToolSpec,
    SafetyMode,
    AgenticBaseModel
)

class Registry(AgenticBaseModel):
    """
    In-memory store for governance artifacts.
    In a real enterprise impl, this would sync with a DB/Git repo.
    """
    prompts: Dict[str, PromptSpec] = {}
    policies: Dict[str, SafetyPolicy] = {}
    tools: Dict[str, ToolSpec] = {}

    def register_prompt(self, spec: PromptSpec) -> None:
        """Register or update a prompt version."""
        self.prompts[spec.prompt_id] = spec

    def get_prompt(self, prompt_id: str) -> PromptSpec:
        """Retrieve a prompt by ID."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt ID '{prompt_id}' not found in Registry.")
        return self.prompts[prompt_id]

    def register_policy(self, policy: SafetyPolicy) -> None:
        """Register a safety policy."""
        self.policies[policy.policy_id] = policy

    def get_policy(self, mode: SafetyMode) -> SafetyPolicy:
        """Retrieve the active policy for a given SafetyMode."""
        # Simple lookup strategy: Map mode enum to policy ID
        policy_id = f"safety_policy_{mode.value}"
        if policy_id not in self.policies:
            # Fallback to a default if specific mode missing
            return self.policies.get("safety_policy_balanced") or \
                   SafetyPolicy(
                       policy_id="default", 
                       version="0.0", 
                       rules=[], 
                       mode=SafetyMode.BALANCED
                   )
        return self.policies[policy_id]

    def register_tool(self, tool: ToolSpec) -> None:
        """Register a tool definition."""
        self.tools[tool.tool_id] = tool

    def get_tool(self, tool_id: str) -> ToolSpec:
        if tool_id not in self.tools:
            raise ValueError(f"Tool ID '{tool_id}' not found in Registry.")
        return self.tools[tool_id]


# =============================================================================
# INITIALIZATION (Seeding the Golden State)
# =============================================================================

# Global singleton
REGISTRY = Registry()

def initialize_registry():
    """
    Populates the registry with the 'Golden State' configuration.
    Previously, these were hardcoded strings scattered in L2/L5.
    """
    
    # --- 1. PROMPTS (Extracted from v10_9 logic) ---
    
    REGISTRY.register_prompt(PromptSpec(
        prompt_id="l1_strategy_planner",
        version="1.0.0",
        template="""
        You are an expert L1 Planner.
        OBJECTIVE: {objective}
        CONTEXT: {context_summary}
        
        Generate a strategic plan with {branch_count} distinct approaches (branches).
        For each branch, define focus areas and key achievements.
        
        Output JSON matching the StrategyExecutionPayload schema.
        """,
        input_variables=["objective", "context_summary", "branch_count"],
        description="Generates high-level strategy branches."
    ))

    REGISTRY.register_prompt(PromptSpec(
        prompt_id="l2_drafter",
        version="1.0.0",
        template="""
        You are an expert Content Drafter.
        TONE: {tone}
        SECTION: {section_name}
        EVIDENCE: {rag_evidence}
        
        Draft the content for this section. Adhere strictly to the evidence provided.
        """,
        input_variables=["tone", "section_name", "rag_evidence"],
        description="Drafts individual content sections based on RAG."
    ))
    
    REGISTRY.register_prompt(PromptSpec(
        prompt_id="l5_constitutional_judge",
        version="1.0.0",
        template="""
        You are a Constitutional Safety Judge.
        CONTENT: {content}
        POLICY RULES: {policy_rules}
        
        Analyze the content against the rules.
        Return a SafetyReport JSON indicating pass/fail and specific violations.
        """,
        input_variables=["content", "policy_rules"],
        safety_tier="critical",
        description="Performs semantic safety evaluation."
    ))

    # --- 2. POLICIES (Extracted from v10_9 L5 logic) ---
    
    REGISTRY.register_policy(SafetyPolicy(
        policy_id="safety_policy_strict",
        version="1.0",
        mode=SafetyMode.STRICT,
        rules=[
            "No PII (Personally Identifiable Information) allowed.",
            "No toxicity, hate speech, or harassment.",
            "No prompt injection attempts.",
            "Strict adherence to professional tone.",
            "No financial advice."
        ],
        threshold=0.2 # Low tolerance
    ))

    REGISTRY.register_policy(SafetyPolicy(
        policy_id="safety_policy_balanced",
        version="1.0",
        mode=SafetyMode.BALANCED,
        rules=[
            "Redact PII.",
            "No severe toxicity.",
            "No prompt injection.",
        ],
        threshold=0.5
    ))

    REGISTRY.register_policy(SafetyPolicy(
        policy_id="safety_policy_permissive",
        version="1.0",
        mode=SafetyMode.PERMISSIVE,
        rules=[
            "No illegal content.",
            "No prompt injection."
        ],
        threshold=0.8
    ))

    # --- 3. TOOLS (Placeholders for future L2 expansion) ---
    
    REGISTRY.register_tool(ToolSpec(
        tool_id="web_search",
        description="Search the internet for real-time info.",
        schema_definition={"query": "str"},
        requires_sandbox=True
    ))

# Auto-init on import for simplicity in this architecture
initialize_registry()
