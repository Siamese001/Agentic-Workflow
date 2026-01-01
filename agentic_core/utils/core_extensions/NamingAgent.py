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
from dataclasses import dataclass
from typing import Optional
import re
import ast
import json
import os

# Tree-sitter imports (optional, with graceful fallback)
try:
    from tree_sitter import Language, Parser
    from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Language = None
    Parser = None

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CANON_SIGNALS,              # High-signal keywords SSOT
    FORBIDDEN_PATTERNS,         # Compiled regex list of banned names
    ROOT_PROTECTED_FILES,
    ALLOWED_DUPLICATE_FILENAMES,  # Files permitted to exist in multiple directories
    validate_no_duplicate_prefix,  # Safeguard against name sprawl
    # New comprehensive naming conventions
    NAMING_CONVENTIONS,
    VALIDATED_FILE_EXTENSIONS,
    NAMING_EXEMPT_FILES,
    NAMING_EXEMPT_DIRS,
)
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SEMANTIC_L2_REGISTRY, CORE_SUBFOLDER_MAP, SOVEREIGN_REGISTRY,
    AST_PLACEMENT_SIGNALS, PLACEMENT_CONFIDENCE, L2_TO_L1_MAP
)
# Backward compatible aliases
semantic_l2_registry = SEMANTIC_L2_REGISTRY
core_subfolder_map = CORE_SUBFOLDER_MAP
sovereign_registry = SOVEREIGN_REGISTRY

# Global agent registry for tracking moved agents
AGENT_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    l1: [] for l1 in sovereign_registry.get('agentic_core', {}).get('subfolders', [])
}

@dataclass
class PlacementResult:
    full_path: str
    l1_folder: str
    l2_subfolder: Optional[str]
    confidence: float
    confidence_level: str
    signals_matched: List[str]
    reasoning: str
    alternative_paths: List[str]


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
        self.FORBIDDEN_FOLDER_PATTERN = re.compile(r'^\d+_')  # Import from structure_blueprint
        
        # Tree-sitter parsers cache (lazy initialization)
        self.parsers = {}  # language_name -> Parser
        self.languages = {}  # language_name -> Language

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

    def _get_parser(self, language_name: str) -> Optional[Parser]:
        """Get or create tree-sitter parser for language."""
        if not TREE_SITTER_AVAILABLE:
            return None
            
        if language_name not in self.parsers:
            try:
                lang = get_language(language_name)
                parser = Parser()
                parser.set_language(lang)
                self.parsers[language_name] = parser
                self.languages[language_name] = lang
            except Exception as e:
                # Silently fail - will use fallback
                return None
        return self.parsers.get(language_name)

    def _extract_ast_symbols(self, content: str) -> Tuple[List[str], List[str], Set[str]]:
        """Extract classes, functions, and imports from Python content (legacy fallback)."""
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

    def _extract_symbols_tree_sitter(self, content: str, language_name: str = 'python') -> Tuple[List[str], List[str], Set[str]]:
        """Extract symbols using tree-sitter with multi-language support."""
        parser = self._get_parser(language_name)
        if not parser:
            # Fallback to legacy ast for Python
            if language_name == 'python':
                return self._extract_ast_symbols(content)
            return [], [], set()

        try:
            tree = parser.parse(bytes(content, "utf8"))
            root_node = tree.root_node
        except Exception:
            return self._extract_ast_symbols(content) if language_name == 'python' else ([], [], set())

        classes = []
        functions = []
        imports = set()

        # Language-specific queries
        try:
            if language_name == 'python':
                class_query = self.languages[language_name].query("""
                    (class_definition name: (identifier) @class.name)
                """)
                func_query = self.languages[language_name].query("""
                    (function_definition name: (identifier) @function.name)
                """)
                import_query = self.languages[language_name].query("""
                    (import_statement) @import
                    (import_from_statement) @import
                """)
            elif language_name in ['javascript', 'typescript']:
                class_query = self.languages[language_name].query("""
                    (class_declaration name: (identifier) @class.name)
                """)
                func_query = self.languages[language_name].query("""
                    (function_declaration name: (identifier) @function.name)
                    (method_definition name: (property_identifier) @function.name)
                """)
                import_query = self.languages[language_name].query("""
                    (import_statement) @import
                """)
            else:
                return self._extract_ast_symbols(content) if language_name == 'python' else ([], [], set())

            # Execute queries
            for capture in class_query.captures(root_node):
                node_text = capture[0].text.decode('utf8')
                classes.append(node_text)
            
            for capture in func_query.captures(root_node):
                node_text = capture[0].text.decode('utf8')
                functions.append(node_text)
            
            for capture in import_query.captures(root_node):
                node_text = capture[0].text.decode('utf8')
                # Extract module name from import statement
                import_parts = node_text.split()
                if len(import_parts) > 1:
                    imports.add(import_parts[1].split('.')[0])

        except Exception:
            # Query failed, use fallback
            return self._extract_ast_symbols(content) if language_name == 'python' else ([], [], set())

        return classes, functions, imports

    def _extract_symbols(self, content: str, file_path: str = None) -> Tuple[List[str], List[str], Set[str]]:
        """Extract symbols with language detection from file extension."""
        language = 'python'
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.js', '.jsx']:
                language = 'javascript'
            elif ext in ['.ts', '.tsx']:
                language = 'typescript'
        
        # Use tree-sitter if available, otherwise fallback to ast
        if TREE_SITTER_AVAILABLE:
            return self._extract_symbols_tree_sitter(content, language_name=language)
        else:
            return self._extract_ast_symbols(content)

    def get_placement_guidance(self, content_preview: str) -> PlacementResult:
        """
        Enhanced LLM-aware placement guidance with AST analysis.
        Helps suggest correct L-layer placement based on content structure.
        SSOT for Key 40/49 migration hints.
        
        Now delegates to get_placement_guidance_v2 for enhanced AST-based placement.
        """
        return self.get_placement_guidance_v2(content_preview)

    def get_placement_guidance_v2(self, content: str, file_path: Path = None) -> PlacementResult:
        classes, functions, imports = self._extract_ast_symbols(content)
        decorators = self._extract_decorators(content)
        base_classes = self._extract_base_classes(content)
        
        placement_scores: Dict[str, Dict[str, Any]] = {}
        
        for path, signals in AST_PLACEMENT_SIGNALS.items():
            score = 0.0
            matched_signals = []
            
            for cls in classes:
                for pattern in signals.get("class_patterns", []):
                    if re.match(pattern, cls, re.IGNORECASE):
                        score += 3.0 * signals.get("weight", 5) / 10
                        matched_signals.append(f"class:{cls}~{pattern}")
            
            for base in base_classes:
                if base in signals.get("base_classes", []):
                    score += 4.0 * signals.get("weight", 5) / 10
                    matched_signals.append(f"inherits:{base}")
            
            for func in functions:
                for pattern in signals.get("function_patterns", []):
                    if re.match(pattern, func, re.IGNORECASE):
                        score += 2.0 * signals.get("weight", 5) / 10
                        matched_signals.append(f"func:{func}~{pattern}")
            
            for imp in imports:
                if imp in signals.get("import_signals", []):
                    score += 2.5 * signals.get("weight", 5) / 10
                    matched_signals.append(f"import:{imp}")
            
            for dec in decorators:
                if dec in signals.get("decorator_signals", []):
                    score += 3.0 * signals.get("weight", 5) / 10
                    matched_signals.append(f"decorator:{dec}")
            
            content_lower = content.lower()
            keyword_hits = sum(1 for kw in signals.get("keyword_signals", []) if kw in content_lower)
            if keyword_hits > 0:
                score += min(keyword_hits * 0.5, 2.0) * signals.get("weight", 5) / 10
                matched_signals.append(f"keywords:{keyword_hits}")
            
            if score > 0:
                placement_scores[path] = {
                    "score": score,
                    "signals": matched_signals,
                    "weight": signals.get("weight", 5)
                }
        
        sorted_placements = sorted(
            placement_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        if not sorted_placements:
            legacy_path = self._legacy_placement_fallback(content)
            return PlacementResult(
                full_path=legacy_path,
                l1_folder=legacy_path.split("/")[1] if "/" in legacy_path else "",
                l2_subfolder=legacy_path.split("/")[2] if legacy_path.count("/") >= 2 else None,
                confidence=0.2,
                confidence_level="LOW",
                signals_matched=["fallback:keyword_heuristic"],
                reasoning="No strong AST signals found, using keyword fallback",
                alternative_paths=[]
            )
        
        top_path, top_data = sorted_placements[0]
        max_possible_score = 15.0
        raw_confidence = min(top_data["score"] / max_possible_score, 1.0)
        
        signal_types = set(s.split(":")[0] for s in top_data["signals"])
        diversity_bonus = len(signal_types) * 0.05
        confidence = min(raw_confidence + diversity_bonus, 1.0)
        
        if confidence >= PLACEMENT_CONFIDENCE["HIGH"]:
            confidence_level = "HIGH"
        elif confidence >= PLACEMENT_CONFIDENCE["MEDIUM"]:
            confidence_level = "MEDIUM"
        elif confidence >= PLACEMENT_CONFIDENCE["LOW"]:
            confidence_level = "LOW"
        else:
            confidence_level = "REJECT"
        
        path_parts = top_path.split("/")
        l1_folder = path_parts[1] if len(path_parts) > 1 else ""
        l2_subfolder = path_parts[2] if len(path_parts) > 2 else None
        
        alternatives = [p for p, _ in sorted_placements[1:4]]
        
        reasoning = f"Matched {len(top_data['signals'])} signals: {', '.join(top_data['signals'][:5])}"
        if len(top_data['signals']) > 5:
            reasoning += f" (+{len(top_data['signals']) - 5} more)"
        
        return PlacementResult(
            full_path=top_path,
            l1_folder=l1_folder,
            l2_subfolder=l2_subfolder,
            confidence=confidence,
            confidence_level=confidence_level,
            signals_matched=top_data["signals"],
            reasoning=reasoning,
            alternative_paths=alternatives
        )

    def _extract_decorators(self, content: str) -> List[str]:
        try:
            tree = ast.parse(content)
        except Exception:
            return []
        
        decorators = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorators.append(f"@{dec.id}")
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                        decorators.append(f"@{dec.func.id}")
                    elif isinstance(dec, ast.Attribute):
                        decorators.append(f"@{dec.attr}")
        return decorators

    def _extract_base_classes(self, content: str) -> List[str]:
        try:
            tree = ast.parse(content)
        except Exception:
            return []
        
        bases = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
        return bases

    def _legacy_placement_fallback(self, content_preview: str) -> str:
        lower_preview = content_preview.lower()
        
        if any(k in lower_preview for k in ['planner', 'strategy', 'reasoning', 'mission']):
            return 'agentic_core/L1_cognition/planning'
        if any(k in lower_preview for k in ['thought', 'node', 'react', 'chain']):
            return 'agentic_core/L1_cognition/thought_engine'
        if any(k in lower_preview for k in ['router', 'orchestrator', 'workflow', 'coordinate']):
            return 'agentic_core/L3_orchestration/workflow_engines'
        if any(k in lower_preview for k in ['fission', 'split', 'parallel']):
            return 'agentic_core/L3_orchestration/fission_logic'
        if any(k in lower_preview for k in ['pinecone', 'redis', 'vector', 'embedding']):
            return 'agentic_core/L4_state/memory'
        if any(k in lower_preview for k in ['guardrail', 'safety', 'heal']):
            return 'agentic_core/L5_safety/guardrails'
        if any(k in lower_preview for k in ['validator', 'enforce', 'compliance']):
            return 'agentic_core/L5_safety/validators'
        if 'prompt' in lower_preview or 'template' in lower_preview:
            return 'agentic_core/prompt_governance/templates'
        if 'schema' in lower_preview or 'pydantic' in lower_preview:
            return 'agentic_core/schemas/models'
        
        return 'agentic_core/L1_cognition/thought_engine'

    def _count_words_in_name(self, name: str) -> int:
        """
        Count words in a filename (handles PascalCase and snake_case).
        
        Examples:
            'HealerAgent' -> 2 (Healer, Agent)
            'CodeDeduplicationAgent' -> 3 (Code, Deduplication, Agent)
            'sovereign_ingestion' -> 2
            'canon_validator_base' -> 3
        """
        # Remove extension
        stem = Path(name).stem
        
        # Handle PascalCase
        if re.match(r'^[A-Z]', stem):
            # Split on uppercase letters
            words = re.findall(r'[A-Z][a-z0-9]*', stem)
            return len(words) if words else 1
        
        # Handle snake_case
        words = stem.split('_')
        return len([w for w in words if w])  # Filter empty strings

    def _get_file_type(self, file_path: Path) -> str:
        """
        Determine the file type category for naming validation.
        
        Returns one of: 'agent', 'base_class', 'script', 'core_module', 
                       'jinja_template', 'json_config', 'yaml_config', 
                       'markdown_doc', 'text_file', 'unknown'
        """
        file_name = file_path.name
        suffix = file_path.suffix.lower()
        
        # Python files
        if suffix == '.py':
            if file_name.endswith('Agent.py'):
                return 'agent'
            if file_name.endswith('_base.py'):
                return 'base_class'
            # Check if in scripts folder
            if 'scripts' in file_path.parts:
                return 'script'
            return 'core_module'
        
        # Templates
        if suffix in {'.jinja', '.jinja2', '.j2'}:
            return 'jinja_template'
        
        # Config files
        if suffix == '.json':
            return 'json_config'
        if suffix in {'.yaml', '.yml'}:
            return 'yaml_config'
        
        # Documentation
        if suffix == '.md':
            return 'markdown_doc'
        if suffix == '.txt':
            return 'text_file'
        
        return 'unknown'

    def validate_file_naming(self, file_path: Path) -> Tuple[bool, str]:
        """
        Core naming law validation for ALL file types.
        Returns (is_compliant, reason_or_guidance)
        
        Enhanced 2025-12-31:
        - PascalCase enforcement for *Agent.py files (2-4 words)
        - snake_case enforcement for scripts/modules (2-3 words, high-signal)
        - Validates .jinja, .json, .yaml, .yml, .md, .txt files
        - Word count validation (min/max per file type)
        """
        file_name = file_path.name
        suffix = file_path.suffix.lower()
        
        # Skip exempt files
        if file_name in NAMING_EXEMPT_FILES:
            return True, f"Exempt infrastructure file: {file_name}"
        
        # Skip exempt directories
        if any(exempt_dir in file_path.parts for exempt_dir in NAMING_EXEMPT_DIRS):
            return True, f"File in exempt directory"
        
        # Skip files with extensions we don't validate
        if suffix not in VALIDATED_FILE_EXTENSIONS:
            return True, f"Extension {suffix} not in validation scope"
        
        # Determine file type
        file_type = self._get_file_type(file_path)
        
        # Get naming convention for this file type
        convention = NAMING_CONVENTIONS.get(file_type)
        if not convention:
            # Fall back to basic validation for unknown types
            return self._validate_basic_naming(file_path)
        
        # Validate pattern
        pattern = convention.get('pattern')
        if pattern and not re.match(pattern, file_name):
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_name}' does not match pattern. "
                f"Expected: {convention['description']}. "
                f"Examples: {', '.join(convention.get('examples', []))}"
            )
        
        # Validate word count
        word_count = self._count_words_in_name(file_name)
        min_words = convention.get('min_words', 1)
        max_words = convention.get('max_words', 5)
        
        if word_count < min_words:
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_name}' has {word_count} word(s), "
                f"minimum is {min_words}. Add more descriptive words."
            )
        if word_count > max_words:
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_name}' has {word_count} word(s), "
                f"maximum is {max_words}. Simplify the name."
            )
        
        # For Python files, do additional validation
        if suffix == '.py':
            return self._validate_python_file(file_path, file_type, convention)
        
        return True, f"Valid {file_type} naming: {file_name}"

    def _validate_basic_naming(self, file_path: Path) -> Tuple[bool, str]:
        """Basic naming validation for unknown file types."""
        file_name = file_path.name
        stem = file_path.stem
        
        # No hyphens in filenames
        if '-' in stem:
            return False, f"NAMING VIOLATION: '{file_name}' contains hyphens (use underscores)"
        
        # No spaces
        if ' ' in file_name:
            return False, f"NAMING VIOLATION: '{file_name}' contains spaces"
        
        return True, f"Basic naming compliant: {file_name}"

    def _validate_python_file(self, file_path: Path, file_type: str, convention: Dict) -> Tuple[bool, str]:
        """
        Extended validation for Python files.
        Handles Agent files, scripts, and core modules.
        """
        file_name = file_path.name
        stem = file_path.stem
        lower_stem = stem.lower()

        # === PASCALCASE ENFORCEMENT FOR AGENT FILES ===
        if file_name.endswith('Agent.py'):
            # Validate PascalCase format
            if not re.match(r'^[A-Z][a-zA-Z0-9]*Agent$', stem):
                return False, (
                    f"AGENT NAMING VIOLATION: '{file_name}' must be PascalCase ending with 'Agent' "
                    f"(e.g., 'CodeSSOTEnforcerAgent.py', 'NamingAgent.py')"
                )
            
            # Extract agent class from file content
            try:
                content = file_path.read_text(encoding="utf-8", errors='ignore')
                classes, _, _ = self._extract_ast_symbols(content)
                agent_classes = [c for c in classes if c.endswith('Agent')]
                
                if not agent_classes:
                    return False, (
                        f"AGENT CLASS VIOLATION: '{file_name}' must contain at least one class ending with 'Agent'"
                    )
                
                # Primary agent class should match filename
                primary_agent = agent_classes[0]  # First agent class is primary
                expected_filename = f"{primary_agent}.py"
                
                if file_name != expected_filename:
                    return False, (
                        f"AGENT NAMING MISMATCH: File '{file_name}' should be '{expected_filename}' "
                        f"to match primary class '{primary_agent}'"
                    )
                
                # PascalCase agent file is valid - skip further checks
                return True, f"Valid PascalCase agent file (class: {primary_agent})"
                
            except Exception as e:
                return False, f"AGENT VALIDATION ERROR: Unable to parse '{file_name}': {e}"
        
        # === SNAKE_CASE ENFORCEMENT FOR NON-AGENT FILES ===
        if re.search(r'[A-Z]', stem):  # Any uppercase letter
            return False, (
                f"NAMING VIOLATION: '{file_name}' contains uppercase letters "
                f"(must be snake_case, or rename to *Agent.py for PascalCase)"
            )
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

    def run(self, files: List[Path] = None, extensions: Set[str] = None) -> List[Tuple[Path, str]]:
        """
        Full naming compliance scan on provided files.
        Returns list of violations as (file_path, reason).
        
        Args:
            files: List of files to validate. If None, scans all validated extensions.
            extensions: Set of extensions to scan. If None, uses VALIDATED_FILE_EXTENSIONS.
        """
        violations: List[Tuple[Path, str]] = []

        if files is None:
            # Scan all validated file extensions (not just .py)
            target_extensions = extensions or VALIDATED_FILE_EXTENSIONS
            files = []
            for ext in target_extensions:
                files.extend(self.project_root.rglob(f"*{ext}"))

        for file_path in files:
            # Skip exempt directories
            if any(exempt_dir in file_path.parts for exempt_dir in NAMING_EXEMPT_DIRS):
                continue
            
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

    # =========================================================================
    # CENTRALIZED NAMING INTERFACE - For use by other agents
    # =========================================================================
    
    def validate_proposed_name(self, proposed_name: str, is_agent: bool = None) -> Tuple[bool, str]:
        """
        CENTRALIZED: Validate a proposed filename before any agent uses it.
        
        All agents that rename/move files should call this method to ensure
        consistent naming conventions across the codebase.
        
        Args:
            proposed_name: The proposed filename (e.g., "MyAgent.py" or "my_file.py")
            is_agent: If None, auto-detect from name. If True/False, force agent/non-agent rules.
            
        Returns:
            (is_valid, reason_or_error)
        """
        if not proposed_name.endswith('.py'):
            return True, "Non-Python file - naming exempt"
        
        stem = proposed_name.replace('.py', '')
        
        # Auto-detect if this should be an agent file
        if is_agent is None:
            is_agent = proposed_name.endswith('Agent.py')
        
        # === PASCALCASE FOR AGENTS ===
        if is_agent:
            if not proposed_name.endswith('Agent.py'):
                return False, (
                    f"AGENT NAMING: '{proposed_name}' must end with 'Agent.py' for PascalCase agents"
                )
            
            if not re.match(r'^[A-Z][a-zA-Z0-9]*Agent$', stem):
                return False, (
                    f"AGENT NAMING: '{proposed_name}' must be PascalCase "
                    f"(e.g., 'CodeSSOTEnforcerAgent.py', 'NamingAgent.py')"
                )
            
            # Check global uniqueness
            if stem in self._existing_agent_stems:
                return False, (
                    f"AGENT UNIQUENESS: '{stem}' already exists. "
                    f"All PascalCase agents must have globally unique names."
                )
            
            return True, f"Valid PascalCase agent name: {proposed_name}"
        
        # === SNAKE_CASE FOR NON-AGENTS ===
        if re.search(r'[A-Z]', stem):
            return False, (
                f"NAMING: '{proposed_name}' must be snake_case "
                f"(no uppercase letters, or rename to *Agent.py for PascalCase)"
            )
        
        if '-' in stem:
            return False, f"NAMING: '{proposed_name}' must use underscores, not hyphens"
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.match(proposed_name):
                return False, f"NAMING: '{proposed_name}' matches forbidden pattern {pattern.pattern}"
        
        return True, f"Valid snake_case name: {proposed_name}"
    
    def generate_compliant_name(self, original_name: str, target_type: str = "auto") -> str:
        """
        CENTRALIZED: Generate a compliant filename from an original name.
        
        [P1 CONSOLIDATION] Absorbs logic from NamingNormalizationAgent._to_snake_case()
        
        Args:
            original_name: Original filename
            target_type: "agent" for PascalCase, "file" for snake_case, "auto" to detect
            
        Returns:
            Compliant filename
        """
        if not original_name or not isinstance(original_name, str):
            raise ValueError("Invalid original_name provided.")
        
        # Preserve extension
        if '.' in original_name:
            stem = original_name.rsplit('.', 1)[0]
            ext = '.' + original_name.rsplit('.', 1)[1]
        else:
            stem = original_name
            ext = '.py'
        
        # Auto-detect type
        if target_type == "auto":
            target_type = "agent" if stem.endswith('Agent') or original_name.endswith('Agent.py') else "file"
        
        if target_type == "agent":
            # Convert to PascalCase
            # Handle snake_case input (e.g., "my_cool_agent" -> "MyCoolAgent")
            if '_' in stem or '-' in stem:
                parts = re.split(r'[_-]', stem)
                pascal = ''.join(p.capitalize() for p in parts if p)
            else:
                # Handle already PascalCase or lowercase
                pascal = stem[0].upper() + stem[1:] if stem else stem
            
            # Ensure ends with Agent
            if not pascal.endswith('Agent'):
                pascal = f"{pascal}Agent"
            
            return f"{pascal}{ext}"
        else:
            # [ABSORBED FROM NamingNormalizationAgent] Convert to snake_case
            # Step 1: Handle CamelCase/PascalCase -> snake_case
            s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', stem)
            s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
            # Step 2: Replace hyphens and spaces with underscores
            s3 = s2.replace('-', '_').replace(' ', '_')
            # Step 3: Lowercase and collapse multiple underscores
            snake = re.sub(r'_+', '_', s3.lower())
            # Step 4: Strip leading/trailing underscores
            snake = snake.strip('_')
            
            return f"{snake}{ext}"
    
    def normalize_filename(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        [P1 CONSOLIDATION] Absorbed from NamingNormalizationAgent.heal_violation()
        
        Normalize a filename to comply with naming conventions:
        - *Agent.py files: PascalCase
        - All other .py files: snake_case
        
        Args:
            file_path: Path to file to normalize
            dry_run: If True, only propose changes without executing
            
        Returns:
            Dict with normalization results
        """
        result = {
            'file_path': str(file_path),
            'original_name': file_path.name,
            'new_name': None,
            'applied': False,
            'reason': None
        }
        
        # Skip files in ALLOWED_DUPLICATE_FILENAMES
        from agentic_core.config.blueprint_sovereign.structure_blueprint import ALLOWED_DUPLICATE_FILENAMES
        if file_path.name in ALLOWED_DUPLICATE_FILENAMES:
            result['reason'] = 'File in ALLOWED_DUPLICATE_FILENAMES - exempt'
            return result
        
        # Determine target type based on content
        is_agent = self.should_be_agent_file(file_path)
        target_type = "agent" if is_agent else "file"
        
        # Generate compliant name
        compliant_name = self.generate_compliant_name(file_path.name, target_type)
        
        # Check if already compliant
        if compliant_name == file_path.name:
            result['reason'] = 'Already compliant'
            return result
        
        result['new_name'] = compliant_name
        new_path = file_path.parent / compliant_name
        
        # Check for collision
        if new_path.exists() and new_path != file_path:
            result['reason'] = f'Collision: {compliant_name} already exists'
            return result
        
        # Execute rename if not dry_run
        if not dry_run:
            try:
                import shutil
                shutil.move(str(file_path), str(new_path))
                result['applied'] = True
                result['reason'] = f'Renamed: {file_path.name} -> {compliant_name}'
                
                # Update agent stem cache if this is an agent
                if is_agent:
                    self._existing_agent_stems.discard(file_path.stem)
                    self._existing_agent_stems.add(new_path.stem)
                    
            except Exception as e:
                result['reason'] = f'Rename failed: {e}'
        else:
            result['reason'] = f'Would rename: {file_path.name} -> {compliant_name}'
        
        return result
    
    def should_be_agent_file(self, file_path: Path) -> bool:
        """
        CENTRALIZED: Determine if a file should follow agent naming conventions.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be PascalCase *Agent.py
        """
        # Check filename
        if file_path.name.endswith('Agent.py'):
            return True
        
        # Check content for agent class
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            classes, _, _ = self._extract_ast_symbols(content)
            return any(c.endswith('Agent') for c in classes)
        except Exception:
            return False


    def scan_for_duplicate_filenames(self, python_files: List[Path] = None) -> Dict[str, List[Path]]:
        """
        [P3 CONSOLIDATION] Absorbed from FilenameUniquenessGuardianAgent.scan_repository()
        
        Scan for duplicate filenames across the repository.
        
        Args:
            python_files: List of Python file paths to scan. If None, scans project_root.
            
        Returns:
            Dict mapping duplicate filenames to list of paths where they exist
        """
        from collections import defaultdict
        from agentic_core.config.blueprint_sovereign.structure_blueprint import ALLOWED_DUPLICATE_FILENAMES
        
        if python_files is None:
            python_files = list(self.project_root.rglob("*.py"))
        
        basename_to_paths: Dict[str, List[Path]] = defaultdict(list)
        
        for file_path in python_files:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            if not file_path.exists():
                continue
            
            basename = file_path.name
            
            # Skip files allowed to have duplicates (from SSOT)
            if basename in ALLOWED_DUPLICATE_FILENAMES:
                continue
            
            # Skip __pycache__ and hidden directories
            if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                continue
                
            basename_to_paths[basename].append(file_path)
        
        # Filter to only duplicates (>1 occurrence)
        duplicates = {
            basename: paths 
            for basename, paths in basename_to_paths.items() 
            if len(paths) > 1
        }
        
        return duplicates
    
    def resolve_duplicate_filename(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        [P3 CONSOLIDATION] Absorbed from FilenameUniquenessGuardianAgent._suggest_sovereign_name()
        
        Resolve a duplicate filename by suggesting a unique name with placement guidance.
        
        Args:
            file_path: Path to the duplicate file
            dry_run: If True, only propose changes without executing
            
        Returns:
            Dict with resolution details
        """
        result = {
            'file_path': str(file_path),
            'original_name': file_path.name,
            'new_name': None,
            'new_path': None,
            'applied': False,
            'reason': None
        }
        
        try:
            # Get placement guidance based on content
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:2048]
            suggested_dir = self.get_placement_guidance(content)
            
            # Generate unique name with counter suffix
            stem = file_path.stem
            suffix = file_path.suffix
            target_dir = self.project_root / suggested_dir
            
            new_path = target_dir / file_path.name
            counter = 1
            while new_path.exists():
                new_name = f"{stem}_v{counter}{suffix}"
                new_path = target_dir / new_name
                counter += 1
            
            result['new_name'] = new_path.name
            result['new_path'] = str(new_path)
            
            if not dry_run:
                import shutil
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(new_path))
                result['applied'] = True
                result['reason'] = f'Resolved duplicate: {file_path.name} -> {new_path.relative_to(self.project_root)}'
            else:
                result['reason'] = f'Would resolve: {file_path.name} -> {new_path.relative_to(self.project_root)}'
                
        except Exception as e:
            result['reason'] = f'Resolution failed: {e}'
        
        return result


    def validate_current_placement(self, file_path: Path) -> Tuple[bool, PlacementResult]:
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return True, None
        
        suggested = self.get_placement_guidance_v2(content, file_path)
        
        try:
            rel_path = file_path.relative_to(self.project_root)
            current_parts = rel_path.parts
            
            if len(current_parts) < 3:
                return True, suggested
            
            current_l1 = current_parts[1] if len(current_parts) > 1 else ""
            current_l2 = current_parts[2] if len(current_parts) > 2 else ""
            current_path = f"agentic_core/{current_l1}/{current_l2}"
            
        except ValueError:
            return True, suggested
        
        if suggested.confidence_level in ["HIGH", "MEDIUM"]:
            if current_path != suggested.full_path:
                return False, suggested
        
        return True, suggested

    def move_to_canonical_location(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        result = {
            'old_path': str(file_path),
            'new_path': None,
            'moved': False,
            'updated_imports': [],
            'error': None
        }
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            placement = self.get_placement_guidance_v2(content)
            if placement.confidence_level in ["LOW", "REJECT"]:
                result['error'] = f"Low confidence ({placement.confidence:.2f}) - skipping move"
                return result
            
            target_dir = placement.full_path
            
            root, *subs = target_dir.split('/')
            if root in sovereign_registry and subs:
                sub_map = core_subfolder_map.get(subs[0], {})
                if sub_map:
                    target_dir = '/'.join([root, subs[0], next(iter(sub_map))])
            
            new_dir = self.project_root / target_dir
            new_path = new_dir / file_path.name
            result['new_path'] = str(new_path)
            
            if self.FORBIDDEN_FOLDER_PATTERN.match(new_dir.name):
                raise ValueError(f"Invalid target: {new_dir.name}")
            
            if not dry_run:
                import shutil
                new_dir.mkdir(parents=True, exist_ok=True)
                backup_path = self.project_root / '.sovereign_healing_backup' / file_path.name
                shutil.copy(file_path, backup_path)
                shutil.move(file_path, new_path)
                result['moved'] = True
                
                if file_path.name.endswith('Agent.py'):
                    new_content = new_path.read_text()
                    classes, funcs, _ = self._extract_ast_symbols(new_content)
                    fingerprint = hash(''.join(classes + funcs))
                    AGENT_REGISTRY[placement.l1_folder].append({'name': new_path.stem, 'file': str(new_path.relative_to(self.project_root)), 'methods': len(funcs), 'fingerprint': hex(fingerprint)})
                
                old_module = file_path.stem
                new_module = new_path.stem
                result['updated_imports'] = self._update_imports_rglob(old_module, new_module)
                
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def _update_imports_rglob(self, old_module: str, new_module: str) -> List[str]:
        """
        Update imports across the repository after a file move/rename.
        
        Args:
            old_module: Original module name (without .py)
            new_module: New module name (without .py)
            
        Returns:
            List of files that were updated
        """
        updated_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            if any(ex in str(py_file) for ex in {"__pycache__", ".git", "archives"}):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                original = content
                
                # Update import statements
                content = re.sub(
                    rf'from\s+([^.]+)\s+import\s+{old_module}',
                    rf'from \1 import {new_module}',
                    content
                )
                
                content = re.sub(
                    rf'import\s+{old_module}',
                    f'import {new_module}',
                    content
                )
                
                # Write back if changed
                if content != original:
                    py_file.write_text(content, encoding='utf-8')
                    updated_files.append(str(py_file.relative_to(self.project_root)))
                    
            except Exception:
                continue
        
        return updated_files


# Singleton instance for centralized access
_naming_agent_instance = None

def get_naming_agent(project_root: Path = None) -> NamingAgent:
    """
    Get singleton NamingAgent instance for centralized naming validation.
    
    Usage by other agents:
        from agentic_core.utils.core_extensions.NamingAgent import get_naming_agent
        naming = get_naming_agent(self.project_root)
        is_valid, reason = naming.validate_proposed_name("MyNewAgent.py")
    """
    global _naming_agent_instance
    if _naming_agent_instance is None and project_root:
        _naming_agent_instance = NamingAgent(project_root)
    return _naming_agent_instance
