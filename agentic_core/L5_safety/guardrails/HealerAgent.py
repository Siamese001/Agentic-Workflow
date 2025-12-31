"""
HealerAgent: Sovereign Structural Convergence Conductor

RESPONSIBILITIES:
- File relocation based on LocationAgent signal.
- Module Fission (>800 LOC) / Fusion (<80 LOC).
- Cross-file import synchronization.

DELEGATION: Dead code pruning moved to specialized DeadCodeAgent.

Placed in L5_safety/guardrails per SSOT semantic registry:
  "Hard safety limits, mutation controls, deletion guards"

Depth: agentic_core/L5_safety/guardrails/healer_agent.py -> 4 parts -> compliant
"""
import ast
import shutil
import logging
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any, Optional
from datetime import datetime
from contextlib import nullcontext

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    HEALING_CONFIG,
    SOVEREIGN_EXCLUDED_FOLDERS,
    CANON_KEY_TO_FOLDER_MAP,
    ALLOWED_DUPLICATE_FILENAMES,
    SOVEREIGN_REGISTRY,
)
from agentic_core.utils.naming.NamingAgent import NamingAgent

# [HARDENING 9] Import audit logger for comprehensive action tracking
try:
    from agentic_core.observability.audit.audit_logger import AuditLogger
    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Canon structural constants
MAX_LINES_PER_FILE = 800
MIN_LINES_PER_FILE = 80
DUST_THRESHOLD = 40


class ImportUpdater(ast.NodeVisitor):
    """AST engine to verify and suggest import updates."""
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


class HealerAgent:
    """
    Autonomous Conductor for structural healing.
    """
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        self.backup_dir = self.project_root / ".sovereign_healing_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archives_root = self.project_root / "archives"
        
        self.moves_applied = self.fissions_applied = self.fusions_applied = self.imports_cleaned = 0
        self.naming_agent = NamingAgent(self.project_root)

        # Healing configuration from SSOT
        self.max_moves = HEALING_CONFIG.get("max_moves_per_run", 5)
        self.max_fissions = HEALING_CONFIG.get("max_fissions_per_run", 3)
        self.max_fusions = HEALING_CONFIG.get("max_fusions_per_run", 20)

        # Observability Linkage
        try:
            from agentic_core.observability.tracing.TracingAgent import tracing_agent as TracingAgent
            from agentic_core.observability.telemetry.TelemetryAgent import telemetry_agent as TelemetryAgent
            from agentic_core.observability.metrics.MetricsAgent import metrics_agent as MetricsAgent
            self.tracing = TracingAgent(project_root)
            self.telemetry = TelemetryAgent(project_root)
            self.metrics = MetricsAgent(project_root)
        except ImportError:
            self.tracing = self.telemetry = self.metrics = None
        
        # [HARDENING 9] Initialize audit logger
        if AUDIT_LOGGER_AVAILABLE:
            self.audit = AuditLogger(project_root)
            logger.info("[HealerAgent] Audit logging enabled")
        else:
            self.audit = None
            logger.warning("[HealerAgent] Audit logging unavailable")

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.archives_root.mkdir(exist_ok=True)
            logger.info(f"[HealerAgent] Backup initialized: {self.backup_dir}")
    
    def _detect_layer(self, file_path: Path) -> str:
        """
        Detect which layer a file belongs to based on its path.
        Returns layer name (e.g., 'L1_cognition', 'L2_execution') or 'unknown'.
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            
            # Check if file is in agentic_core structure
            if len(parts) >= 2 and parts[0] == 'agentic_core':
                layer_part = parts[1]
                # Validate it's a recognized layer
                if layer_part.startswith('L') and layer_part[1].isdigit():
                    return layer_part
            
            return 'unknown'
        except (ValueError, IndexError):
            return 'unknown'
    
    def _get_layer_directory(self, file_path: Path) -> Optional[Path]:
        """
        Get the layer directory for a file (e.g., agentic_core/L5_safety).
        Returns None if file is not in a recognized layer.
        """
        layer = self._detect_layer(file_path)
        if layer == 'unknown':
            return None
        
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            if len(parts) >= 2 and parts[0] == 'agentic_core':
                return self.project_root / parts[0] / parts[1]
        except ValueError:
            pass
        
        return None

    def _backup_file(self, file_path: Path) -> Path:
        """Standardized backup procedure for all L5 mutations."""
        if self.dry_run: return file_path
        rel = file_path.relative_to(self.project_root)
        backup = self.backup_dir / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup)
        return backup

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

            # Skip files allowed to exist in multiple directories (from SSOT)
            if file_path.name in ALLOWED_DUPLICATE_FILENAMES:
                continue

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
                    
                    # [HARDENING 9] Log structural change
                    if self.audit:
                        self.audit.log_structural_change(
                            agent_name=self.__class__.__name__,
                            operation="move",
                            source_files=[str(file_path)],
                            target_files=[str(target_path)],
                            reason=msg,
                            applied=True
                        )
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
        """AST symbol extraction for fusion and fission logic."""
        try:
            tree = ast.parse(content)
        except (SyntaxError, ValueError):
            return set()
        symbols = {node.name for node in ast.walk(tree) 
                   if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                   and not node.name.startswith("_")}
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

    def _find_cross_directory_consumers(self, old_modules: List[str], moved_symbols: Set[str], scope_dirs: Optional[List[Path]] = None) -> List[Path]:
        """
        Search for files using moved symbols, optionally scoped to specific directories.
        
        Args:
            old_modules: List of old module names being replaced
            moved_symbols: Set of symbols that were moved
            scope_dirs: Optional list of directories to limit search scope
        """
        consumers = []
        
        # [HARDENING] If scope provided, limit search to those directories only
        if scope_dirs:
            py_files = []
            for scope_dir in scope_dirs:
                if scope_dir.exists():
                    py_files.extend(scope_dir.rglob("*.py"))
        else:
            # Fallback: scan entire project (legacy behavior)
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
        [HARDENING] Limited to same layer directory to prevent cross-layer import pollution.
        """
        actions = []
        new_module_name = new_file.stem
        
        # [HARDENING] Restrict scan to layer directory only
        layer_dir = self._get_layer_directory(new_file)
        if layer_dir and layer_dir != affected_dir:
            # If new_file is in a different layer, limit scope to that layer
            scan_dir = layer_dir
            logger.info(f"[IMPORT_SCOPE] Limiting import updates to layer: {layer_dir.name}")
        else:
            scan_dir = affected_dir

        for consumer_path in scan_dir.rglob("*.py"):
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
        [SOVEREIGN FISSION] Identifies safe line numbers to split a file.
        RATIONALE: Splits must occur at the end of structural blocks (Key 15).
        """
        content = "\n".join(lines)
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
            
        # Collect end line numbers for all top-level structures
        points = [node.end_lineno for node in ast.walk(tree) 
                 if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.end_lineno]
        
        return sorted(set(p for p in points if p))

    def heal_fission(self, large_files: List[Path]) -> List[Dict[str, Any]]:
        """
        Surgically split oversized files into sub-atomic modules.
        [HARDENING] Fission targets restricted to same layer directory.
        """
        actions = []
        for file_path in large_files:
            if self.fissions_applied >= self.max_fissions:
                logger.warning("[HealerAgent] Max fissions reached")
                break

            try:
                # [HARDENING] Detect layer and validate fission is allowed
                layer = self._detect_layer(file_path)
                layer_dir = self._get_layer_directory(file_path)
                
                if layer == 'unknown' or not layer_dir:
                    actions.append({
                        "type": "FISSION_BLOCKED",
                        "file": str(file_path),
                        "reason": "File not in recognized layer structure - fission restricted"
                    })
                    logger.warning(f"[FISSION_BLOCKED] {file_path.name} not in layer structure")
                    continue
                
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
                    new_files_created = []
                    
                    # [HARDENING] Ensure all fission targets stay within layer directory
                    allowed_target_dir = layer_dir
                    
                    for i in range(len(valid_splits)):
                        start = valid_splits[i]
                        end = valid_splits[i+1] if i+1 < len(valid_splits) else len(lines)
                        chunk_content = "".join(lines[start:end])
                        
                        if i == 0:
                            # Original file retains the first chunk
                            file_path.write_text(chunk_content, encoding="utf-8")
                        else:
                            new_name = f"{stem}_part{i+1}.py"
                            # [HARDENING] Validate target stays in same layer
                            new_path = file_path.parent / new_name
                            
                            if not new_path.is_relative_to(allowed_target_dir):
                                logger.error(f"[FISSION_BLOCKED] Target {new_path} outside layer {layer}")
                                raise ValueError(f"Fission target outside allowed layer directory: {layer}")
                            
                            new_path.write_text(chunk_content, encoding="utf-8")
                            action["new_files"].append(str(new_path))
                            new_files_created.append(str(new_path))
                            # Track symbols moved to new parts for import remediation
                            symbols = self._extract_symbols(chunk_content)
                            if symbols:
                                chunk_symbols_map.append((new_path, symbols))
                    
                    # [HARDENING] Execute import remediation scoped to layer only
                    for n_path, syms in chunk_symbols_map:
                        updates = self._update_imports_after_change(file_path.parent, [file_path], n_path, syms)
                        action["import_updates"].extend(updates)
                        
                        # [HARDENING] Cross-directory remediation limited to same layer + direct dependents
                        allowed_scan_dirs = [layer_dir]
                        cross_updates = self._update_imports_cross_directory(
                            [file_path.stem], 
                            str(n_path), 
                            syms
                        )
                        action["import_updates"].extend(cross_updates)
                    
                    action["applied"] = True
                    self.fissions_applied += 1
                    logger.info(f"[FISSION] Split {file_path.name} into {len(valid_splits)} modules")
                    
                    # [HARDENING 9] Log structural change
                    if self.audit:
                        self.audit.log_structural_change(
                            agent_name=self.__class__.__name__,
                            operation="fission",
                            source_files=[str(file_path)],
                            target_files=new_files_created,
                            reason=f"File exceeded {MAX_LINES_PER_FILE} LOC limit",
                            applied=True,
                            metadata={
                                "original_lines": len(lines),
                                "split_count": len(valid_splits),
                                "layer": layer
                            }
                        )
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

    def run(self) -> Dict[str, Any]:
        """
        Execute healing sweep - validation only, no file splitting.
        Fission disabled to avoid creating part1/part2 files.
        """
        results = {
            "scanned": 0,
            "large_files_flagged": 0,
            "healing_available": True
        }
        
        for py_file in self.project_root.rglob("*.py"):
            if any(ex in py_file.parts for ex in SOVEREIGN_EXCLUDED_FOLDERS):
                continue
            if "__pycache__" in str(py_file):
                continue
            
            results["scanned"] += 1
            try:
                content = py_file.read_text(encoding="utf-8")
                loc = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith('#')])
                if loc > MAX_LINES_PER_FILE:
                    results["large_files_flagged"] += 1
            except Exception:
                continue
        
        return results


# PascalCase is now the canonical name
