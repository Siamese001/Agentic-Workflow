"""
[PHASE 11] Cognitive Disposition Agent - AI-Powered Architectural Triage.

Uses LLM API to analyze structural violations and determine intelligent resolutions.
This agent provides "Intelligent Triage" for files flagged by the ArchitectureGovernorAgent.

Responsibilities:
- Analyze ORPHAN violations and recommend proper SSOT locations
- Analyze GRAVITY violations and suggest refactoring strategies
- Analyze DUPLICATE violations and recommend consolidation targets
- Return structured DispositionDecision with action, target, and confidence

Actions:
- MOVE: Relocate file to suggested target_path
- REFACTOR: Apply suggested code changes
- ARCHIVE: Move to archives for later review
- IGNORE: No action needed (false positive)
- MANUAL_REVIEW: Requires human decision

[SSOT] Integrates with ArchitectureGovernorAgent for violation resolution.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

Logger = logging.getLogger(__name__)


@dataclass
class DispositionDecision:
    """Structured decision from cognitive analysis."""
    
    action: str  # MOVE, REFACTOR, ARCHIVE, IGNORE, MANUAL_REVIEW
    target_path: Optional[str] = None
    reason: str = ""
    confidence: float = 0.0
    suggested_code: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate action is one of the allowed values."""
        valid_actions = {"MOVE", "REFACTOR", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"}
        if self.action not in valid_actions:
            raise ValueError(f"Invalid action: {self.action}. Must be one of {valid_actions}")
        
        # Clamp confidence to [0.0, 1.0]
        self.confidence = max(0.0, min(1.0, self.confidence))


class CognitiveDispositionAgent:
    """
    AI-Powered Architectural Triage Agent.
    
    Analyzes structural violations and determines intelligent resolutions
    using LLM capabilities.
    
    Attributes:
        project_root: Root directory of the project
        confidence_threshold: Minimum confidence to auto-execute decisions
        llm_enabled: Whether to use actual LLM calls (vs mock responses)
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        confidence_threshold: float = 0.8,
        llm_enabled: bool = False,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Cognitive Disposition Agent.
        
        Args:
            project_root: Project root directory
            confidence_threshold: Minimum confidence for auto-execution
            llm_enabled: Enable actual LLM API calls
            api_key: API key for LLM service (defaults to env var)
        """
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        self.llm_enabled = llm_enabled
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._llm_client = None
        
        # Layer mapping for SSOT compliance
        self.layer_map = {
            "L0_maintenance": "Maintenance and tooling",
            "L1_cognition": "Cognitive processing and thought engines",
            "L2_execution": "Execution and tool orchestration",
            "L3_orchestration": "Workflow orchestration",
            "L4_state": "State management and persistence",
            "L5_safety": "Safety, validation, and governance",
            "L6_observability": "Observability and telemetry",
        }
    
    def analyze_violation(
        self,
        file_path: str | Path,
        violation_type: str,
        context: Optional[dict[str, Any]] = None,
    ) -> DispositionDecision:
        """
        Analyze a violation and return a disposition decision.
        
        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY, DUPLICATE, etc.)
            context: Additional context about the violation
        
        Returns:
            DispositionDecision with recommended action
        """
        file_path = Path(file_path)
        context = context or {}
        
        Logger.info(f"[COGNITIVE] Analyzing disposition for {file_path.name} ({violation_type})...")
        
        # If LLM is enabled, use actual API call
        if self.llm_enabled and self.api_key:
            return self._analyze_with_llm(file_path, violation_type, context)
        
        # Otherwise, use heuristic-based analysis
        return self._analyze_heuristic(file_path, violation_type, context)
    
    def _analyze_heuristic(
        self,
        file_path: Path,
        violation_type: str,
        context: dict[str, Any],
    ) -> DispositionDecision:
        """
        Heuristic-based analysis when LLM is not available.
        
        Uses file naming patterns and location to suggest disposition.
        """
        file_name = file_path.name
        file_stem = file_path.stem
        
        # ORPHAN violations - suggest based on naming patterns
        if violation_type == "ORPHAN":
            return self._analyze_orphan_heuristic(file_path, file_name, file_stem)
        
        # GRAVITY violations - suggest archive for failed repairs
        elif violation_type in ("GRAVITY", "GRAVITY_FAIL"):
            return DispositionDecision(
                action="ARCHIVE",
                target_path="archives/gravity_violations",
                reason=f"Gravity violation requires import refactoring: {file_name}",
                confidence=0.6,
                metadata={"original_path": str(file_path)},
            )
        
        # DUPLICATE violations - suggest archive
        elif violation_type == "DUPLICATE":
            return DispositionDecision(
                action="ARCHIVE",
                target_path="archives/deduplication_cleanup",
                reason=f"Duplicate detected, archiving for consolidation review: {file_name}",
                confidence=0.7,
                metadata={"original_path": str(file_path)},
            )
        
        # Default: manual review
        return DispositionDecision(
            action="MANUAL_REVIEW",
            reason=f"Unknown violation type requires human review: {violation_type}",
            confidence=0.0,
        )
    
    def _analyze_orphan_heuristic(
        self,
        file_path: Path,
        file_name: str,
        file_stem: str,
    ) -> DispositionDecision:
        """
        Heuristic analysis for ORPHAN violations.
        
        Suggests target location based on file naming patterns.
        """
        # Agent files -> L5_safety or appropriate layer
        if file_name.endswith("Agent.py"):
            # Check for layer hints in the name
            if any(x in file_stem.lower() for x in ["validator", "enforcer", "governor", "safety"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L5_safety/validators",
                    reason=f"Agent with safety/validator pattern: {file_name}",
                    confidence=0.75,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["healer", "repair", "fixer"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L5_safety/repair",
                    reason=f"Agent with healer/repair pattern: {file_name}",
                    confidence=0.75,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["orchestrat", "workflow", "coordinator"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L3_orchestration",
                    reason=f"Agent with orchestration pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["observ", "telemetry", "metric", "monitor"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L6_observability",
                    reason=f"Agent with observability pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["state", "checkpoint", "persist", "ledger"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L4_state",
                    reason=f"Agent with state management pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["tool", "execute", "mcp"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L2_execution",
                    reason=f"Agent with execution pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["thought", "cognit", "reason", "prompt"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L1_cognition",
                    reason=f"Agent with cognition pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            else:
                # Default: archive for review
                return DispositionDecision(
                    action="ARCHIVE",
                    target_path="archives/orphan_agents",
                    reason=f"Orphan agent with unclear layer affinity: {file_name}",
                    confidence=0.5,
                    metadata={"original_path": str(file_path)},
                )
        
        # Test files -> tests directory
        if file_name.startswith("test_") or file_name.endswith("_test.py"):
            return DispositionDecision(
                action="MOVE",
                target_path="tests/unit",
                reason=f"Test file should be in tests directory: {file_name}",
                confidence=0.85,
                metadata={"original_path": str(file_path)},
            )
        
        # Script files -> scripts directory
        if "script" in str(file_path).lower() or file_name.startswith("run_"):
            return DispositionDecision(
                action="MOVE",
                target_path="scripts/maintenance",
                reason=f"Script file should be in scripts directory: {file_name}",
                confidence=0.7,
                metadata={"original_path": str(file_path)},
            )
        
        # Default: archive for review
        return DispositionDecision(
            action="ARCHIVE",
            target_path="archives/orphan_files",
            reason=f"Orphan file with unclear destination: {file_name}",
            confidence=0.4,
            metadata={"original_path": str(file_path)},
        )
    
    def _analyze_with_llm(
        self,
        file_path: Path,
        violation_type: str,
        context: dict[str, Any],
    ) -> DispositionDecision:
        """
        LLM-based analysis using Gemini API.
        
        Constructs a prompt and parses the structured response.
        """
        try:
            # Read file content for analysis
            content = ""
            if file_path.exists() and file_path.stat().st_size < 50000:  # 50KB limit
                content = file_path.read_text(encoding="utf-8", errors="ignore")[:5000]
            
            # Construct prompt
            prompt = self._build_analysis_prompt(file_path, violation_type, content, context)
            
            # Call LLM (placeholder for actual implementation)
            # response = self._call_llm(prompt)
            # return self._parse_llm_response(response)
            
            # For now, fall back to heuristic
            Logger.warning("[COGNITIVE] LLM integration pending, using heuristic fallback")
            return self._analyze_heuristic(file_path, violation_type, context)
            
        except Exception as e:
            Logger.error(f"[COGNITIVE] LLM analysis failed: {e}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"LLM analysis failed: {e}",
                confidence=0.0,
            )
    
    def _build_analysis_prompt(
        self,
        file_path: Path,
        violation_type: str,
        content: str,
        context: dict[str, Any],
    ) -> str:
        """Build the analysis prompt for LLM."""
        return f"""Analyze this architectural violation and recommend a disposition.

File: {file_path}
Violation Type: {violation_type}
Context: {context}

Layer Structure (SSOT):
{self.layer_map}

File Content (truncated):
```python
{content[:2000]}
```

Respond with JSON:
{{
    "action": "MOVE|REFACTOR|ARCHIVE|IGNORE",
    "target_path": "suggested/path/if/MOVE",
    "reason": "explanation",
    "confidence": 0.0-1.0
}}
"""
    
    def should_auto_execute(self, decision: DispositionDecision) -> bool:
        """
        Determine if a decision should be auto-executed.
        
        Args:
            decision: The disposition decision
        
        Returns:
            True if confidence meets threshold and action is executable
        """
        executable_actions = {"MOVE", "ARCHIVE"}
        return (
            decision.action in executable_actions
            and decision.confidence >= self.confidence_threshold
        )
