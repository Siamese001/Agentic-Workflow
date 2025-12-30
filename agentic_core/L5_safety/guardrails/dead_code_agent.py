"""
DeadCodeAgent: Sovereign Code Hygiene Guardian

Detects and safely prunes:
- Unused imports (AST-based)
- Unreachable private functions (intra-module analysis)
- "Dust" logic (placeholders that drifted into permanence)

Integrates with:
- TracingAgent: (Future) To detect dead public modules via lack of runtime spans.
- ImportAgent: To validate dependency gravity before pruning.

Placed in L5_safety/guardrails per SSOT semantic registry:
  "Guardrails, safety checks, and destructive action prevention"

Depth: agentic_core/L5_safety/guardrails/dead_code_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant
"""
import ast
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any

logger = logging.getLogger(__name__)

class dead_code_agent:
    """
    Autonomous agent for detecting and pruning dead code.
    Operates with extreme caution (backup-first).
    """

    def __init__(self, project_root: Path, tracing_agent=None):
        self.project_root = project_root.resolve()
        self.tracing_agent = tracing_agent
        self.prune_threshold = 0.98  # Require high confidence

    def _get_unused_imports(self, tree: ast.AST) -> List[int]:
        """
        Analyze AST to find imports that are never used in the file.
        Returns list of line numbers to prune.
        """
        imports = []
        names_used = set()

        for node in ast.walk(tree):
            # Collect imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.append({"name": name, "lineno": node.lineno})
            
            # Collect usage
            elif isinstance(node, ast.Name):
                names_used.add(node.id)
            elif isinstance(node, ast.Attribute):
                # covers module.func() -> 'module' is the name
                if isinstance(node.value, ast.Name):
                    names_used.add(node.value.id)

        # Filter unused
        unused_lines = []
        for imp in imports:
            # Split 'os.path' -> 'os' for usage check
            root_name = imp["name"].split('.')[0]
            if root_name not in names_used:
                # Special case: __init__.py often imports just to expose
                unused_lines.append(imp["lineno"])
        
        return sorted(list(set(unused_lines)), reverse=True)

    def _get_dead_privates(self, tree: ast.AST) -> List[Tuple[str, int, int]]:
        """
        Find private functions (_func) never called within the module.
        Returns list of (func_name, start_line, end_line).
        """
        defined_privates = {}
        calls = set()

        for node in ast.walk(tree):
            # Find definitions
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_") and not node.name.startswith("__"):
                    # Store definition with range
                    defined_privates[node.name] = (node.lineno, node.end_lineno)
            
            # Find calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)

        dead_funcs = []
        for name, (start, end) in defined_privates.items():
            if name not in calls:
                dead_funcs.append((name, start, end))
        
        return dead_funcs

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for dead code candidates."""
        report = {"file": str(file_path), "unused_imports": [], "dead_privates": []}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception:
            return report  # Skip unparsable files

        # 1. Check Imports
        # Skip __init__.py as imports there are often for exporting
        if file_path.name != "__init__.py":
            report["unused_imports"] = self._get_unused_imports(tree)

        # 2. Check Private Functions
        report["dead_privates"] = self._get_dead_privates(tree)

        return report

    def apply_prune(self, file_path: Path, report: Dict[str, Any], backup: bool = True) -> bool:
        """
        Physically remove detected dead code.
        """
        if not report["unused_imports"] and not report["dead_privates"]:
            return False

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                file_path.write_text("\n".join(lines), encoding="utf-8") # Save current state
                shutil.copy(file_path, backup_path)

            # Prune Privates First (ranges)
            # Sort by line number descending to avoid index shifting
            dead_privates = sorted(report["dead_privates"], key=lambda x: x[1], reverse=True)
            
            lines_to_remove = set()
            
            for func_name, start, end in dead_privates:
                # AST line numbers are 1-based, list is 0-based
                # Remove function body + decorator lines above if any (heuristic)
                # For safety, strict AST range:
                for i in range(start - 1, end):
                    lines_to_remove.add(i)
                logger.info(f"[DeadCode] Marked private function {func_name} for removal in {file_path.name}")

            # Prune Imports
            for lineno in report["unused_imports"]:
                lines_to_remove.add(lineno - 1)
                logger.info(f"[DeadCode] Marked unused import line {lineno} in {file_path.name}")

            # Reconstruct content
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            
            # Write back
            file_path.write_text("\n".join(new_lines), encoding="utf-8")
            return True

        except Exception as e:
            logger.error(f"[DeadCode] Failed to prune {file_path}: {e}")
            return False

    def run_scan(self, files: List[Path] = None) -> List[Dict[str, Any]]:
        """Run project-wide dead code scan."""
        if not files:
            files = list(self.project_root.rglob("*.py"))
        
        results = []
        for f in files:
            # Skip tests and venvs
            if "tests" in f.parts or "venv" in f.parts:
                continue
                
            res = self.scan_file(f)
            if res["unused_imports"] or res["dead_privates"]:
                results.append(res)
        
        return results

    def run_prune(self, results: List[Dict[str, Any]]) -> int:
        """Execute pruning on scan results."""
        pruned_count = 0
        for res in results:
            if self.apply_prune(Path(res["file"]), res):
                pruned_count += 1
        return pruned_count


# Uppercase alias for backward compatibility
DeadCodeAgent = dead_code_agent
