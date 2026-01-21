"""
[PHASE 11/12] Cognitive Disposition Agent - AI-Powered Architectural Triage.

Uses LLM API (Gemini) to analyze structural violations and determine intelligent resolutions.
This agent provides "Intelligent Triage" for files flagged by the ArchitectureGovernorAgent.

Phase 11: Heuristic-based analysis
Phase 12: Gemini LLM integration with JSON enforcement

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

import json
import logging
import os
import re
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
        self._llm_model = None  # Lazy-loaded Gemini model
        
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
        
        # Phase 12: Hybrid approach - heuristics first, then LLM if needed
        # 1. Try fast heuristics first
        heuristic_decision = self._analyze_heuristic(file_path, violation_type, context)
        
        # If heuristic confidence is high enough, use it (saves LLM tokens)
        if heuristic_decision.confidence >= 0.8:
            Logger.info(f"[COGNITIVE] High-confidence heuristic: {heuristic_decision.action} ({heuristic_decision.confidence:.2f})")
            return heuristic_decision
        
        # 2. Try LLM if enabled and API key is available
        if self.llm_enabled and self.api_key:
            llm_decision = self._generate_llm_decision(file_path, violation_type, context)
            if llm_decision.action != "MANUAL_REVIEW":
                return llm_decision
        
        # 3. Fall back to heuristic decision
        return heuristic_decision
    
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
    
    def _get_llm_model(self):
        """
        Lazy-load the Gemini model.
        
        Returns:
            GenerativeModel instance or None if not configured
        """
        if self._llm_model is None and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._llm_model = genai.GenerativeModel("gemini-1.5-flash")
                Logger.info("[COGNITIVE] Gemini model initialized")
            except ImportError:
                Logger.warning("[COGNITIVE] google-generativeai not installed")
                return None
            except Exception as e:
                Logger.error(f"[COGNITIVE] Failed to initialize Gemini: {e}")
                return None
        return self._llm_model

    def _generate_llm_decision(
        self,
        file_path: Path,
        violation_type: str,
        context: dict[str, Any],
    ) -> DispositionDecision:
        """
        [PHASE 12] Generate disposition decision using Gemini LLM.
        
        Constructs a strict JSON-enforcing prompt and parses the response.
        
        Args:
            file_path: Path to the file with violation
            violation_type: Type of violation
            context: Additional context
        
        Returns:
            DispositionDecision from LLM analysis
        """
        try:
            model = self._get_llm_model()
            if model is None:
                return DispositionDecision(
                    action="MANUAL_REVIEW",
                    reason="LLM not available (missing API key or library)",
                    confidence=0.0,
                )
            
            # Read file content safely
            content = self._read_file_safe(file_path)
            
            # Build strict JSON-enforcing prompt
            prompt = self._build_strict_json_prompt(file_path, violation_type, content, context)
            
            Logger.info(f"[COGNITIVE] Calling Gemini for {file_path.name}...")
            
            # Call LLM
            response = model.generate_content(prompt)
            
            # Parse JSON response
            return self._parse_llm_json_response(response.text)
            
        except Exception as e:
            Logger.error(f"[COGNITIVE] LLM analysis failed: {e}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"LLM Error: {e}",
                confidence=0.0,
            )

    def _read_file_safe(self, file_path: Path) -> str:
        """
        Safely read file content with size limits.
        
        Args:
            file_path: Path to file
        
        Returns:
            File content (truncated if needed) or empty string
        """
        try:
            if not file_path.exists():
                return ""
            if file_path.stat().st_size > 50000:  # 50KB limit
                return ""
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return content[:3000]  # Truncate to 3000 chars for prompt
        except Exception:
            return ""

    def _build_strict_json_prompt(
        self,
        file_path: Path,
        violation_type: str,
        content: str,
        context: dict[str, Any],
    ) -> str:
        """
        [PHASE 12] Build a strict JSON-enforcing prompt for LLM.
        
        Uses explicit instructions to ensure valid JSON output.
        """
        layer_desc = "\n".join(f"- {k}: {v}" for k, v in self.layer_map.items())
        
        return f"""You are a Senior Software Architect analyzing an architectural violation.

TASK: Determine the correct disposition for this file in a standard Agentic L0-L6 architecture.

FILE INFORMATION:
- Path: {file_path}
- Name: {file_path.name}
- Violation Type: {violation_type}

LAYER STRUCTURE (SSOT):
{layer_desc}

FILE CONTENT (truncated):
```python
{content}
```

INSTRUCTIONS:
1. Analyze the file's purpose based on its name and content
2. Determine which layer it belongs to based on the SSOT
3. Return ONLY a valid JSON object, no other text

VALID ACTIONS:
- "MOVE": File should be moved to target_path
- "ARCHIVE": File should be archived (unclear purpose or duplicate)
- "IGNORE": File is correctly placed or is a false positive

OUTPUT FORMAT (JSON ONLY - NO MARKDOWN, NO EXPLANATION):
{{"action": "MOVE", "target_path": "agentic_core/L5_safety/validators", "reason": "brief explanation", "confidence": 0.85}}

RESPOND WITH ONLY THE JSON OBJECT:"""

    def _parse_llm_json_response(self, response_text: str) -> DispositionDecision:
        """
        [PHASE 12] Parse LLM response with strict JSON extraction.
        
        Handles various response formats including markdown code blocks.
        
        Args:
            response_text: Raw LLM response
        
        Returns:
            DispositionDecision parsed from response
        """
        try:
            # Clean response - remove markdown code blocks
            cleaned = response_text.strip()
            cleaned = re.sub(r"```json\s*", "", cleaned)
            cleaned = re.sub(r"```\s*", "", cleaned)
            cleaned = cleaned.strip()
            
            # Try to find JSON object in response
            json_match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Extract and validate fields
            action = data.get("action", "MANUAL_REVIEW").upper()
            if action not in {"MOVE", "REFACTOR", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"}:
                action = "MANUAL_REVIEW"
            
            target_path = data.get("target_path")
            reason = data.get("reason", "LLM Generated")
            confidence = float(data.get("confidence", 0.5))
            
            Logger.info(f"[COGNITIVE] LLM decision: {action} -> {target_path} ({confidence:.2f})")
            
            return DispositionDecision(
                action=action,
                target_path=target_path,
                reason=reason,
                confidence=confidence,
                metadata={"source": "gemini"},
            )
            
        except json.JSONDecodeError as e:
            Logger.warning(f"[COGNITIVE] Failed to parse LLM JSON: {e}")
            Logger.debug(f"[COGNITIVE] Raw response: {response_text[:500]}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"JSON parse error: {e}",
                confidence=0.0,
            )
        except Exception as e:
            Logger.error(f"[COGNITIVE] Error parsing LLM response: {e}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"Parse error: {e}",
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
