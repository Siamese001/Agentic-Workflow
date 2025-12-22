"""
⚛️ Memory Architect - Autonomous Knowledge Distillation

This agent bridges Short-Term Episodic Memory (Redis) and Long-Term Semantic Memory (Pinecone)
by automatically distilling successful healing operations into reusable patterns.

Level 5 Autonomy: No manual prompts required - learns from every successful fix.

Architecture:
    Detection → Reflection → Generalization → Inoculation
    
Integration:
    Monitors Atomic Blackboard for file_health transitions (FAIL → PASS)
    Analyzes before/after AST diffs
    Synthesizes generalized patterns with Gemini Deep Think
    Upserts to Pinecone structural_patterns namespace
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
import re
import time


import ast
import difflib
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from agentic_core.agents.base import SubAtomicAgent

logger = logging.getLogger(__name__)


@dataclass
class HealingSuccess:
    """Represents a successful healing operation."""
    file_path: str
    key_id: int
    before_code: str
    after_code: str
    before_metrics: Dict
    after_metrics: Dict
    timestamp: str
    healing_round: int


@dataclass
class DistilledPattern:
    """Represents a distilled pattern ready for Pinecone."""
    pattern_id: str
    pattern_type: str
    source_file: str
    key_id: int
    trigger_condition: str
    transformation_steps: List[str]
    before_metrics: Dict
    after_metrics: Dict
    improvement_percentage: float
    generalized_rule: str
    code_examples: Dict
    timestamp: str


class HealingDiffAnalyzer:
    """
    Analyzes before/after code to identify structural changes and metrics.
    This class encapsulates the logic for diff analysis, function extraction,
    and nesting calculation, reducing the complexity of MemoryArchitect.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def analyze_diff(self, success: HealingSuccess) -> Optional[Dict]:
        """
        Analyze the before/after AST to identify the specific refactoring mutation.
        
        Args:
            success: Healing success to analyze
            
        Returns:
            Diff analysis dictionary
        """
        try:
            # Parse before and after code
            before_tree = ast.parse(success.before_code)
            after_tree = ast.parse(success.after_code)
            
            # Extract structural changes
            before_functions = self._extract_functions(before_tree)
            after_functions = self._extract_functions(after_tree)
            
            # Identify what changed
            added_functions = set(after_functions.keys()) - set(before_functions.keys())
            removed_functions = set(before_functions.keys()) - set(after_functions.keys())
            modified_functions = set(before_functions.keys()) & set(after_functions.keys())
            
            # Analyze modifications
            modifications = []
            for func_name in modified_functions:
                before_func = before_functions[func_name]
                after_func = after_functions[func_name]
                
                if before_func['lines'] != after_func['lines'] or before_func['nesting'] != after_func['nesting']:
                    modifications.append({
                        'function': func_name,
                        'before': before_func,
                        'after': after_func,
                        'line_reduction': before_func['lines'] - after_func['lines'],
                        'nesting_reduction': before_func['nesting'] - after_func['nesting']
                    })
            
            # Generate text diff for context
            text_diff = list(difflib.unified_diff(
                success.before_code.split('\n'),
                success.after_code.split('\n'),
                lineterm='',
                n=3
            ))
            
            return {
                'added_functions': list(added_functions),
                'removed_functions': list(removed_functions),
                'modified_functions': modifications,
                'text_diff': '\n'.join(text_diff[:50]),  # First 50 lines
                'total_line_reduction': success.before_metrics.get('lines', 0) - success.after_metrics.get('lines', 0),
                'total_nesting_reduction': success.before_metrics.get('nesting', 0) - success.after_metrics.get('nesting', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing diff: {e}")
            return None
    
    def _extract_functions(self, tree: ast.AST) -> Dict:
        """Extract function metadata from AST."""
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate metrics
                lines = (node.end_lineno or node.lineno) - node.lineno + 1
                nesting = self._calculate_nesting(node)
                
                functions[node.name] = {
                    'lines': lines,
                    'nesting': nesting,
                    'is_private': node.name.startswith('_'),
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                }
        
        return functions
    
    def _calculate_nesting(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            child_depth = depth
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth += 1
            max_depth = max(max_depth, self._calculate_nesting(child, child_depth))
        
        return max_depth


class MemoryArchitect(SubAtomicAgent):
    """
    Autonomous Knowledge Distillation Agent
    
    Monitors healing successes and automatically distills them into
    long-term patterns stored in Pinecone Deep Brain.
    
    Four-Stage Process:
    1. Detection: Monitor Atomic Blackboard for FAIL → PASS transitions
    2. Reflection: Analyze before/after AST diffs
    3. Generalization: Synthesize reusable pattern with Gemini Deep Think
    4. Inoculation: Upsert to Pinecone structural_patterns namespace
    """
    
    def __init__(self, ctx):
        """
        Initialize Memory Architect.
        
        Args:
            ctx: ValidationContext with Gemini client and Pinecone access
        """
        super().__init__(ctx)
        # Initialize shared Sub-Atomic Engine components via ValidationContext
        # This refactors the direct import from apps_shared to use dependency injection
        # through the ValidationContext, adhering to the architectural rule.
        if hasattr(self.ctx, '_client') and self.ctx._client:
            try:
                # Assuming ValidationContext provides these methods
                self.engine = self.ctx.get_subatomic_engine(gemini_client=self.ctx._client)
                self.safety = self.ctx.get_safety_guardrail()
                self.fission = self.ctx.get_fission_manager()
            except Exception as e:
                logger.warning(f"Failed to initialize Sub-Atomic Engine components via ctx: {e}")
                self.engine = None
                self.safety = None
                self.fission = None
        else:
            self.engine = None
            self.safety = None
            self.fission = None

        self.namespace = "structural_patterns"
        self.pinecone_available = PINECONE_AVAILABLE
        
        # Initialize Pinecone if available
        if PINECONE_AVAILABLE:
            api_key = self.ctx.get_env("PINECONE_API_KEY")
            if api_key:
                try:
                    self.pc = Pinecone(api_key=api_key)
                    self.index = self.pc.Index("canon-healing-patterns")
                    logger.info("[OK] Memory Architect connected to Pinecone")
                except Exception as e:
                    logger.warning(f"[!]  Could not connect to Pinecone: {e}")
                    self.pinecone_available = False
            else:
                logger.warning("[!]  PINECONE_API_KEY not found")
                self.pinecone_available = False
        
        # Track processed successes to avoid duplicates
        self.processed_hashes = set()
        
        # Initialize the extracted diff analyzer
        self.diff_analyzer = HealingDiffAnalyzer(logger)
    
    async def execute(self):
        """
        Execute Memory Architect autonomous monitoring.
        
        This is called by the orchestrator after each healing cycle.
        """
        logger.info("🧠 Memory Architect: Scanning for healing successes...")
        
        # Get recent healing successes from context
        successes = self._detect_healing_successes()
        
        if not successes:
            logger.info("   No new healing successes to harvest")
            return
        
        logger.info(f"   Found {len(successes)} healing successes to analyze")
        
        # Process each success
        for success in successes:
            try:
                await self._harvest_success(success)
            except Exception as e:
                logger.error(f"[X] Error harvesting success from {success.file_path}: {e}")
    
    def _detect_healing_successes(self) -> List[HealingSuccess]:
        """
        Stage 1: Detection
        
        Monitor Atomic Blackboard for file_health transitions from FAIL to PASS
        on Keys 41 (nesting) and 42 (file size).
        
        Returns:
            List of healing successes
        """
        successes = []
        
        # Check context for recently healed files
        if not hasattr(self.ctx, 'healing_history'):
            return successes
        
        for file_path, history in self.ctx.healing_history.items():
            # Look for Key 41 or 42 transitions
            for key_id in [41, 42]:
                if key_id not in history:
                    continue
                
                # Check if this file went from FAIL to PASS
                if history[key_id].get('status') == 'PASS' and history[key_id].get('previous_status') == 'FAIL':
                    # Create success record
                    success = HealingSuccess(
                        file_path=file_path,
                        key_id=key_id,
                        before_code=history[key_id].get('before_code', ''),
                        after_code=history[key_id].get('after_code', ''),
                        before_metrics=history[key_id].get('before_metrics', {}),
                        after_metrics=history[key_id].get('after_metrics', {}),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        healing_round=history[key_id].get('round', 1)
                    )
                    
                    # Check if already processed
                    success_hash = self._hash_success(success)
                    if success_hash not in self.processed_hashes:
                        successes.append(success)
                        self.processed_hashes.add(success_hash)
        
        return successes
    
    def _hash_success(self, success: HealingSuccess) -> str:
        """Generate unique hash for a healing success."""
        content = f"{success.file_path}:{success.key_id}:{success.after_code}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _harvest_success(self, success: HealingSuccess):
        """
        Harvest a successful healing operation and distill into pattern.
        
        Args:
            success: Healing success to harvest
        """
        logger.info(f"🌾 Harvesting success: {success.file_path} (Key {success.key_id})")
        
        # Stage 2: Reflection - Analyze the diff
        diff_analysis = self.diff_analyzer.analyze_diff(success)
        
        if not diff_analysis:
            logger.warning(f"   Could not analyze diff for {success.file_path}")
            return
        
        # Stage 3: Generalization - Synthesize pattern with Gemini Deep Think
        pattern = await self._synthesize_pattern(success, diff_analysis)
        
        if not pattern:
            logger.warning(f"   Could not synthesize pattern for {success.file_path}")
            return
        
        # Stage 4: Inoculation - Upsert to Pinecone
        await self._inoculate_pattern(pattern)
        
        logger.info(f"[OK] Successfully harvested pattern from {success.file_path}")
    
    async def _synthesize_pattern(self, success: HealingSuccess, diff_analysis: Dict) -> Optional[DistilledPattern]:
        """
        Stage 3: Generalization - Rule Synthesis
        
        Use Gemini Deep Think to convert the fix into a generalized Subatomic Pattern.
        
        Args:
            success: Healing success
            diff_analysis: Diff analysis from reflection stage
            
        Returns:
            Distilled pattern
        """
        # Build prompt for Gemini Deep Think
        prompt = self._build_synthesis_prompt(success, diff_analysis)
        
        try:
            # Use Gemini with maximum thinking budget
            response = await self.ctx.generate_with_thinking(
                prompt=prompt,
                thinking_budget=24576,  # Maximum for deep reasoning
                temperature=0.2  # Low temperature for consistency
            )
            
            # Parse response into structured pattern
            pattern = self._parse_synthesis_response(response, success, diff_analysis)
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error synthesizing pattern: {e}")
            return None
    
    def _build_synthesis_prompt(self, success: HealingSuccess, diff_analysis: Dict) -> str:
        """Build prompt for pattern synthesis."""
        key_name = "Nesting Depth" if success.key_id == 41 else "File Size"
        
        prompt_parts = [
            f"# Subatomic Pattern Synthesis",
            f"",
            f"## Context",
            f"A successful healing operation fixed a {key_name} violation (Key {success.key_id}) in `{success.file_path}`.",
            f"",
            f"## Before Metrics",
            f"- Lines: {success.before_metrics.get('lines', 'N/A')}",
            f"- Nesting: {success.before_metrics.get('nesting', 'N/A')}",
            f"",
            f"## After Metrics",
            f"- Lines: {success.after_metrics.get('lines', 'N/A')}",
            f"- Nesting: {success.after_metrics.get('nesting', 'N/A')}",
            f"",
            f"## Structural Changes",
            f"- Added functions: {', '.join(diff_analysis['added_functions']) if diff_analysis['added_functions'] else 'None'}",
            f"- Modified functions: {len(diff_analysis['modified_functions'])}",
            f"- Line reduction: {diff_analysis['total_line_reduction']}",
            f"- Nesting reduction: {diff_analysis['total_nesting_reduction']}",
            f"",
            f"## Diff Sample",
            f"```",
            diff_analysis['text_diff'][:500],  # First 500 chars
            f"```",
            f"",
            f"## Task",
            f"Analyze this successful refactoring and extract a **generalized Subatomic Pattern** that can be applied to ANY file in the codebase with similar complexity issues.",
            f"",
            f"Your response must include:",
            f"1. **Trigger Condition**: When should this pattern be applied? (e.g., 'method > 40 lines AND nesting > 3')",
            f"2. **Transformation Steps**: What specific refactoring steps were taken? (e.g., 'Extract nested conditionals into _process_* helpers')",
            f"3. **Naming Convention**: How should extracted helpers be named? (e.g., '_process_[action]', '_validate_[aspect]')",
            f"4. **Recognition Pattern**: What code smells indicate this pattern is needed? (e.g., 'if/elif chains with similar structure')",
            f"5. **Generalized Rule**: A one-sentence rule that captures the essence of this transformation.",
            f"",
            f"Format your response as JSON with these exact keys: trigger_condition, transformation_steps (array), naming_convention, recognition_pattern (array), generalized_rule"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _parse_synthesis_response(self, response: str, success: HealingSuccess, diff_analysis: Dict) -> DistilledPattern:
        """Parse Gemini response into structured pattern."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
            else:
                # Fallback: create pattern from diff analysis
                parsed = self._create_fallback_pattern(diff_analysis)
            
            # Calculate improvement percentage
            before_lines = success.before_metrics.get('lines', 1)
            after_lines = success.after_metrics.get('lines', 1)
            improvement = ((before_lines - after_lines) / before_lines * 100) if before_lines > 0 else 0
            
            # Generate pattern ID
            pattern_id = f"pattern_{success.key_id}_{hashlib.sha256(success.file_path.encode()).hexdigest()[:8]}_{datetime.now().strftime('%Y%m%d')}"
            
            return DistilledPattern(
                pattern_id=pattern_id,
                pattern_type="flattening" if success.key_id == 41 else "size_reduction",
                source_file=success.file_path,
                key_id=success.key_id,
                trigger_condition=parsed.get('trigger_condition', 'method > 40 lines OR nesting > 3'),
                transformation_steps=parsed.get('transformation_steps', []),
                before_metrics=success.before_metrics,
                after_metrics=success.after_metrics,
                improvement_percentage=improvement,
                generalized_rule=parsed.get('generalized_rule', 'Extract complex logic into focused helper methods'),
                code_examples={
                    'added_functions': diff_analysis['added_functions'],
                    'modified_functions': [m['function'] for m in diff_analysis['modified_functions']]
                },
                timestamp=success.timestamp
            )
            
        except Exception as e:
            logger.error(f"Error parsing synthesis response: {e}")
            # Return fallback pattern
            return self._create_fallback_pattern_object(success, diff_analysis)
    
    def _create_fallback_pattern(self, diff_analysis: Dict) -> Dict:
        """Create fallback pattern when parsing fails."""
        return {
            'trigger_condition': 'method > 40 lines OR nesting > 3',
            'transformation_steps': [
                'Identify complex nested blocks',
                'Extract into private helper methods',
                'Name helpers with _[action]_[noun] convention',
                'Verify nesting ≤ 3 after extraction'
            ],
            'naming_convention': '_[action]_[noun] (e.g., _process_data, _validate_input)',
            'recognition_pattern': [
                'Nested if/elif chains',
                'Repeated code patterns',
                'Large initialization blocks'
            ],
            'generalized_rule': 'Extract nested logic into focused helper methods to reduce complexity'
        }
    
    def _create_fallback_pattern_object(self, success: HealingSuccess, diff_analysis: Dict) -> DistilledPattern:
        """Create fallback DistilledPattern object."""
        pattern_id = f"pattern_{success.key_id}_{hashlib.sha256(success.file_path.encode()).hexdigest()[:8]}_{datetime.now().strftime('%Y%m%d')}"
        
        before_lines = success.before_metrics.get('lines', 1)
        after_lines = success.after_metrics.get('lines', 1)
        improvement = ((before_lines - after_lines) / before_lines * 100) if before_lines > 0 else 0
        
        return DistilledPattern(
            pattern_id=pattern_id,
            pattern_type="flattening" if success.key_id == 41 else "size_reduction",
            source_file=success.file_path,
            key_id=success.key_id,
            trigger_condition='method > 40 lines OR nesting > 3',
            transformation_steps=[
                'Identify complex nested blocks',
                'Extract into private helper methods',
                'Verify nesting ≤ 3 after extraction'
            ],
            before_metrics=success.before_metrics,
            after_metrics=success.after_metrics,
            improvement_percentage=improvement,
            generalized_rule='Extract nested logic into focused helper methods',
            code_examples={
                'added_functions': diff_analysis['added_functions'],
                'modified_functions': [m['function'] for m in diff_analysis['modified_functions']]
            },
            timestamp=success.timestamp
        )
    
    async def _inoculate_pattern(self, pattern: DistilledPattern):
        """
        Stage 4: Inoculation - Deep Brain Write
        
        Upsert the generalized pattern to Pinecone structural_patterns namespace.
        
        Args:
            pattern: Distilled pattern to store
        """
        logger.info(f"💉 Inoculating pattern: {pattern.pattern_id}")
        
        if not self.pinecone_available:
            logger.warning("   Pinecone not available, storing locally")
            self._store_pattern_locally(pattern)
            return
        
        try:
            # Create searchable text representation
            pattern_text = self._create_pattern_text(pattern)
            
            # Generate embedding (would use OpenAI in production)
            # For now, store with zero vector as placeholder
            embedding = [0.0] * 1536  # OpenAI ada-002 dimension
            
            # Prepare metadata
            metadata = {
                'pattern_type': pattern.pattern_type,
                'source_file': pattern.source_file,
                'key_id': pattern.key_id,
                'trigger_condition': pattern.trigger_condition,
                'generalized_rule': pattern.generalized_rule,
                'improvement_percentage': pattern.improvement_percentage,
                'before_lines': pattern.before_metrics.get('lines', 0),
                'after_lines': pattern.after_metrics.get('lines', 0),
                'before_nesting': pattern.before_metrics.get('nesting', 0),
                'after_nesting': pattern.after_metrics.get('nesting', 0),
                'timestamp': pattern.timestamp,
                'pattern_text': pattern_text[:1000]  # First 1000 chars
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    'id': pattern.pattern_id,
                    'values': embedding,
                    'metadata': metadata
                }],
                namespace=self.namespace
            )
            
            logger.info(f"[OK] Pattern inoculated to Pinecone: {pattern.pattern_id}")
            
        except Exception as e:
            logger.error(f"[X] Error inoculating pattern: {e}")
            # Fallback to local storage
            self._store_pattern_locally(pattern)
    
    def _create_pattern_text(self, pattern: DistilledPattern) -> str:
        """Create searchable text representation of pattern."""
        text_parts = [
            f"# {pattern.pattern_type.replace('_', ' ').title()} Pattern",
            f"",
            f"Source: {pattern.source_file}",
            f"Key: {pattern.key_id}",
            f"",
            f"## Trigger",
            pattern.trigger_condition,
            f"",
            f"## Rule",
            pattern.generalized_rule,
            f"",
            f"## Transformation Steps",
            *[f"{i}. {step}" for i, step in enumerate(pattern.transformation_steps, 1)],
            f"",
            f"## Results",
            f"- Line reduction: {pattern.before_metrics.get('lines', 0)} → {pattern.after_metrics.get('lines', 0)}",
            f"- Nesting reduction: {pattern.before_metrics.get('nesting', 0)} → {pattern.after_metrics.get('nesting', 0)}",
            f"- Improvement: {pattern.improvement_percentage:.1f}%",
            f"",
            f"## Examples",
            f"Added functions: {', '.join(pattern.code_examples.get('added_functions', []))}",
            f"Modified functions: {', '.join(pattern.code_examples.get('modified_functions', []))}"
        ]
        
        return '\n'.join(text_parts)
    
    def _store_pattern_locally(self, pattern: DistilledPattern):
        """Store pattern locally when Pinecone is unavailable."""
        patterns_dir = Path("agentic_core/patterns/harvested")
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        pattern_file = patterns_dir / f"{pattern.pattern_id}.json"
        
        with open(pattern_file, 'w') as f:
            json.dump({
                'pattern_id': pattern.pattern_id,
                'pattern_type': pattern.pattern_type,
                'source_file': pattern.source_file,
                'key_id': pattern.key_id,
                'trigger_condition': pattern.trigger_condition,
                'transformation_steps': pattern.transformation_steps,
                'before_metrics': pattern.before_metrics,
                'after_metrics': pattern.after_metrics,
                'improvement_percentage': pattern.improvement_percentage,
                'generalized_rule': pattern.generalized_rule,
                'code_examples': pattern.code_examples,
                'timestamp': pattern.timestamp
            }, f, indent=2)
        
        logger.info(f"[OK] Pattern stored locally: {pattern_file}")


# Singleton instance for global access
_memory_architect = None

def get_memory_architect(ctx) -> MemoryArchitect:
    """Get or create global Memory Architect instance."""
    global _memory_architect
    if _memory_architect is None:
        _memory_architect = MemoryArchitect(ctx)
    return _memory_architect