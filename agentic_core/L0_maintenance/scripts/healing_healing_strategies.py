from __future__ import annotations
"""
Sovereign Healing Engine: Strategy Registry
Proactive repair strategies for L0 governance violations.

Phase 10: Sovereign Self-Correction (Dec 26, 2025)
"""
from typing import List, Dict, Any
from pathlib import Path
import logging

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


Logger = logging.getLogger(__name__)

# NAMING FIXED: HealingStrategy → HealingStrategy
class HealingStrategy:
    """Base class for all healing strategies."""
    
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority  # Lower = higher priority
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """
        Analyze issues and return actionable fixes.
        
        Args:
            issues: List of issue dictionaries from audit report
            
        Returns:
            List of fix dictionaries with action, target, reason, priority
        """
        return []
    
    async def apply(self, fix: Dict, ctx: Any) -> bool:
        """
        Apply a specific fix and return success status.
        
        Args:
            fix: Fix dictionary with action details
            ctx: Execution context
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        return False


# NAMING FIXED: StructureHealing → StructureHealing
class StructureHealing(HealingStrategy):
    """Heals structural violations (forbidden root folders, directory depth)."""
    
    def __init__(self):
        super().__init__("Structure", priority=1)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            description = issue.get("description", "").lower()
            if "forbidden root" in description or "root folder" in description:
                source = Path(issue.get("file", ""))
                # Determine target directory based on file type
                if "legacy" in str(source) or "archive" in str(source):
                    target_dir = "agentic_core/L0_maintenance/scripts"
                elif "test" in str(source):
                    target_dir = "tests"
                else:
                    target_dir = "agentic_core/L0_maintenance/scripts"
                
                fixes.append({
                    "action": "move",
                    "source": str(source),
                    "target": str(Path(target_dir) / source.name),
                    "reason": "Forbidden root folder Violation",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Physically relocate files to compliant territories."""
        try:
            import shutil
            source = Path(fix["source"])
            target = Path(fix["target"])
            
            if not source.exists():
                return False
                
            # Ensure target parent exists
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Execute physical move
            shutil.move(str(source), str(target))
            Logger.info(f"[L0 STRUCTURE] Relocated {source.name} to {target.parent}")
            return True
        except Exception as e:
            Logger.error(f"[L0 STRUCTURE] Move failed: {e}")
            return False


# NAMING FIXED: UnderscoreFieldHealing → UnderscoreFieldHealing
class UnderscoreFieldHealing(HealingStrategy):
    """Heals underscore-prefixed fields in SSOT models."""
    
    def __init__(self):
        super().__init__("UnderscoreFields", priority=2)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            description = issue.get("description", "").lower()
            # If the auditor parsed the field specifically
            field_name = issue.get("field")
            
            # If not, try to extract from description
            if not field_name and "field '" in description:
                try:
                    field_name = description.split("field '")[1].split("'")[0]
                except (IndexError, ValueError):
                    pass
                    
            if field_name and field_name.startswith("_") and not field_name.startswith("__"):
                fixes.append({
                    "action": "rename_field",
                    "file": issue.get("file"),
                    "old_name": field_name,
                    "new_name": field_name.lstrip("_"),
                    "reason": "Underscore field in SSOT model",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Rename illegal underscore fields in SSOT schema files."""
        try:
            import re
            file_path = Path(fix["file"])
            if not file_path.exists():
                return False
                
            old_name = fix["old_name"]
            new_name = fix["new_name"]
            
            content = file_path.read_text(encoding="utf-8")
            # Use word boundaries to prevent partial matches
            new_content = re.sub(rf"\b{old_name}\b", new_name, content)
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                Logger.info(f"[L0 SSOT HEALING] Renamed {old_name} -> {new_name} in {file_path}")
                return True
            return False
        except Exception as e:
            Logger.error(f"[L0 SSOT HEALING] Failed: {e}")
            return False


# NAMING FIXED: DarkReasoningHealing → DarkReasoningHealing
class DarkReasoningHealing(HealingStrategy):
    """Heals Dark Reasoning violations by injecting L6 logging."""
    
    def __init__(self):
        super().__init__("DarkReasoning", priority=3)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            desc = issue.get("description", "").lower()
            if "dark reasoning" in desc or "l6 footprint" in desc:
                fixes.append({
                    "action": "inject_logging",
                    "file": issue.get("file", ""),
                    "line": issue.get("line"),
                    "reason": "Dark Reasoning - Missing L6 observability footprint",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Inject structured logging around dark reasoning calls."""
        try:
            file_path = Path(fix["file"])
            line_num = fix.get("line")
            if not file_path.exists() or line_num is None:
                return False

            lines = file_path.read_text(encoding="utf-8").splitlines()
            if line_num > len(lines): return False

            target_line = lines[line_num - 1]
            indent = len(target_line) - len(target_line.lstrip())
            log_stmt = " " * indent + f'Logger.info("[L1 REASONING] Observed: {target_line.strip()}")'
            
            lines.insert(line_num, log_stmt)
            file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            Logger.info(f"[L0 DARK REASONING] Injected log at {file_path}:{line_num}")
            return True
        except Exception as e:
            Logger.error(f"[L0 DARK REASONING] Failed: {e}")
            return False


# NAMING FIXED: DDDAlignmentHealing → DddAlignmentHealing
class DddAlignmentHealing(HealingStrategy):
    """Heals DDD alignment violations by refactoring imports."""
    
    def __init__(self):
        super().__init__("DDDAlignment", priority=4)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose DDD violations and propose import refactoring."""
        fixes = []
        
        for issue in issues:
            description = issue.get("description", "").lower()
            
            if "context Violation" in description or "importing" in description:
                # Extract module being imported
                if "importing" in description:
                    parts = description.split("importing")
                    if len(parts) > 1:
                        module_info = parts[1].strip()
                        
                        fixes.append({
                            "action": "refactor_import",
                            "file": issue.get("file", ""),
                            "module": module_info,
                            "reason": "DDD Context Violation - illegal cross-layer import",
                            "priority": self.priority,
                            "strategy": self.name
                        })
        
        return fixes
    
    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Apply DDD import refactoring by commenting out illegal imports."""
        try:
            file_path = Path(fix.get("file", ""))
            if not file_path.exists():
                Logger.warning(f"[L0 DDD HEALING] File not found: {file_path}")
                return False
            
            module_info = fix.get("module", "")
            if not module_info:
                Logger.warning(f"[L0 DDD HEALING] No module info in fix")
                return False
            
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
            
            # Find and comment out the illegal import
            modified = False
            for i, line in enumerate(lines):
                if "import" in line and any(part in line for part in module_info.split()):
                    # Check if already commented
                    if line.strip().startswith("#"):
                        Logger.info(f"[L0 DDD HEALING] Import already commented at line {i+1}")
                        return True
                    
                    # Comment out the import with explanation
                    indent = len(line) - len(line.lstrip())
                    lines[i] = " " * indent + f"# DDD VIOLATION: {line.lstrip()}"
                    modified = True
                    Logger.info(f"[L0 DDD HEALING] Commented illegal import at {file_path}:{i+1}")
                    break
            
            if modified:
                # Write back to file
                file_path.write_text("".join(lines), encoding="utf-8")
                return True
            else:
                Logger.warning(f"[L0 DDD HEALING] Could not find import to fix in {file_path}")
                return False
            
        except Exception as e:
            Logger.error(f"[L0 DDD HEALING] Failed to refactor import: {e}")
            return False


# NAMING FIXED: ObservabilityHealing → ObservabilityHealing
class ObservabilityHealing(HealingStrategy):
    """Heals observability footprint violations by injecting L6 logging."""
    
    def __init__(self):
        super().__init__("Observability", priority=3)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose observability violations and propose logging injections."""
        fixes = []
        
        for issue in issues:
            dimension = issue.get("dimension", "")
            description = issue.get("description", "").lower()
            
            # Check if this is an observability footprint issue
            if "observability footprint" in dimension.lower() or "dark reasoning" in description or "observability" in description:
                # Extract function and line information if available
                function_name = issue.get("function", "anonymous")
                line_num = issue.get("line")
                
                # Try to parse from description if not directly available
                if not function_name or function_name == "anonymous":
                    if "function" in description:
                        try:
                            parts = description.split("function")
                            if len(parts) > 1:
                                function_name = parts[1].strip().split()[0]
                        except (ValueError, IndexError):
                            pass
                
                if not line_num and "line" in description:
                    try:
                        parts = description.split("line")
                        if len(parts) > 1:
                            line_num = int(parts[1].strip().split(":")[0].strip())
                    except (ValueError, IndexError):
                        pass
                
                fixes.append({
                    "action": "inject_logging",
                    "file": issue.get("file", ""),
                    "line": line_num,
                    "function": function_name,
                    "insert_start": f'        Logger.info("[REASONING START] Entering {function_name}")',
                    "insert_end": f'        Logger.info("[REASONING END] Exiting {function_name}")',
                    "reason": "Missing L6 observability footprint — bracketed logging required",
                    "strategy": self.name,
                    "priority": self.priority
                })
        
        return fixes
    
    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Apply observability logging injection."""
        try:
            file_path = Path(fix.get("file", ""))
            if not file_path.exists():
                Logger.warning(f"[L0 OBSERVABILITY HEALING] File not found: {file_path}")
                return False
            
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
            
            line_num = fix.get("line")
            if not line_num or line_num < 1 or line_num > len(lines):
                Logger.warning(f"[L0 OBSERVABILITY HEALING] Invalid line number: {line_num}")
                return False
            
            # Check if logging already exists at this line
            target_line = lines[line_num - 1]
            if "Logger.info" in target_line or "REASONING" in target_line:
                Logger.info(f"[L0 OBSERVABILITY HEALING] Logging already exists at line {line_num}")
                return True  # Already fixed
            
            # Insert logging statement before the target line
            indent = len(target_line) - len(target_line.lstrip())
            log_statement = " " * indent + f'Logger.info("[L6_AUDIT] Action at line {line_num}")\n'
            lines.insert(line_num - 1, log_statement)
            
            # Write back to file
            file_path.write_text("".join(lines), encoding="utf-8")
            Logger.info(f"[L0 OBSERVABILITY HEALING] Injected logging at {file_path}:{line_num}")
            return True
            
        except Exception as e:
            Logger.error(f"[L0 OBSERVABILITY HEALING] Failed to inject logging: {e}")
            return False


# NAMING FIXED: DirectRedisHealing → DirectRedisHealing
class DirectRedisHealing(HealingStrategy):
    """Fixes direct redis-py usage — replaces with SovereignRedisMCPClient"""
    
    def __init__(self):
        super().__init__("DirectRedis", priority=1)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            desc = issue.get("description", "").lower()
            # Handle both formats from auditor
            if "redis" in desc:
                fixes.append({
                    "action": "replace_redis",
                    "file": issue["file"],
                    "reason": "Direct redis-py usage — sovereignty breach",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
                    
        try:
            import re
            file_path = Path(fix["file"])
            if not file_path.exists(): return False
            
            content = file_path.read_text(encoding="utf-8")
            
            # 1. Replace Imports
            new_import = "from agentic_core.L4_state.caching.redis_mcp_client import get_redis_client"
            content = re.sub(r"^\s*import\s+redis.*$", new_import, content, flags=re.MULTILINE)
            content = re.sub(r"^\s*from\s+redis\s+import.*$", new_import, content, flags=re.MULTILINE)
            
            # 2. Replace Usage (redis.Redis(...) -> get_redis_client())
            content = re.sub(r"redis\.Redis\([^)]*\)", "get_redis_client()", content)
            
            file_path.write_text(content, encoding="utf-8")
            Logger.info(f"[L0 REDIS HEALING] Replaced direct redis usage in {file_path}")
            return True
        except Exception as e:
            Logger.error(f"[L0 REDIS HEALING] Failed: {e}")
            return False


# NAMING FIXED: DirectLLMHealing → DirectLlmHealing
class DirectLlmHealing(HealingStrategy):
    """Fixes direct OpenAI/Anthropic calls — routes through LLM Router MCP"""
    
    def __init__(self):
        super().__init__("DirectLLM", priority=1)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            desc = issue.get("description", "").lower()
            if any(sdk in desc for sdk in ["openai", "anthropic"]):
                sdk_name = "OpenAI" if "openai" in desc else "Anthropic"
                fixes.append({
                    "action": "replace_llm_sdk",
                    "file": issue["file"],
                    "sdk": sdk_name,
                    "new_client": "get_llm_router_client()",
                    "import_path": "from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client",
                    "reason": "Direct LLM SDK call — bypasses L5 shield",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Replace direct OpenAI/Anthropic calls with sovereign LLM router."""
        try:
            import re
            file_path = Path(fix["file"])
            if not file_path.exists(): return False

            content = file_path.read_text(encoding="utf-8")
            
            # 1. Replace Imports
            old_import = r"^(import (openai|anthropic)|from (openai|anthropic) import.*)$"
            content = re.sub(old_import, fix["import_path"], content, flags=re.MULTILINE)

            # 2. Replace SDK usage (e.g. openai.ChatCompletion -> get_llm_router_client())
            sdk = fix["sdk"].lower()
            content = re.sub(rf"{sdk}\.[a-zA-Z_]+\(", f"{fix['new_client']}.(", content)

            file_path.write_text(content, encoding="utf-8")
            Logger.info(f"[L0 LLM HEALING] Routed {fix['sdk']} through L5 MCP in {file_path}")
            return True
        except Exception as e:
            Logger.error(f"[L0 LLM HEALING] Failed: {e}")
            return False


# NAMING FIXED: FilesystemBypassHealing → FilesystemBypassHealing
class FilesystemBypassHealing(HealingStrategy):
    """Fixes direct file I/O — routes through Filesystem MCP"""
    
    def __init__(self):
        super().__init__("FilesystemBypass", priority=2)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
                    
        fixes = []
        for issue in issues:
            desc = issue.get("description", "")
            message = issue.get("message", "")
            if any(pattern in desc or pattern in message for pattern in ["Path(", "open(", "os.", "shutil."]):
                fixes.append({
                    "action": "replace_io",
                    "file": issue["file"],
                    "operation": desc,
                    "new_client": "get_filesystem_client()",
                    "import_path": "from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client",
                    "reason": "Direct file I/O — bypasses L5 validation",
                    "priority": self.priority,
                    "strategy": self.name
                })
        return fixes

    async def apply(self, fix: Dict, ctx: Any = None) -> bool:
        """Flag direct filesystem operations for MCP routing."""
        try:
            import re
            file_path = Path(fix["file"])
            if not file_path.exists(): return False

            content = file_path.read_text(encoding="utf-8")
            
            # Comment out direct file operations with sovereignty warnings
            content = re.sub(
                r"(\s*)(open\()",
                r"\1# SOVEREIGNTY: Use filesystem MCP - \2",
                content
            )
            content = re.sub(
                r"(\s*)(Path\([^)]+\)\.(read_text|write_text|read_bytes|write_bytes)\()",
                r"\1# SOVEREIGNTY: Use filesystem MCP - \2",
                content
            )
            content = re.sub(
                r"(\s*)(shutil\.(copy|move|rmtree)\()",
                r"\1# SOVEREIGNTY: Use filesystem MCP - \2",
                content
            )
            
            file_path.write_text(content, encoding="utf-8")
            Logger.info(f"[L0 FILESYSTEM HEALING] Flagged direct file I/O in {file_path}")
            return True
        except Exception as e:
            Logger.error(f"[L0 FILESYSTEM HEALING] Failed: {e}")
            return False


# Import Phase 17B Vector Healing Strategy
from agentic_core.L0_maintenance.P1_core.VectorHealingStrategy import VectorHealingStrategy
# Import Phase 17C Knowledge Graph Healing Strategy
from agentic_core.L0_maintenance.P1_core.kg_healing_strategy import KnowledgeGraphHealingStrategy
# Import Phase 17D GitKraken Healing Strategy
from agentic_core.L0_maintenance.P1_core.gitkraken_healing_strategy import GitKrakenHealingStrategy
# Import Phase 17E DeepWiki Healing Strategy
from agentic_core.L0_maintenance.P1_core.deepwiki_healing_strategy import DeepWikiHealingStrategy
# Import Phase 17F L6 Audit Healing Strategy
from agentic_core.L0_maintenance.P1_core.L6AuditHealingStrategy import L6AuditHealingStrategy

# Registry of all available healing strategies
# NAMING FIXED: HEALING_STRATEGIES → healing_strategies
healing_strategies = [
    DirectRedisHealing(),  # Phase 17: Autonomous Healing (Dec 27, 2025)
    DirectLLMHealing(),  # Phase 17: Autonomous Healing (Dec 27, 2025)
    FilesystemBypassHealing(),  # Phase 17: Autonomous Healing (Dec 27, 2025)
    # Use factory functions to ensure async clients are initialized if needed
    # or ensuring consistent instantiation patterns
    VectorHealingStrategy(),
    KnowledgeGraphHealingStrategy(),
    GitKrakenHealingStrategy(),
    DeepWikiHealingStrategy(),
    L6AuditHealingStrategy(),
    StructureHealing(),
    UnderscoreFieldHealing(),
    DarkReasoningHealing(),
    ObservabilityHealing(),  # Phase 10: Dark Reasoning Healing (Dec 26, 2025)
    DDDAlignmentHealing()
]


def get_strategy_by_name(name: str) -> HealingStrategy:
    """Get a healing strategy by name."""
    for strategy in HEALING_STRATEGIES:
        if strategy.name.lower() == name.lower():
            return strategy
    return None


def get_strategies_by_priority() -> List[HealingStrategy]:
    """Get all strategies sorted by priority (lower number = higher priority)."""
    return sorted(HEALING_STRATEGIES, key=lambda s: s.priority)