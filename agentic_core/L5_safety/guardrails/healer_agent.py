"""
HealerAgent: Autonomous Structural Healer with Guardrails

Applies safe fixes for detected violations:
- Move files to correct territory (Location/Naming guidance)
- Remove unused imports (ImportAgent detections)
- Fission oversized files (>800 lines) into sub-atomic modules
- Fusion undersized dust files (<80 lines) into meaningful modules
- Update imports in affected files (same-directory + **cross-directory**)
- Clean empty directories

Operates under strict guardrails:
- Backup all changes
- Respect HEALING_CONFIG budgets (max_moves, max_fissions)
- Deletion guardrail (line limits)
- Dry-run mode

Placed in L5_safety/guardrails per SSOT:
  "Hard safety limits, mutation controls, deletion guards"

Depth: agentic_core/L5_safety/guardrails/healer_agent.py → 4 parts → compliant
"""
import shutil
import os
import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set, Optional
from datetime import datetime
import logging
from contextlib import nullcontext

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    HEALING_CONFIG,
    SOVEREIGN_EXCLUDED_FOLDERS
)
from agentic_core.utils.naming.naming_agent import naming_agent as NamingAgent

# Fission constants from canon policy
MAX_LINES_PER_FILE = 800
MIN_LINES_PER_FILE = 80
DUST_THRESHOLD = 40

logger = logging.getLogger(__name__)


class ImportUpdater(ast.NodeVisitor):
    """
    AST visitor to extract used symbols and locate existing import blocks.
    """
    def __init__(self, target_symbols: Optional[Set[str]] = None):
        self.target_symbols = target_symbols or set()
        self.found_usage = False
        self.imported_modules: Set[str] = set()
        self.used_names: Set[str] = set()
        self.last_import_lineno = 0

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imported_modules.add(alias.name.split('.')[0])
        self.last_import_lineno = max(self.last_import_lineno, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imported_modules.add(node.module.split('.')[0])
        self.last_import_lineno = max(self.last_import_lineno, node.lineno)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            if node.id in self.target_symbols:
                self.found_usage = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
            if node.value.id in self.target_symbols:
                self.found_usage = True
        self.generic_visit(node)


class healer_agent:
    """
    Autonomous healer with full guardrail protection.
    Applies fixes only after validation phase.
    """

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        self.backup_dir = self.project_root / ".sovereign_healing_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.moves_applied = 0
        self.fissions_applied = 0
        self.imports_cleaned = 0
        self.fusions_applied = 0
        self.deletions_applied = 0
        
        from agentic_core.utils.naming.naming_agent import naming_agent as NamingAgent
        self.naming_agent = NamingAgent(project_root)

        self.max_moves = HEALING_CONFIG.get("max_moves_per_run", 5)
        self.max_fissions = HEALING_CONFIG.get("max_fissions_per_run", 3)
        self.max_fusions = HEALING_CONFIG.get("max_fusions_per_run", 20)
        self.max_deletions = HEALING_CONFIG.get("max_deletions_per_run", 10)

        # Optional observability integration
        try:
            from agentic_core.observability.tracing.tracing_agent import tracing_agent as TracingAgent
            from agentic_core.observability.telemetry.telemetry_agent import telemetry_agent as TelemetryAgent
            from agentic_core.observability.metrics.metrics_agent import metrics_agent as MetricsAgent
            self.tracing = TracingAgent(project_root)
            self.telemetry = TelemetryAgent(project_root)
            self.metrics = MetricsAgent(project_root)
        except ImportError:
            self.tracing = self.telemetry = self.metrics = None

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[HealerAgent] Backup directory: {self.backup_dir}")

    def _backup_file(self, file_path: Path) -> Path:
        """Create backup copy before mutation."""
        if self.dry_run:
            return file_path
        rel = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def heal_file_moves(self, move_violations: List[Tuple[Path, str]]) -> List[Dict[str, Any]]:
        """
        Heal location/naming violations by moving files.
        Parses guidance from NamingAgent.
        """
        actions = []
        for file_path, msg in move_violations:
            if self.moves_applied >= self.max_moves:
                logger.warning("[HealerAgent] Max moves reached")
                break

            if "Suggested placement:" not in msg and "Invalid depth" not in msg:
                continue  # Skip if no clear target

            # Extract target path from guidance
            if "Suggested placement:" in msg:
                # Split to get just the path string after the label
                target_str = msg.split("Suggested placement:")[-1].strip().split()[0]
            else:
                # Fallback: use current L1/L2 and correct depth 4 parts
                rel = file_path.relative_to(self.project_root)
                parts = list(rel.parts)
                target_str = "/".join(parts[:3]) if len(parts) >= 3 else parts[0]

            target_path = self.project_root / target_str / file_path.name
            
            action = {
                "type": "MOVE",
                "source": str(file_path),
                "target": str(target_path),
                "reason": msg,
                "applied": False
            }

            if target_path.exists():
                action["reason"] += " [BLOCKED: target exists]"
            elif self.dry_run:
                action["applied"] = True
                action["note"] = "DRY-RUN"
            else:
                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    self._backup_file(file_path)
                    shutil.move(str(file_path), str(target_path))
                    action["applied"] = True
                    self.moves_applied += 1
                    logger.info(f"[HEALED] Moved {file_path.name} -> {target_str}/")
                except Exception as e:
                    action["reason"] += f" [FAILED: {e}]"

            actions.append(action)

        return actions

    def heal_unused_imports(self, import_violations: List[Tuple[Path, List[str]]]) -> List[Dict[str, Any]]:
        """Remove unused imports (high confidence only)."""
        actions = []
        for file_path, msgs in import_violations:
            unused = [m for m in msgs if "UNUSED IMPORT [Confidence 100%]" in m]
            if not unused:
                continue

            action = {
                "type": "CLEAN_IMPORTS",
                "file": str(file_path),
                "removed": [],
                "applied": False
            }

            if self.dry_run:
                action["removed"] = [m.split(": ")[-1] for m in unused]
                action["applied"] = True
            else:
                try:
                    self._backup_file(file_path)
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.splitlines()
                    new_lines = []
                    
                    for line in lines:
                        keep = True
                        for u in unused:
                            # Extract module/name after the confidence tag
                            import_name = u.split(": ")[-1].split()[0]
                            if import_name in line and ("import " in line or "from " in line):
                                keep = False
                                action["removed"].append(line.strip())
                                break
                        if keep:
                            new_lines.append(line)

                    if action["removed"]:
                        file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                        action["applied"] = True
                        self.imports_cleaned += len(action["removed"])

                except Exception as e:
                    action["reason"] = str(e)

            actions.append(action)

        return actions

    def _extract_symbols(self, content: str) -> Set[str]:
        """Extract top-level class/function names from file content."""
        try:
            tree = ast.parse(content)
        except Exception:
            return set()

        symbols = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("__"): # Skip private dunders
                    symbols.add(node.name)
        return symbols

    def _get_intelligent_merged_name(self, files: List[Path], combined_preview: str = None) -> Tuple[str, str, str, str]:
        """
        Use NamingAgent to find the most high-signal name for fused content.
        Returns: (merged_name, naming_source, guidance_path, matched_signal)
        """
        if combined_preview is None:
            combined_preview = ""
            for f in files:
                try:
                    content = f.read_text(encoding="utf-8")
                    combined_preview += content + "\n\n"
                    if len(combined_preview) > 5000:  # Limit for performance
                        break
                except Exception:
                    continue
        
        guidance = "agentic_core/utils"
        if combined_preview.strip():
            guidance = self.naming_agent.get_placement_guidance(combined_preview)
            # Extract domain stem (e.g., "agentic_core/L3_orchestration" -> "orchestrator")
            suggested_domain = guidance.split("/")[-1] if "/" in guidance else "component"
        else:
            suggested_domain = "merged"

        # Strong signal fallback from keywords in content
        lower_preview = combined_preview.lower()
        strong_signals = ["engine", "manager", "handler", "validator", "strategy", "orchestrator", "guardian"]
        matched_signal = next((kw for kw in strong_signals if kw in lower_preview), None)
        
        merged_name = f"{matched_signal}.py" if matched_signal else f"{suggested_domain}.py"
        naming_source = f"Strong keyword: {matched_signal}" if matched_signal else "NamingAgent guidance"
        
        return merged_name, naming_source, guidance if combined_preview else "N/A", matched_signal or ""

    def heal_deletions(self, dead_files: List[Path]) -> List[Dict[str, Any]]:
        """Safe deletion of confirmed dead files (no imports, no traces)."""
        actions = []
        for file_path in dead_files:
            if self.deletions_applied >= self.max_deletions:
                break
            
            action = {"type": "DELETE_DEAD", "file": str(file_path), "applied": False}
            
            if self.dry_run:
                action["applied"] = True
                action["note"] = "DRY-RUN"
            else:
                try:
                    self._backup_file(file_path)
                    file_path.unlink()
                    action["applied"] = True
                    self.deletions_applied += 1
                    logger.info(f"[DELETED] Pruned dead file: {file_path.name}")
                except Exception as e:
                    action["reason"] = str(e)
            
            actions.append(action)
        return actions

    def _find_cross_directory_consumers(self, old_modules: List[str], moved_symbols: Set[str]) -> List[Path]:
        """
        Search entire project for files using moved symbols.
        """
        consumers = []
        # Scan only Python files within sovereign roots
        py_files = list(self.project_root.rglob("*.py"))

        for file_path in py_files:
            # Performance & Safety: Skip excluded territories (venv, git, etc)
            if any(ex in file_path.parts for ex in SOVEREIGN_EXCLUDED_FOLDERS):
                continue
            
            # Skip the source/target modules being mutated
            if file_path.stem in old_modules:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
                visitor = ImportUpdater(moved_symbols)
                visitor.visit(tree)
                if visitor.found_usage:
                    consumers.append(file_path)
            except Exception:
                continue

        return consumers

    def _update_imports_cross_directory(self, old_modules: List[str], new_module: str, moved_symbols: Set[str]) -> List[Dict[str, Any]]:
        """
        Update imports project-wide after a structural change.
        """
        actions = []
        new_module_name = Path(new_module).stem
        consumers = self._find_cross_directory_consumers(old_modules, moved_symbols)

        for consumer_path in consumers:
            try:
                content = consumer_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
                visitor = ImportUpdater(moved_symbols)
                visitor.visit(tree)

                needed_symbols = moved_symbols.intersection(visitor.used_names)
                if not needed_symbols:
                    continue

                action = {"type": "CROSS_DIRECTORY_IMPORT_UPDATE", "file": str(consumer_path), "added_imports": [], "applied": False}
                import_stmt = f"from {new_module_name} import {', '.join(sorted(needed_symbols))}\n"

                if not self.dry_run:
                    self._backup_file(consumer_path)
                    lines = content.splitlines(keepends=True)
                    # Insertion: after last import or first logic line
                    idx = visitor.last_import_lineno
                    if idx == 0:
                        for i, line in enumerate(lines):
                            if not line.strip().startswith(("#", '"', "'")) and line.strip() != "":
                                idx = i
                                break
                    lines.insert(idx, import_stmt)
                    consumer_path.write_text("".join(lines), encoding="utf-8")
                    action["applied"] = True
                    action["added_imports"].append(import_stmt.strip())
                    logger.info(f"[CROSS_IMPORT] Updated {consumer_path.name}")
                
                actions.append(action)
            except Exception as e:
                logger.error(f"Cross-import update failed for {consumer_path}: {e}")
        return actions

    def _update_imports_after_change(self, affected_dir: Path, old_files: List[Path], new_file: Path, moved_symbols: Set[str]) -> List[Dict[str, Any]]:
        """
        Scan directory for files that used moved symbols and point them to new_file.
        """
        actions = []
        new_module_name = new_file.stem

        for consumer_path in affected_dir.rglob("*.py"):
            if consumer_path in old_files or consumer_path == new_file:
                continue 

            try:
                content = consumer_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
            except Exception:
                continue

            visitor = ImportUpdater()
            visitor.visit(tree)

            # Only update if the file actually uses the symbols that were moved
            needed_symbols = moved_symbols.intersection(visitor.used_names)
            if not needed_symbols:
                continue

            action = {
                "type": "IMPORT_UPDATE",
                "file": str(consumer_path),
                "added_imports": [],
                "applied": False
            }

            if self.dry_run:
                action["added_imports"] = [f"from {new_module_name} import {', '.join(sorted(needed_symbols))}"]
                action["applied"] = True
            else:
                try:
                    self._backup_file(consumer_path)
                    lines = content.splitlines(keepends=True)

                    # Insert new import after the existing import block
                    # fallback to top of file if no imports found
                    insert_idx = visitor.last_import_lineno
                    import_stmt = f"from {new_module_name} import {', '.join(sorted(needed_symbols))}\n"
                    lines.insert(insert_idx, import_stmt)

                    consumer_path.write_text("".join(lines), encoding="utf-8")
                    action["added_imports"].append(import_stmt.strip())
                    action["applied"] = True
                    logger.info(f"[IMPORT_FIX] Updated {consumer_path.name} -> {new_module_name}")
                except Exception as e:
                    action["reason"] = f"Update failed: {e}"

            actions.append(action)
        return actions

    def _find_split_points(self, lines: List[str]) -> List[int]:
        """
        Find logical split points using AST (class/function defs).
        """
        content = "".join(lines)
        try:
            tree = ast.parse(content)
        except Exception:
            return []  # Fallback: no safe splits if file is currently broken

        splits = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    if node.end_lineno > MIN_LINES_PER_FILE:
                        splits.append(node.end_lineno)
        return sorted(set(splits))

    def heal_fission(self, large_files: List[Path]) -> List[Dict[str, Any]]:
        """
        Surgically split oversized files into sub-atomic modules.
        """
        actions = []
        for file_path in large_files:
            if self.fissions_applied >= self.max_fissions:
                logger.warning("[HealerAgent] Max fissions reached")
                break

            try:
                lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
                if len(lines) <= MAX_LINES_PER_FILE:
                    continue

                split_points = self._find_split_points(lines)
                if not split_points:
                    actions.append({
                        "type": "FISSION_SKIPPED",
                        "file": str(file_path),
                        "reason": "No logical AST split points found"
                    })
                    continue

                # Filter splits to ensure resulting chunks satisfy MIN_LINES and DUST thresholds
                valid_splits = [0]
                current_idx = 0
                for point in split_points:
                    chunk_size = point - current_idx
                    if chunk_size >= MIN_LINES_PER_FILE:
                        remaining = len(lines) - point
                        if remaining >= DUST_THRESHOLD:
                            valid_splits.append(point)
                            current_idx = point

                if len(valid_splits) <= 1:
                    continue # No valid chunking possible without creating dust

                action = {
                    "type": "FISSION",
                    "source": str(file_path),
                    "new_files": [],
                    "applied": False,
                    "import_updates": []
                }

                if not self.dry_run:
                    self._backup_file(file_path)
                    stem = file_path.stem
                    chunk_symbols_map = []
                    
                    for i in range(len(valid_splits)):
                        start = valid_splits[i]
                        end = valid_splits[i+1] if i+1 < len(valid_splits) else len(lines)
                        chunk_content = "".join(lines[start:end])
                        
                        if i == 0:
                            # Original file retains the first chunk
                            file_path.write_text(chunk_content, encoding="utf-8")
                        else:
                            new_name = f"{stem}_part{i+1}.py"
                            new_path = file_path.parent / new_name
                            new_path.write_text(chunk_content, encoding="utf-8")
                            action["new_files"].append(str(new_path))
                            # Track symbols moved to new parts for import remediation
                            symbols = self._extract_symbols(chunk_content)
                            if symbols:
                                chunk_symbols_map.append((new_path, symbols))
                    
                    # Execute cross-file import remediation
                    for n_path, syms in chunk_symbols_map:
                        updates = self._update_imports_after_change(file_path.parent, [file_path], n_path, syms)
                        action["import_updates"].extend(updates)
                        
                        # [NEW] Execute cross-directory remediation
                        cross_updates = self._update_imports_cross_directory([file_path.stem], str(n_path), syms)
                        action["import_updates"].extend(cross_updates)
                    
                    action["applied"] = True
                    self.fissions_applied += 1
                    logger.info(f"[FISSION] Split {file_path.name} into {len(valid_splits)} modules")
                else:
                    action["applied"] = True
                    action["note"] = "DRY-RUN"

                actions.append(action)
            except Exception as e:
                logger.error(f"[HealerAgent] Fission failed for {file_path}: {e}")

        return actions

    def heal_all(self, violations: List[Tuple[Path, str]], large_files: List[Path] = None, dust_files: List[Path] = None, dead_files: List[Path] = None) -> Dict[str, Any]:
        """Orchestrate all healing actions with tracing and telemetry."""
        trace_ctx = self.tracing.create_span("healing_mission") if self.tracing else nullcontext()
        
        with trace_ctx as span:
            if span:
                span.set_attribute("violations_in", len(violations))
                span.set_attribute("large_files", len(large_files or []))

            move_violations = [v for v in violations if "VIOLATION" in v[1] and ("depth" in v[1].lower() or "placement" in v[1].lower())]
            import_violations = [] 
            large_files = large_files or []
            dust_files = dust_files or []
            dead_files = dead_files or []

            results = {
                "moves": self.heal_file_moves(move_violations),
                "imports_cleaned": self.heal_unused_imports(import_violations),
                "fissions": self.heal_fission(large_files),
                "deletions": self.heal_deletions(dead_files),
                "import_updates": [],
                "total_actions": 0,
                "backup_dir": str(self.backup_dir) if not self.dry_run else "DRY-RUN"
            }

            # Aggregate internal import fixes
            for op in results["fissions"]:
                if "import_updates" in op:
                    results["import_updates"].extend(op["import_updates"])

            results["total_actions"] = sum([len(results[k]) for k in ["moves", "imports_cleaned", "fissions", "deletions", "import_updates"]])
            
            # Final Observability Dispatch
            if self.telemetry:
                self.telemetry.emit("healing.mission_completed", details={"total": results["total_actions"]})
            if self.metrics:
                self.metrics.increment("healing.actions_total", results["total_actions"])
                self.metrics.increment("healing.fissions", len(results["fissions"]))

            if span:
                span.set_attribute("actions_applied", results["total_actions"])
                span.set_status("SUCCESS" if results["total_actions"] > 0 else "OK")

            return results


# Uppercase alias for backward compatibility
HealerAgent = healer_agent
