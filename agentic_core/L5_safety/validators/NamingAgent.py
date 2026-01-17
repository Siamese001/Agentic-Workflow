from __future__ import annotations
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
from typing import Any, Dict, List, Optional, Set, Tuple
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
    # App-specific placement rules
    APP_SPECIFIC_PREFIXES,
    is_app_specific_file,
    get_correct_app_folder,
    # Forbidden filename patterns
    FORBIDDEN_LAYER_PREFIXES,
    has_forbidden_layer_prefix,
    is_broken_backup_file,
)
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SEMANTIC_L2_REGISTRY, CORE_SUBFOLDER_MAP, SOVEREIGN_REGISTRY,
    AST_PLACEMENT_SIGNALS, PLACEMENT_CONFIDENCE, L2_TO_L1_MAP
)
# Backward compatible aliases
semantic_l2_registry = SOVEREIGN_REGISTRY
core_subfolder_map = CORE_SUBFOLDER_MAP
sovereign_registry = SOVEREIGN_REGISTRY

# Global agent registry for tracking moved agents
AGENT_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    l1: [] for l1 in sovereign_registry.get('agentic_core', {}).get('subfolders', [])
}

@dataclass
class PlacementResult:
    """PlacementResult agent for autonomous operations."""
    full_path: str
    l1_folder: str
    l2_subfolder: Optional[str]
    confidence: float
    ConfidenceLevel: str
    signals_matched: List[str]
    reasoning: str
    alternative_paths: List[str]

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class NamingAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Autonomous agent for naming law compliance.
    Operates after LocationAgent (assumes file is in valid territory).
    
    ULTRA HARDENING — GLOBAL UNIQUENESS + SEMANTIC AWARENESS — 2025-12-30
    Enforces:
    - Globally unique PascalCase agent names (no duplicates like CanonBaseAgent L1/L2)
    - Semantic territory context for higher signal
    - True LLM-powered intelligent suggestions
    - App-specific prefix must match actual root folder (rg_* → apps_rg, etc.)
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
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

    def validate_prefix_location_match(self, file_path: Path) -> List[str]:
        """
        Validate that files with app-specific prefixes are in the correct root folder.
        Returns list of violation messages (empty = compliant).
        """
        violations = []
        filename = file_path.name

        if not is_app_specific_file(filename):
            return violations

        try:
            rel_path = file_path.relative_to(self.project_root)
            root_folder = rel_path.parts[0]
        except ValueError:
            root_folder = None

        expected_root = get_correct_app_folder(filename)
        if expected_root and root_folder != expected_root:
            violations.append(
                f"PREFIX-LOCATION MISMATCH: '{filename}' has app-specific prefix "
                f"→ expected root '{expected_root}', but found in '{root_folder}'. "
                f"Move to '{expected_root}/engines/'."
            )

        # Additional strict check using PREFIXES dict
        for prefix, expected in APP_SPECIFIC_PREFIXES.items():
            if filename.startswith(prefix) and root_folder != expected:
                violations.append(
                    f"PREFIX VIOLATION: File starts with '{prefix}' → must be under '{expected}/'"
                )
                break  # one message is enough

        return violations

    def validate_forbidden_layer_prefix(self, file_path: Path) -> List[str]:
        """
        Validate that filenames do not begin with layer/priority prefixes.
        Examples of forbidden: l1_cms_schemas.py, P1_core___init__.py
        Layer info belongs in FOLDER structure, not filenames.
        Returns list of violation messages (empty = compliant).
        """
        violations = []
        filename = file_path.name

        forbidden_prefix = has_forbidden_layer_prefix(filename)
        if forbidden_prefix:
            violations.append(
                f"LAYER PREFIX VIOLATION: '{filename}' begins with forbidden prefix '{forbidden_prefix}'. "
                f"Layer/priority info belongs in folder structure, not filenames. "
                f"Rename to remove the '{forbidden_prefix}' prefix."
            )

        return violations

    def validate_broken_backup_file(self, file_path: Path) -> List[str]:
        """
        Validate that file is not a broken backup (.bak.NNNNNN pattern).
        These files break archiving logic and sit unused in repo.
        Returns list of violation messages (empty = compliant).
        """
        violations = []
        filename = file_path.name

        if is_broken_backup_file(filename):
            violations.append(
                f"BROKEN BACKUP FILE: '{filename}' matches forbidden backup pattern (.bak.NNNNNN). "
                f"These files break archiving logic. Delete or properly archive this file."
            )

        return violations

    def _build_agent_stem_cache(self) -> Set[str]:
        """Build set of all agent class names from agent_discovery_full.json (authoritative source)."""
        stems = set()
        json_path = self.project_root / "agent_discovery_full.json"
        
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                for agent in data:
                    class_name = agent.get("class_name", "")
                    if class_name:
                        stems.add(class_name)
                return stems
            except Exception:
                pass
        
        # Fallback to rglob if JSON not found
        for py_file in self.project_root.rglob("*Agent.py"):
            if any(ex in str(py_file) for ex in {"__pycache__", ".git", "archives"}):
                continue
            stem = py_file.stem
            if stem.endswith("Agent"):
                stems.add(stem)
        return stems

    def _get_hierarchy_agent(self) -> Any:
        """Lazy load HierarchyAgent for semantic territory context"""
        if self._hierarchy_agent is None:
            from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
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
        """Execute get_placement_guidance_v2 operation."""
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
                ConfidenceLevel="LOW",
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
        
        ConfidenceLevel = self._determine_confidence_level(confidence)
        
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
            ConfidenceLevel=ConfidenceLevel,
            signals_matched=top_data["signals"],
            reasoning=reasoning,
            alternative_paths=alternatives
        )

    def _determine_confidence_level(self, confidence: float) -> str:
        """Determine confidence level using lookup table pattern."""
        confidence_thresholds = [
            (PLACEMENT_CONFIDENCE["HIGH"], "HIGH"),
            (PLACEMENT_CONFIDENCE["MEDIUM"], "MEDIUM"),
            (PLACEMENT_CONFIDENCE["LOW"], "LOW"),
        ]
        
        for threshold, level in confidence_thresholds:
            if confidence >= threshold:
                return level
        return "REJECT"

    def _extract_decorators(self, content: str) -> List[str]:
        """Extract decorators."""
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
        """Extract base classes."""
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

    # Placement keyword mapping (reduces CC by using lookup table)
    PLACEMENT_KEYWORDS = {
        'agentic_core/L1_cognition/planning': ['planner', 'strategy', 'reasoning', 'mission'],
        'agentic_core/L1_cognition/thought_engine': ['thought', 'node', 'react', 'chain'],
        'agentic_core/L3_orchestration/workflow_engines': ['router', 'orchestrator', 'workflow', 'coordinate'],
        'agentic_core/L3_orchestration/fission_logic': ['fission', 'split', 'parallel'],
        'agentic_core/L4_state/memory': ['pinecone', 'redis', 'vector', 'embedding'],
        'agentic_core/L5_safety/guardrails': ['guardrail', 'safety', 'heal'],
        'agentic_core/L5_safety/validators': ['validator', 'enforce', 'compliance'],
        'agentic_core/prompt_governance/templates': ['prompt', 'template'],
        'agentic_core/schemas/models': ['schema', 'pydantic'],
    }

    def _legacy_placement_fallback(self, content_preview: str) -> str:
        """Legacy placement fallback using keyword lookup."""
        lower_preview = content_preview.lower()
        for path, keywords in self.PLACEMENT_KEYWORDS.items():
            if any(k in lower_preview for k in keywords):
                return path
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
        # Early returns for exempt cases
        exempt_result = self._check_exemptions(file_path)
        if exempt_result:
            return exempt_result
        
        # Get file type and convention
        file_type = self._get_file_type(file_path)
        convention = NAMING_CONVENTIONS.get(file_type)
        if not convention:
            return self._validate_basic_naming(file_path)
        
        # Validate pattern and word count
        pattern_result = self._validate_pattern(file_path, file_type, convention)
        if not pattern_result[0]:
            return pattern_result
        
        word_count_result = self._validate_word_count(file_path, file_type, convention)
        if not word_count_result[0]:
            return word_count_result
        
        # For Python files, do additional validation
        if file_path.suffix.lower() == '.py':
            return self._validate_python_file(file_path, file_type, convention)
        
        return True, f"Valid {file_type} naming: {file_path.name}"

    def _check_exemptions(self, file_path: Path) -> Optional[Tuple[bool, str]]:
        """Check if file is exempt from naming validation."""
        file_name = file_path.name
        suffix = file_path.suffix.lower()
        
        if file_name in NAMING_EXEMPT_FILES:
            return True, f"Exempt infrastructure file: {file_name}"
        
        if any(exempt_dir in file_path.parts for exempt_dir in NAMING_EXEMPT_DIRS):
            return True, f"File in exempt directory"
        
        if suffix not in VALIDATED_FILE_EXTENSIONS:
            return True, f"Extension {suffix} not in validation scope"
        
        return None
    
    def _validate_pattern(self, file_path: Path, file_type: str, convention: Dict) -> Tuple[bool, str]:
        """Validate filename against expected pattern."""
        pattern = convention.get('pattern')
        if pattern and not re.match(pattern, file_path.name):
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_path.name}' does not match pattern. "
                f"Expected: {convention['description']}. "
                f"Examples: {', '.join(convention.get('examples', []))}"
            )
        return True, "Pattern valid"
    
    def _validate_word_count(self, file_path: Path, file_type: str, convention: Dict) -> Tuple[bool, str]:
        """Validate word count in filename."""
        word_count = self._count_words_in_name(file_path.name)
        min_words = convention.get('min_words', 1)
        max_words = convention.get('max_words', 5)
        
        if word_count < min_words:
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_path.name}' has {word_count} word(s), "
                f"minimum is {min_words}. Add more descriptive words."
            )
        if word_count > max_words:
            return False, (
                f"NAMING VIOLATION [{file_type}]: '{file_path.name}' has {word_count} word(s), "
                f"maximum is {max_words}. Simplify the name."
            )
        return True, "Word count valid"

    # Basic naming validation rules (reduces CC)
    BASIC_NAMING_RULES = [
        (lambda s, n: '-' in s, "contains hyphens (use underscores)"),
        (lambda s, n: ' ' in n, "contains spaces"),
    ]

    def _validate_basic_naming(self, file_path: Path) -> Tuple[bool, str]:
        """Basic naming validation using rule table."""
        file_name, stem = file_path.name, file_path.stem
        for check, msg in self.BASIC_NAMING_RULES:
            if check(stem, file_name):
                return False, f"NAMING VIOLATION: '{file_name}' {msg}"
        return True, f"Basic naming compliant: {file_name}"

    def _validate_python_file(self, file_path: Path, file_type: str, convention: Dict) -> Tuple[bool, str]:
        """
        Extended validation for Python files.
        Handles Agent files, scripts, and core modules.
        """
        file_name = file_path.name
        stem = file_path.stem

        # Check if this is an Agent file
        if file_name.endswith('Agent.py'):
            return self._validate_agent_file(file_path, file_name, stem)
        
        # Check for hidden agent classes in non-Agent files
        result = self._check_hidden_agent_classes(file_path, file_name)
        if not result[0]:
            return result
        
        # Enforce snake_case for non-Agent files
        return self._validate_snake_case(file_name, stem, file_path)
    
    def _validate_agent_file(self, file_path: Path, file_name: str, stem: str) -> Tuple[bool, str]:
        """Validate Agent.py files for PascalCase and class matching."""
        # Validate PascalCase format
        if not re.match(r'^[A-Z][a-zA-Z0-9]*Agent$', stem):
            return False, (
                f"AGENT NAMING VIOLATION: '{file_name}' must be PascalCase ending with 'Agent' "
                f"(e.g., 'CodeSSOTEnforcerAgent.py', 'NamingAgent.py')"
            )
        
        # Extract and validate agent classes
        try:
            content = file_path.read_text(encoding="utf-8", errors='ignore')
            classes, _, _ = self._extract_ast_symbols(content)
            agent_classes = [c for c in classes if c.endswith('Agent')]
            
            if not agent_classes:
                return False, (
                    f"AGENT CLASS VIOLATION: '{file_name}' must contain at least one class ending with 'Agent'"
                )
            
            # Validate filename matches primary agent class
            return self._validate_agent_class_match(file_name, agent_classes)
            
        except Exception as e:
            return False, f"AGENT VALIDATION ERROR: Unable to parse '{file_name}': {e}"
    
    def _validate_agent_class_match(self, file_name: str, agent_classes: List[str]) -> Tuple[bool, str]:
        """Validate that filename matches primary agent class."""
        primary_agent = agent_classes[0]  # First agent class is primary
        expected_filename = f"{primary_agent}.py"
        
        if file_name != expected_filename:
            return False, (
                f"AGENT NAMING MISMATCH: File '{file_name}' should be '{expected_filename}' "
                f"to match primary class '{primary_agent}'"
            )
        
        return True, f"Valid PascalCase agent file (class: {primary_agent})"
    
    def _check_hidden_agent_classes(self, file_path: Path, file_name: str) -> Tuple[bool, str]:
        """Check for agent classes hiding in non-Agent.py files."""
        try:
            content = file_path.read_text(encoding="utf-8", errors='ignore')
            classes, _, _ = self._extract_ast_symbols(content)
            
            # Find classes that look like agents
            agent_suffixes = ('Agent', 'Handler', 'Manager', 'Controller', 'Executor', 
                            'Validator', 'Orchestrator', 'Governor', 'Enforcer', 'Sentinel')
            hidden_agents = [c for c in classes if any(c.endswith(s) for s in agent_suffixes)
                           and not any(excl in c for excl in ('Mixin', 'Base', 'Abstract', 'Protocol'))]
            
            if hidden_agents:
                primary = hidden_agents[0]
                suggested_name = f"{primary}.py" if primary.endswith('Agent') else f"{primary}Agent.py"
                return False, (
                    f"AGENT FILE NAMING VIOLATION: '{file_name}' contains agent class(es) {hidden_agents}. "
                    f"Rename file to '{suggested_name}' to comply with *Agent.py naming law."
                )
        except Exception:
            pass  # If we can't parse, continue with other checks
        
        return True, "OK"
    
    def _validate_snake_case(self, file_name: str, stem: str, file_path: Path = None) -> Tuple[bool, str]:
        """Validate snake_case naming for non-Agent files."""
        lower_stem = stem.lower()  # Define at the start for use throughout method
        
        if re.search(r'[A-Z]', stem):  # Any uppercase letter
            return False, (
                f"NAMING VIOLATION: '{file_name}' contains uppercase letters "
                f"(must be snake_case, or rename to *Agent.py for PascalCase)"
            )
        if '-' in stem:
            return False, f"NAMING VIOLATION: '{file_name}' contains hyphens (use underscores)"

        # === ROOT-LEVEL SOVEREIGN MARKER CHECK ===
        if file_path:
            try:
                rel_path = file_path.relative_to(self.project_root)
                is_root_file = len(rel_path.parts) == 1
            except ValueError:
                return False, "File outside project root"
        else:
            is_root_file = False

        if is_root_file:
            if file_name in ROOT_PROTECTED_FILES:
                return True, "Protected sovereign root file (Key 0 exempt)"

            sovereign_markers = {'validator', 'compliance', 'healer', 'enforcer', 'governor', 'auditor', 'canon'}
            if not any(marker in lower_stem for marker in sovereign_markers):
                return False, f"SOVEREIGN VIOLATION: Root file '{file_name}' Missing required marker {sovereign_markers}"
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


    # SUPPLEMENTED FROM NamingLawHealerAgent (now deprecated) — merged 2025-12-30
    def detect_low_signal_patterns(self, file_path: Path) -> List[str]:
        """
        SUPPLEMENTED FROM NamingLawHealerAgent (deprecated 2026-01-02) — merged 2025-12-30
        
        Detect low-signal patterns in file name.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of detected Violation types
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
        SUPPLEMENTED FROM NamingLawHealerAgent (deprecated 2026-01-02) — merged 2025-12-30
        
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
        SUPPLEMENTED FROM NamingLawHealerAgent (deprecated 2026-01-02) — merged 2025-12-30
        
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
        UPGRADED 2026-01-02: Uses actual primary agent class name from AST
        Falls back to high-signal suggestions only if no agent class found.
        Respects global uniqueness via _existing_agent_stems cache.
        Detects multi-agent files and recommends splitting.
        
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
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            classes, _, _ = self._extract_ast_symbols(content)
            
            # Find agent-like classes (prioritize those ending with Agent)
            agent_classes = [
                c for c in classes 
                if c.endswith('Agent') 
                or c.endswith(('Handler', 'Manager', 'Orchestrator', 'Governor', 'Enforcer', 'Sentinel'))
            ]
            agent_classes = [c for c in agent_classes 
                            if not any(excl in c for excl in ('Mixin', 'Base', 'Abstract', 'Protocol'))]
            
            if not agent_classes:
                # Fallback to legacy heuristic only if truly no agent
                result['violations'] = self.detect_low_signal_patterns(file_path)
                if not result['violations']:
                    result['status'] = 'compliant'
                    return result
                result['suggestions'] = self.generate_name_suggestions(file_path)
                result['best_name'] = self.rank_name_suggestions(result['suggestions'], file_path) or file_path.name
            elif len(agent_classes) == 1:
                primary = agent_classes[0]
                # ENFORCE NAMING LAW: Must end with Agent
                if not primary.endswith('Agent'):
                    primary = f"{primary}Agent"
                result['best_name'] = f"{primary}.py"
            else:
                # MULTI-AGENT FILE → recommend split instead of rename
                result['status'] = 'multi_agent_needs_split'
                result['error'] = f"File contains multiple agents: {agent_classes}. Split into individual *Agent.py files."
                result['best_name'] = None
                return result
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"Failed to parse {file_path.name}: {e}"
            return result
        
        if not result['best_name']:
            result['status'] = 'no_suggestion'
            return result
            
        # Ensure .py extension and PascalCase agent format
        new_name = result['best_name']
        if not new_name.endswith('.py'):
            new_name = f'{new_name}.py'
        
        # GLOBAL UNIQUENESS ENFORCEMENT
        target_stem = Path(new_name).stem
        if target_stem in self._existing_agent_stems and target_stem != file_path.stem:
            result['status'] = 'collision'
            result['error'] = f"Target name '{target_stem}' already exists globally. Manual resolution required."
            return result
            
        new_path = file_path.parent / new_name
        result['new_path'] = str(new_path)
        
        # Check for filesystem collision
        if new_path.exists() and new_path != file_path:
            result['status'] = 'collision'
            result['error'] = f'Target {new_name} already exists in directory'
            return result
            
        # Execute rename if not dry_run
        if not dry_run:
            try:
                file_path.rename(new_path)
                result['executed'] = True
                result['status'] = 'renamed'
                
                # Update global cache
                self._existing_agent_stems.discard(file_path.stem)
                self._existing_agent_stems.add(new_path.stem)
                
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

    def propose_split(self, file_path: Path) -> List[Dict]:
        """
        Propose splitting multi-agent file into individual *Agent.py files.
        
        Args:
            file_path: Path to multi-agent file
            
        Returns:
            List of split proposals with class name and target filename
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            classes, _, _ = self._extract_ast_symbols(content)
            
            # Find agent classes
            agent_classes = [
                c for c in classes 
                if c.endswith('Agent') 
                or c.endswith(('Handler', 'Manager', 'Orchestrator', 'Governor', 'Enforcer', 'Sentinel'))
            ]
            agent_classes = [c for c in agent_classes 
                            if not any(excl in c for excl in ('Mixin', 'Base', 'Abstract', 'Protocol'))]
            
            if len(agent_classes) <= 1:
                return []
            
            proposals = []
            for cls in agent_classes:
                # Ensure Agent suffix
                target_name = f"{cls}.py" if cls.endswith('Agent') else f"{cls}Agent.py"
                proposals.append({
                    "class_name": cls,
                    "new_file": target_name,
                    "action": "create_new_file"
                })
            
            proposals.append({
                "old_file": file_path.name,
                "action": "delete_or_convert_to_init"
            })
            
            return proposals
        except Exception:
            return []

    def _detect_runner_script_violations(self) -> List[Path]:
        """
        Detect forbidden external runner scripts — autonomy law violation (Canon Key 51).
        
        Returns:
            List of paths to forbidden runner scripts
        """
        violations = []
        forbidden_dirs = ["scripts/healing", "scripts/tools", "scripts/runners"]
        forbidden_patterns = ["heal", "runner", "launcher", "driver"]
        
        for dir_path in forbidden_dirs:
            dir_obj = self.project_root / dir_path
            if dir_obj.exists():
                for py_file in dir_obj.rglob("*.py"):
                    stem_lower = py_file.stem.lower()
                    if any(pattern in stem_lower for pattern in forbidden_patterns):
                        violations.append(py_file)
        
        return violations

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None,
    ) -> Dict[str, int]:
        """
        Autonomous full-repository naming law healing.
        Replaces external scripts — NamingAgent is now self-orchestrating.
        
        Args:
            dry_run: If True, only propose changes (default for safety)
            execute: Must be explicitly True to perform renames (defense in depth)
            depth: Current recursion depth (for meta-healing)
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in current call path (cycle detection)
        
        Returns:
            Summary dict with counts
        """
        # Initialize call path on first call
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        
        # CYCLE DETECTION
        if agent_name in _call_path:
            print(f"  [!] HEALING CYCLE DETECTED: {agent_name} already in path → stopping")
            return {"renamed": 0, "collisions_blocked": 0, "multi_agent_needs_split": 0, "skipped": 0, "errors": 0, "cycle_detected": True}
        
        # DEPTH LIMIT
        if depth > max_depth:
            print(f"  [!] RECURSION DEPTH LIMIT REACHED ({depth}/{max_depth}) → stopping")
            return {"renamed": 0, "collisions_blocked": 0, "multi_agent_needs_split": 0, "skipped": 0, "errors": 0, "depth_limited": True}
        
        # Add self to path
        _call_path.add(agent_name)
        
        if execute and dry_run:
            raise ValueError("execute and dry_run cannot both be True")
        
        actual_execute = execute and not dry_run
        
        try:
            # CRITICAL FIRST: Invoke parent healing chain (HealerMixin + upper layers)
            parent_result = super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth + 1,
                max_depth=max_depth,
                _call_path=_call_path
            )
            
            # AUTONOMY LAW ENFORCEMENT (Canon Key 51)
            script_violations = self._detect_runner_script_violations()
            if script_violations:
                print(f"\nfrom agentic_core.utils.mixins import SubatomicTestingMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[!] AUTONOMY LAW VIOLATION: Found {len(script_violations)} forbidden runner scripts")
                for script in script_violations:
                    print(f"    → {script.relative_to(self.project_root)} — DELETE THIS FILE")
                    if actual_execute:
                        try:
                            script.unlink()
                            print(f"      [+] DELETED forbidden script")
                        except Exception as e:
                            print(f"      [!] Failed to delete: {e}")
                if actual_execute:
                    print("[+] Autonomy law enforced — external scripts removed")
            
            violations = self.run()  # uses existing full scan
            print(f"[NAMING HEAL @ depth {depth}] Found {len(violations)} violations")
            
            summary = self._initialize_summary()
            
            for file_path, reason in violations:
                # Only process AGENT FILE NAMING VIOLATION (not other naming issues)
                if not self._is_agent_naming_violation(reason):
                    summary['skipped'] += 1
                    continue
                    
                proposal = self.auto_rename_proposal(file_path, dry_run=not actual_execute)
                self._process_healing_status(proposal, file_path, summary)
            
            self._print_healing_summary(summary)
            
            # Merge parent results with agent-specific results
            merged = self._merge_healing_results(parent_result, summary)
            return merged
        finally:
            _call_path.discard(agent_name)
    
    def _merge_healing_results(self, parent: Dict[str, Any], agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge parent healing results with agent-specific results.
        
        Args:
            parent: Parent/HealerMixin healing results
            agent: Agent-specific healing results
            
        Returns:
            Merged results with summed metrics
        """
        merged = {}
        
        # Standard metrics (sum parent + agent)
        for key in ['renamed', 'collisions_blocked', 'multi_agent_needs_split', 'skipped', 'errors', 'healed', 'total']:
            merged[key] = parent.get(key, 0) + agent.get(key, 0)
        
        # Preserve other keys from both dicts
        for key in set(parent.keys()) | set(agent.keys()):
            if key not in merged:
                # For non-numeric keys, preserve from agent (more specific)
                if key in agent:
                    merged[key] = agent[key]
                elif key in parent:
                    merged[key] = parent[key]
        
        return merged
    
    def _initialize_summary(self) -> Dict[str, int]:
        """Initialize healing summary dictionary."""
        return {
            "renamed": 0,
            "collisions_blocked": 0,
            "multi_agent_needs_split": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def _is_agent_naming_violation(self, reason: str) -> bool:
        """Check if reason is an agent file naming violation."""
        return 'AGENT FILE NAMING VIOLATION' in reason
    
    def _process_healing_status(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Dispatch healing status to appropriate handler."""
        status_handlers = {
            'renamed': self._handle_renamed,
            'proposed': self._handle_proposed,
            'collision': self._handle_collision,
            'multi_agent_needs_split': self._handle_multi_agent_split,
            'compliant': self._handle_compliant,
        }
        
        status = proposal.get('status', 'error')
        handler = status_handlers.get(status, self._handle_error)
        handler(proposal, file_path, summary)
    
    def _handle_renamed(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle renamed status."""
        summary['renamed'] += 1
        print(f"  [+] RENAMED: {file_path.name} → {Path(proposal['new_path']).name}")
    
    def _handle_proposed(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle proposed status."""
        summary['renamed'] += 1
        print(f"  [→] WOULD RENAME: {file_path.name} → {Path(proposal['new_path']).name}")
    
    def _handle_collision(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle collision status."""
        summary['collisions_blocked'] += 1
        print(f"  [!] BLOCKED (collision): {file_path.name} → {proposal.get('best_name')} — {proposal.get('error')}")
    
    def _handle_multi_agent_split(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle multi-agent split required status."""
        summary['multi_agent_needs_split'] += 1
        print(f"  [!] SPLIT REQUIRED: {file_path.name} contains multiple agents — manual split needed")
    
    def _handle_compliant(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle compliant status."""
        summary['skipped'] += 1
    
    def _handle_error(self, proposal: Dict[str, Any], file_path: Path, summary: Dict[str, int]) -> None:
        """Handle error status."""
        summary['errors'] += 1
        status = proposal.get('status', 'unknown')
        print(f"  [!] ERROR: {file_path.name} — {proposal.get('error', status)}")
    
    def _print_healing_summary(self, summary: Dict[str, int]) -> None:
        """Print healing summary."""
        print(f"\n[NAMING HEAL SUMMARY] "
              f"Renamed: {summary['renamed']} | "
              f"Collisions: {summary['collisions_blocked']} | "
              f"Split needed: {summary['multi_agent_needs_split']} | "
              f"Skipped: {summary['skipped']} | "
              f"Errors: {summary['errors']}")

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
        """Execute validate_current_placement operation."""
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
        
        if suggested.ConfidenceLevel in ["HIGH", "MEDIUM"]:
            if current_path != suggested.full_path:
                return False, suggested
        
        return True, suggested

    def move_to_canonical_location(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """Execute move_to_canonical_location operation."""
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
            if placement.ConfidenceLevel in ["LOW", "REJECT"]:
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
        naming = get_naming_agent(self.project_root)
        is_valid, reason = naming.validate_proposed_name("MyNewAgent.py")
    """
    global _naming_agent_instance
    if _naming_agent_instance is None and project_root:
        _naming_agent_instance = NamingAgent(project_root)
    return _naming_agent_instance
