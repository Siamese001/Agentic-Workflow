"""
NamingAgent: Canon Naming Law Enforcer (Key 49 territory)

Enforces:
- snake_case only (no CamelCase, no hyphens)
- High-signal canon keywords in non-root files (from CANON_SIGNALS)
- Forbidden generic/versioned/temporary filenames (FORBIDDEN_PATTERNS)
- Sovereign marker presence in root files (validator, compliance, etc.)
- Provides placement guidance heuristics for healer agents
- Advanced signal detection with confidence scoring
- LLM-aware placement guidance with AST analysis
- Auto-rename proposals for HealerAgent integration

Replaces logic from void_compliance.py:
  - validate_file_naming()
  - get_placement_guidance()
  - HIGH_SIGNAL_KEYWORDS usage

Placed in utils/naming per semantic_l2_registry:
  "Naming law enforcement logic, casing validators, and canon signal checks"
"""
from pathlib import Path
from typing import Tuple, Dict, List, Set, Any
import re
import ast
import json

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CANON_SIGNALS,              # High-signal keywords SSOT
    FORBIDDEN_PATTERNS,         # Compiled regex list of banned names
    ROOT_PROTECTED_FILES,
    ALLOWED_DUPLICATE_FILENAMES,  # Files permitted to exist in multiple directories
    validate_no_duplicate_prefix,  # Safeguard against name sprawl
)


class NamingAgent:
    """
    Autonomous agent for naming law compliance.
    Operates after LocationAgent (assumes file is in valid territory).
    
    ULTRA HARDENING — GLOBAL UNIQUENESS + SEMANTIC AWARENESS — 2025-12-30
    Enforces:
    - Globally unique PascalCase agent names (no duplicates like CanonBaseAgent L1/L2)
    - Semantic territory context for higher signal
    - True LLM-powered intelligent suggestions
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.high_signal_keywords = CANON_SIGNALS
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        
        # Keyword weights: core roles > actions > concepts
        self.keyword_weights = {
            "engine": 5, "manager": 5, "validator": 5, "healer": 5, "orchestrator": 5,
            "handler": 4, "guardian": 4, "strategy": 4, "workflow": 4,
            "reasoning": 3, "memory": 3, "state": 3, "prompt": 3, "agent": 3
        }
        
        # ULTRA: Cache all existing agent filenames for uniqueness enforcement
        self._existing_agent_stems: Set[str] = self._build_agent_stem_cache()
        self._hierarchy_agent = None  # Lazy load for semantic context

    def _build_agent_stem_cache(self) -> Set[str]:
        """Build set of all PascalCase agent filenames (without .py)"""
        stems = set()
        for py_file in self.project_root.rglob("*Agent.py"):
            if any(ex in str(py_file) for ex in {"__pycache__", ".git", "archives"}):
                continue
            stem = py_file.stem
            if stem.endswith("Agent"):
                stems.add(stem)
        return stems

    def _get_hierarchy_agent(self):
        """Lazy load HierarchyAgent for semantic territory context"""
        if self._hierarchy_agent is None:
            from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
            self._hierarchy_agent = HierarchyAgent(self.project_root)
        return self._hierarchy_agent

    def _extract_ast_symbols(self, content: str) -> Tuple[List[str], List[str], Set[str]]:
        """Extract classes, functions, and imports from content."""
        try:
            tree = ast.parse(content)
        except Exception:
            return [], [], set()
        
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return classes, functions, imports

    def get_placement_guidance(self, content_preview: str) -> str:
        """
        Enhanced LLM-aware placement guidance with AST analysis.
        Helps suggest correct L-layer placement based on content structure.
        SSOT for Key 40/49 migration hints.
        """
        # Extract AST symbols for stronger signal
        classes, functions, imports = self._extract_ast_symbols(content_preview)
        lower_preview = content_preview.lower()
        
        # Priority 1: Strong class/function names
        for name in classes + functions:
            lower_name = name.lower()
            if any(k in lower_name for k in ["engine", "orchestrator", "workflow"]):
                return 'agentic_core/L3_orchestration'
            if "strategy" in lower_name or "reason" in lower_name or "planner" in lower_name:
                return 'agentic_core/L1_cognition'
            if "memory" in lower_name or "state" in lower_name or "cache" in lower_name:
                return 'agentic_core/L4_state'
            if "guardian" in lower_name or "validator" in lower_name or "healer" in lower_name:
                return 'agentic_core/L5_safety'
        
        # Priority 2: Import-based detection
        if any(imp in imports for imp in ["pinecone", "redis", "vector"]):
            return 'agentic_core/L4_state'
        if any(imp in imports for imp in ["guardrail", "safety"]):
            return 'agentic_core/L5_safety'
        if "pydantic" in imports or "basemodel" in lower_preview:
            return 'agentic_core/schemas'
        
        # Priority 3: Keyword fallback (existing logic)
        if any(k in lower_preview for k in ['planner', 'strategy', 'reasoning', 'mission', 'intent', 'decompose']):
            return 'agentic_core/L1_cognition'
        if any(k in lower_preview for k in ['thought', 'node', 'execute', 'react', 'chain']):
            return 'agentic_core/L1_cognition/thought_engine'
        if any(k in lower_preview for k in ['router', 'orchestrator', 'fission', 'hop', 'workflow', 'coordinate']):
            return 'agentic_core/L3_orchestration'
        if any(k in lower_preview for k in ['pinecone', 'redis', 'vector', 'embedding', 'storage', 'cache', 'ledger']):
            return 'agentic_core/L4_state'
        if any(k in lower_preview for k in ['guardrail', 'safety', 'redteam', 'gravity', 'validator']):
            return 'agentic_core/L5_safety'
        if 'prompt' in lower_preview or 'template' in lower_preview or 'persona' in lower_preview:
            return 'agentic_core/prompt_governance'
        if 'schema' in lower_preview or 'model' in lower_preview or 'pydantic' in lower_preview:
            return 'agentic_core/schemas'

        # Default fallback
        return 'agentic_core/L1_cognition'

    def validate_file_naming(self, file_path: Path) -> Tuple[bool, str]:
        """
        Core naming law validation.
        Returns (is_compliant, reason_or_guidance)
        """
        file_name = file_path.name

        if not file_name.endswith('.py'):
            return True, "Non-Python file - naming exempt"

        stem = file_path.stem
        lower_stem = stem.lower()

        # === SNAKE_CASE ENFORCEMENT ===
        if re.search(r'[A-Z]', stem):  # Any uppercase letter
            return False, f"NAMING VIOLATION: '{file_name}' contains uppercase letters (must be snake_case)"
        if '-' in stem:
            return False, f"NAMING VIOLATION: '{file_name}' contains hyphens (use underscores)"

        # === ROOT-LEVEL SOVEREIGN MARKER CHECK ===
        try:
            rel_path = file_path.relative_to(self.project_root)
            is_root_file = len(rel_path.parts) == 1
        except ValueError:
            return False, "File outside project root"

        if is_root_file:
            if file_name in ROOT_PROTECTED_FILES:
                return True, "Protected sovereign root file (Key 0 exempt)"

            sovereign_markers = {'validator', 'compliance', 'healer', 'enforcer', 'governor', 'auditor', 'canon'}
            if not any(marker in lower_stem for marker in sovereign_markers):
                return False, f"SOVEREIGN VIOLATION: Root file '{file_name}' missing required marker {sovereign_markers}"
            return True, "Valid sovereign root file"

        # === ULTRA GLOBAL UNIQUENESS ENFORCEMENT ===
        # Skip uniqueness check for files explicitly allowed to have duplicates (SSOT)
        if file_name in ALLOWED_DUPLICATE_FILENAMES:
            pass  # Allowed to exist in multiple directories
        elif file_name.endswith("Agent.py"):
            stem_check = file_path.stem
            if stem_check in self._existing_agent_stems:
                # Check if this is the actual file in cache (not a duplicate)
                all_matching = [
                    p for p in self.project_root.rglob(f"{stem_check}.py")
                    if "__pycache__" not in str(p) and p.stem == stem_check
                ]
                if len(all_matching) > 1:
                    return False, (
                        f"UNIQUE NAME VIOLATION: Agent '{stem_check}' already exists elsewhere. "
                        f"All PascalCase agents must have globally unique names. "
                        f"Found {len(all_matching)} instances: {[str(p.relative_to(self.project_root)) for p in all_matching[:3]]}"
                    )

        # === FORBIDDEN GENERIC/VERSIONED NAMES ===
        for pattern in self.forbidden_patterns:
            if pattern.match(file_name):
                return False, f"NAMING VIOLATION: Forbidden pattern '{file_name}' matched {pattern.pattern}"

        # === ADVANCED HIGH-SIGNAL DETECTION WITH CONFIDENCE SCORING ===
        try:
            content = file_path.read_text(encoding="utf-8", errors='ignore')
            lower_content = content.lower()
        except Exception:
            return False, f"SIGNAL VIOLATION: Unable to read '{file_name}' for signal analysis"
        
        score = 0
        found_keywords = set()

        # Score calculation: stem match (strong) + content frequency + position bonus
        for kw, weight in self.keyword_weights.items():
            if kw in lower_stem:
                score += weight * 3  # Stem match = strong signal
                found_keywords.add(kw)
            
            count = lower_content.count(kw)
            if count > 0:
                score += weight * min(count, 3)  # Cap influence to prevent spam
                found_keywords.add(kw)

        # Position bonus: keyword in first 200 chars (early declaration = stronger signal)
        first_section = lower_content[:200]
        for kw in found_keywords:
            if kw in first_section:
                score += 2

        # Threshold check (tunable: 8 = minimum viable signal)
        if score < 8:
            guidance = self.get_placement_guidance(content[:2000])
            return False, (
                f"SIGNAL VIOLATION [Score {score}/20]: '{file_name}' weak canon signal. "
                f"Found: {', '.join(sorted(found_keywords)) or 'none'}. "
                f"Suggested placement: {guidance}"
            )

        return True, f"Naming compliant with high-signal requirement [Score {score}/20]"

    def run(self, files: List[Path] = None) -> List[Tuple[Path, str]]:
        """
        Full naming compliance scan on provided files.
        Returns list of violations as (file_path, reason).
        """
        violations: List[Tuple[Path, str]] = []

        if files is None:
            # If no files provided, scan project root for Python files
            files = list(self.project_root.rglob("*.py"))

        for file_path in files:
            is_valid, reason = self.validate_file_naming(file_path)
            if not is_valid:
                violations.append((file_path, reason))

        return violations

    def suggest_fixes(self, violations: List[Tuple[Path, str]]) -> Dict[Path, str]:
        """
        Generate intelligent rename proposals with collision avoidance.
        """
        suggestions = {}
        for file_path, reason in violations:
            if any(v in reason for v in ["SIGNAL VIOLATION", "NAMING VIOLATION", "UNIQUE NAME VIOLATION"]):
                try:
                    content = file_path.read_text(encoding="utf-8", errors='ignore')
                    guidance = self.get_placement_guidance(content[:3000])
                    domain = guidance.split("/")[-1]
                    
                    # Generate candidates
                    candidates = self.generate_name_suggestions(file_path)
                    
                    # ULTRA: Avoid collisions with existing agents
                    safe_candidates = []
                    for cand in candidates:
                        stem = Path(cand).stem
                        if stem not in self._existing_agent_stems:
                            safe_candidates.append(cand)
                        elif Path(cand).stem == file_path.stem:
                            safe_candidates.append(cand)  # Allow same name for current file
                    
                    if not safe_candidates:
                        # Fallback with domain suffix
                        base = candidates[0].replace('.py', '')
                        safe_name = f"{base}_{domain}.py"
                        safe_candidates = [safe_name]
                    
                    best = self.rank_name_suggestions(safe_candidates, file_path)
                    
                    suggestions[file_path] = f"Rename to {best} (collision-safe) and move to {guidance}"
                    
                except Exception as e:
                    # Fallback suggestion
                    if "Suggested placement:" in reason:
                        suggested_path = reason.split("Suggested placement:")[-1].strip()
                        suggestions[file_path] = f"Move to {suggested_path} (add signal keyword to filename)"
        
        return suggestions


    # SUPPLEMENTED FROM NamingLawHealerAgent — enhances AI-driven rename suggestion engine — merged 2025-12-30
    def detect_low_signal_patterns(self, file_path: Path) -> List[str]:
        """
        SUPPLEMENTED FROM NamingLawHealerAgent._detect_low_signal — merged 2025-12-30
        
        Detect low-signal patterns in file name.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of detected violation types
        """
        violations = []
        current_name = file_path.name
        stem = file_path.stem.lower()
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.match(current_name):
                violations.append('forbidden_pattern')
                break
                
        # Check for low signal
        if not any(sig in stem for sig in self.high_signal_keywords):
            violations.append('low_signal_name')
            
        # Check for uppercase (non-snake_case)
        if re.search(r'[A-Z]', file_path.stem):
            violations.append('non_snake_case')
            
        # Check for hyphens
        if '-' in file_path.stem:
            violations.append('contains_hyphen')
            
        return violations

    def generate_name_suggestions(self, file_path: Path) -> List[str]:
        """
        SUPPLEMENTED FROM NamingLawHealerAgent._generate_suggestions — merged 2025-12-30
        
        Generate high-signal name suggestions based on code content.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of suggested names
        """
        suggestions = []
        stem = file_path.stem.lower()
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return [f'{stem}_agent.py']
            
        # Extract class names for suggestions
        classes, functions, _ = self._extract_ast_symbols(content)
        
        for cls in classes:
            # Convert PascalCase to snake_case
            snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls).lower()
            suggestions.append(snake_name)
            
        # Add role-based suffixes if not present
        if not stem.endswith('_agent'):
            suggestions.append(f'{stem}_agent')
        if not stem.endswith('_engine'):
            suggestions.append(f'{stem}_engine')
        if not stem.endswith('_handler'):
            suggestions.append(f'{stem}_handler')
            
        # Use keyword detection for stronger suggestions
        lower_content = content.lower()
        for kw in self.keyword_weights.keys():
            if kw in lower_content and kw not in stem:
                suggestions.append(f'{kw}_{stem.split("_")[0]}')
                
        return list(set(suggestions))

    def rank_name_suggestions(self, suggestions: List[str], file_path: Path) -> str:
        """
        SUPPLEMENTED FROM NamingLawHealerAgent._rank_suggestions — merged 2025-12-30
        
        Rank suggestions by signal strength and return the best one.
        
        Args:
            suggestions: List of name suggestions
            file_path: Path to original file (for content analysis)
            
        Returns:
            Best suggested name or None
        """
        if not suggestions:
            return None
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
        except Exception:
            content = ''
            
        scores = {}
        for sug in suggestions:
            score = 0
            lower_sug = sug.lower()
            
            # Score based on canon signal presence
            for kw, weight in self.keyword_weights.items():
                if kw in lower_sug:
                    score += weight * 2
                    
            # Bonus for matching content keywords
            for kw in self.keyword_weights.keys():
                if kw in lower_sug and kw in content:
                    score += 3
                    
            # Penalize long names
            score -= len(sug) / 20
            
            # Prefer names ending with role suffixes
            if any(lower_sug.endswith(f'_{role}') for role in ['agent', 'engine', 'handler', 'validator']):
                score += 2
                
            scores[sug] = score
            
        return max(scores, key=scores.get) if scores else None

    def auto_rename_proposal(self, file_path: Path, dry_run: bool = True) -> Dict:
        """
        SUPPLEMENTED FROM NamingLawHealerAgent — merged 2025-12-30
        
        Generate automatic rename proposal with full context.
        
        Args:
            file_path: Path to file to rename
            dry_run: If True, only propose without executing
            
        Returns:
            Dict with proposal details and execution status
        """
        result = {
            'file_path': str(file_path),
            'violations': [],
            'suggestions': [],
            'best_name': None,
            'new_path': None,
            'executed': False,
            'import_updates_needed': [],
        }
        
        # Detect violations
        result['violations'] = self.detect_low_signal_patterns(file_path)
        
        if not result['violations']:
            result['status'] = 'compliant'
            return result
            
        # Generate and rank suggestions
        result['suggestions'] = self.generate_name_suggestions(file_path)
        result['best_name'] = self.rank_name_suggestions(result['suggestions'], file_path)
        
        if not result['best_name']:
            result['status'] = 'no_suggestion'
            return result
            
        # Ensure .py extension
        new_name = result['best_name']
        if not new_name.endswith('.py'):
            new_name = f'{new_name}.py'
            
        new_path = file_path.parent / new_name
        result['new_path'] = str(new_path)
        
        # [SAFEGUARD] Check for duplicate prefix sprawl
        has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
        if has_dup:
            result['status'] = 'blocked'
            result['error'] = f'Name sprawl prevented: {dup_msg}'
            return result
        
        # Check for collision
        if new_path.exists():
            result['status'] = 'collision'
            result['error'] = f'Target {new_name} already exists'
            return result
            
        # Execute rename if not dry_run
        if not dry_run:
            try:
                file_path.rename(new_path)
                result['executed'] = True
                result['status'] = 'renamed'
                
                # Note: import updates would need to be handled separately
                result['import_updates_needed'].append({
                    'old_import': file_path.stem,
                    'new_import': new_path.stem,
                })
            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
        else:
            result['status'] = 'proposed'
            
        return result

    async def _assess_naming_signal(self, name: str, file_path: Path) -> float:
        """Assess naming signal strength (0.0-1.0)."""
        score = 0.0
        stem = name.replace('.py', '').lower()
        
        # Check for canon signals
        for kw, weight in self.keyword_weights.items():
            if kw in stem:
                score += weight * 0.1
                
        # Check for proper suffixes
        if any(stem.endswith(f'_{role}') for role in ['agent', 'engine', 'handler', 'validator', 'manager']):
            score += 0.2
            
        return min(score, 1.0)


# PascalCase is now the canonical name
