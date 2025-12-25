"""
⚛️ Context Curator - Prompt Engineer Agent

Manages and compresses UniversalContext between HOP pipeline stages.
Prunes noise while preserving critical architectural decisions.

Mission: Higher accuracy and lower API costs
Strategy: "Clean Slate" with "High Wisdom" - compressed context injection

Impact: Agents don't get confused by previous stage history
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
import re
import time
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

logger = logging.getLogger(__name__)


@dataclass
class ContextSnapshot:
    """Snapshot of context at a point in time."""
    timestamp: str
    stage: str
    total_size: int
    ephemeral_logs: int
    semantic_facts: int
    compressed_size: int


@dataclass
class HandoffSummary:
    """Compressed summary for stage handoff."""
    previous_stage: str
    next_stage: str
    structural_facts: List[str]
    critical_decisions: List[str]
    lessons_learned: List[str]
    warnings: List[str]
    compressed_context: str


class ContextCurator(SubAtomicAgent):
    """
    The Context Curator - Prompt Engineer Agent
    
    Runs between pipeline stages (post-convergence).
    Identifies ephemeral logs vs semantic architectural decisions.
    Uses Gemini to compress session into structural facts.
    Writes handoff_summary.md for next stage.
    Archives bloated logs and wipes active memory.
    
    Process:
    1. Read current_context.json
    2. Classify: Ephemeral vs Semantic
    3. Compress with Gemini: "What must persist?"
    4. Write handoff_summary.md to .canon_memory/
    5. Archive raw logs to archives/logs/
    6. Wipe active memory for fresh context window
    """
    
    def __init__(self, ctx):
        """
        Initialize Context Curator.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        # The ContextCurator's core functionality (compression, archiving, wiping)
        # does not directly use Sub-Atomic Engine components (engine, safety, fission).
        # These attributes are not used elsewhere in this class, so their initialization
        # and the associated import from 'apps_shared' can be removed to resolve
        # the architectural violation without impacting ContextCurator's operations.
        
        # Directories
        self.memory_dir = Path(".canon_memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.archive_dir = Path("archives/logs")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Context size thresholds
        self.MAX_CONTEXT_SIZE = 50000  # characters
        self.TARGET_COMPRESSED_SIZE = 5000  # characters
    
    async def execute(self):
        """
        Execute context curation.
        
        Runs post-convergence to compress and handoff context.
        """
        logger.info("📚 Context Curator: Compressing context for handoff...")
        
        # Take snapshot
        snapshot = self._take_snapshot()
        
        # Check if compression needed
        if snapshot.total_size < self.MAX_CONTEXT_SIZE:
            logger.info(f"   Context size ({snapshot.total_size}) within limits")
            return
        
        logger.info(f"   Context size ({snapshot.total_size}) exceeds limit, compressing...")
        
        # Classify content
        ephemeral, semantic = self._classify_content()
        
        # Compress with Gemini
        handoff = await self._compress_context(semantic)
        
        # Write handoff summary
        self._write_handoff_summary(handoff)
        
        # Archive raw logs
        self._archive_logs(ephemeral)
        
        # Wipe active memory
        self._wipe_active_memory()
        
        logger.info(f"   [OK] Context compressed: {snapshot.total_size} → {len(handoff.compressed_context)} chars")
    
    def _take_snapshot(self) -> ContextSnapshot:
        """Take snapshot of current context."""
        # Calculate context size
        total_size = 0
        
        if hasattr(self.ctx, 'results'):
            total_size += len(str(self.ctx.results))
        
        if hasattr(self.ctx, 'instructions'):
            total_size += len(str(self.ctx.instructions))
        
        if hasattr(self.ctx, 'signals'):
            total_size += len(str(self.ctx.signals))
        
        return ContextSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            stage="current",
            total_size=total_size,
            ephemeral_logs=0,  # Will be calculated in classify
            semantic_facts=0,
            compressed_size=0
        )
    
    def _classify_content(self) -> tuple[List[str], List[str]]:
        """
        Classify content as ephemeral vs semantic.
        
        Returns:
            Tuple of (ephemeral_logs, semantic_facts)
        """
        ephemeral = []
        semantic = []
        
        # Classify instructions
        if hasattr(self.ctx, 'instructions'):
            for instruction in self.ctx.instructions:
                if self._is_ephemeral(instruction):
                    ephemeral.append(instruction)
                else:
                    semantic.append(instruction)
        
        # Classify signals
        if hasattr(self.ctx, 'signals'):
            for signal in self.ctx.signals:
                if self._is_ephemeral(signal):
                    ephemeral.append(signal)
                else:
                    semantic.append(signal)
        
        return ephemeral, semantic
    
    def _is_ephemeral(self, content: str) -> bool:
        """Determine if content is ephemeral."""
        # Ephemeral indicators
        ephemeral_keywords = [
            "processing",
            "checking",
            "scanning",
            "analyzing",
            "attempt",
            "retry",
            "waiting",
            "loading"
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in ephemeral_keywords)
    
    async def _compress_context(self, semantic_facts: List[str]) -> HandoffSummary:
        """
        Compress context using Gemini.
        
        Args:
            semantic_facts: Semantic architectural decisions
            
        Returns:
            Handoff summary
        """
        # Build compression prompt
        prompt = self._build_compression_prompt(semantic_facts)
        
        # Use Gemini to compress (if available)
        if hasattr(self.ctx, 'generate_with_thinking'):
            try:
                compressed = await self.ctx.generate_with_thinking(
                    prompt=prompt,
                    thinking_budget=8000,
                    temperature=0.1
                )
            except Exception as e:
                logger.warning(f"Could not use Gemini for compression: {e}")
                compressed = self._simple_compression(semantic_facts)
        else:
            compressed = self._simple_compression(semantic_facts)
        
        # Parse compressed output
        return self._parse_compression(compressed, semantic_facts)
    
    def _build_compression_prompt(self, semantic_facts: List[str]) -> str:
        """Build prompt for Gemini compression."""
        return f"""# Context Compression Task

You are compressing a context window for a multi-stage pipeline.

## Current Context ({len(semantic_facts)} items):
{chr(10).join(f"- {fact}" for fact in semantic_facts[:50])}

## Task:
Extract ONLY the structural facts that must persist to the next stage.

Focus on:
1. Architectural decisions (e.g., "Extracted X into Y module")
2. Critical constraints (e.g., "Must maintain 90% preservation")
3. Lessons learned (e.g., "Nesting > 3 causes healing failures")
4. Warnings (e.g., "File X is a healing sink")

Ignore:
- Temporary status updates
- Processing logs
- Retry attempts

Format your response as:
STRUCTURAL_FACTS:
- [fact 1]
- [fact 2]

CRITICAL_DECISIONS:
- [decision 1]

LESSONS_LEARNED:
- [lesson 1]

WARNINGS:
- [warning 1]
"""
    
    def _simple_compression(self, semantic_facts: List[str]) -> str:
        """Simple compression without Gemini."""
        # Group by type
        structural = []
        decisions = []
        lessons = []
        warnings = []
        
        for fact in semantic_facts:
            fact_lower = fact.lower()
            
            if "warning" in fact_lower or "error" in fact_lower:
                warnings.append(fact)
            elif "learned" in fact_lower or "discovered" in fact_lower:
                lessons.append(fact)
            elif "decided" in fact_lower or "chose" in fact_lower:
                decisions.append(fact)
            else:
                structural.append(fact)
        
        # Format
        output = "STRUCTURAL_FACTS:\n"
        output += "\n".join(f"- {f}" for f in structural[:10])
        output += "\n\nCRITICAL_DECISIONS:\n"
        output += "\n".join(f"- {d}" for d in decisions[:5])
        output += "\n\nLESSONS_LEARNED:\n"
        output += "\n".join(f"- {l}" for l in lessons[:5])
        output += "\n\nWARNINGS:\n"
        output += "\n".join(f"- {w}" for w in warnings[:5])
        
        return output
    
    def _parse_compression(self, compressed: str, original_facts: List[str]) -> HandoffSummary:
        """Parse compressed output into HandoffSummary."""
        # Extract sections
        structural_facts = []
        critical_decisions = []
        lessons_learned = []
        warnings = []
        
        current_section = None
        
        for line in compressed.split('\n'):
            line = line.strip()
            
            if line.startswith('STRUCTURAL_FACTS:'):
                current_section = 'structural'
            elif line.startswith('CRITICAL_DECISIONS:'):
                current_section = 'decisions'
            elif line.startswith('LESSONS_LEARNED:'):
                current_section = 'lessons'
            elif line.startswith('WARNINGS:'):
                current_section = 'warnings'
            elif line.startswith('- '):
                item = line[2:]
                
                if current_section == 'structural':
                    structural_facts.append(item)
                elif current_section == 'decisions':
                    critical_decisions.append(item)
                elif current_section == 'lessons':
                    lessons_learned.append(item)
                elif current_section == 'warnings':
                    warnings.append(item)
        
        return HandoffSummary(
            previous_stage="current",
            next_stage="next",
            structural_facts=structural_facts,
            critical_decisions=critical_decisions,
            lessons_learned=lessons_learned,
            warnings=warnings,
            compressed_context=compressed
        )
    
    def _write_handoff_summary(self, handoff: HandoffSummary):
        """Write handoff summary to .canon_memory/."""
        summary_file = self.memory_dir / "handoff_summary.md"
        
        content = f"""# Context Handoff Summary

Generated: {datetime.now(timezone.utc).isoformat()}

## Structural Facts
{chr(10).join(f"- {fact}" for fact in handoff.structural_facts)}

## Critical Decisions
{chr(10).join(f"- {decision}" for decision in handoff.critical_decisions)}

## Lessons Learned
{chr(10).join(f"- {lesson}" for lesson in handoff.lessons_learned)}

## Warnings
{chr(10).join(f"- {warning}" for warning in handoff.warnings)}

---

## Full Compressed Context
{handoff.compressed_context}
"""
        
        with open(summary_file, 'w') as f:
            f.write(content)
        
        logger.info(f"   Handoff summary written to {summary_file}")
    
    def _archive_logs(self, ephemeral_logs: List[str]):
        """Archive ephemeral logs."""
        if not ephemeral_logs:
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"ephemeral_logs_{timestamp}.json"
        
        with open(archive_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "count": len(ephemeral_logs),
                "logs": ephemeral_logs
            }, f, indent=2)
        
        logger.info(f"   Archived {len(ephemeral_logs)} ephemeral logs to {archive_file}")
    
    def _wipe_active_memory(self):
        """Wipe active memory to keep context window fresh."""
        # Clear ephemeral data
        if hasattr(self.ctx, 'instructions'):
            self.ctx.instructions = []
        
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals = set()
        
        logger.info("   Active memory wiped for fresh context window")
    
    def load_handoff_summary(self) -> Optional[HandoffSummary]:
        """Load handoff summary from previous stage."""
        summary_file = self.memory_dir / "handoff_summary.md"
        
        if not summary_file.exists():
            return None
        
        try:
            with open(summary_file, 'r') as f:
                content = f.read()
            
            # Parse markdown (simple implementation)
            # In production, would use proper markdown parser
            logger.info(f"   Loaded handoff summary from {summary_file}")
            
            return HandoffSummary(
                previous_stage="previous",
                next_stage="current",
                structural_facts=[],
                critical_decisions=[],
                lessons_learned=[],
                warnings=[],
                compressed_context=content
            )
        except Exception as e:
            logger.warning(f"Could not load handoff summary: {e}")
            return None


# Singleton instance
_context_curator = None

def get_context_curator(ctx) -> ContextCurator:
    """Get or create global Context Curator instance."""
    global _context_curator
    if _context_curator is None:
        _context_curator = ContextCurator(ctx)
    return _context_curator