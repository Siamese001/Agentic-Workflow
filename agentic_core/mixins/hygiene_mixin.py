"""
unified_hygiene_mixin.py - HARDENED: Unified code hygiene validation
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.exceptions.SovereignError import HygieneError
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class HygieneMixin:
    """
    HARDENED: Unified code hygiene validation and healing.
    SALVAGED: Consolidated from HygieneValidatorAgent.py.
    """

    project_root: Path = field(default_factory=Path.cwd)
    allowed_duplicates: set[str] = field(default_factory=lambda: {"__init__.py", "README.md", ".gitignore"})

    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        HARDENED: Unified hygiene healing with comprehensive validation.
        """
        try:
            hygiene_results = self._analyze_hygiene_violations()
            violations_found = len(hygiene_results.get("empty_files", [])) + len(
                hygiene_results.get("duplicate_files", [])
            )
            violations_fixed = 0
            if execute and (not dry_run):
                violations_fixed = self._fix_hygiene_violations(hygiene_results)
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": 0,
                "skipped": 0,
            }
        except Exception as e:
            raise HygieneError(f"Hygiene healing failed: {e}") from e

    def _analyze_hygiene_violations(self) -> dict[str, list[dict[str, Any]]]:
        """
        Analyze hygiene violations across the project.
        SALVAGED: Comprehensive hygiene analysis from legacy HygieneValidatorAgent.
        """
        results = {"empty_files": [], "duplicate_files": [], "large_files": [], "syntax_errors": []}
        try:
            file_hashes = {}
            for py_file in self.project_root.rglob("*.py"):
                if py_file.name.startswith(".") or "__pycache__" in str(py_file):
                    continue
                rel_path = py_file.relative_to(self.project_root)
                try:
                    if py_file.stat().st_size == 0:
                        content = py_file.read_text(encoding="utf-8")
                        if not content.strip():
                            results["empty_files"].append({"file": str(rel_path), "size": 0})
                    if py_file.name not in self.allowed_duplicates:
                        file_hash = self._calculate_file_hash(py_file)
                        if file_hash in file_hashes:
                            results["duplicate_files"].append(
                                {"file": str(rel_path), "duplicate_of": file_hashes[file_hash]}
                            )
                        else:
                            file_hashes[file_hash] = str(rel_path)
                    if py_file.stat().st_size > 1024 * 1024:
                        results["large_files"].append(
                            {"file": str(rel_path), "size_bytes": py_file.stat().st_size}
                        )
                    try:
                        import ast

                        content = py_file.read_text(encoding="utf-8")
                        ast.parse(content)
                    except SyntaxError as e:
                        results["syntax_errors"].append({"file": str(rel_path), "error": str(e)})
                except (OSError, UnicodeDecodeError) as e:
                    self.logger.debug(f"Failed to scan {rel_path}: {e}")
                    continue
        except Exception as e:
            raise HygieneError(f"Hygiene analysis failed: {str(e)}") from e
        return results

    def _fix_hygiene_violations(self, violations: dict[str, list[dict[str, Any]]]) -> int:
        """
        Fix hygiene violations.
        SALVAGED: Automated fixing from legacy hygiene validators.
        """
        fixed = 0
        for item in violations.get("empty_files", []):
            try:
                file_path = self.project_root / item["file"]
                if file_path.exists():
                    file_path.unlink()
                    fixed += 1
            except OSError as e:
                self.logger.debug(f"Failed to remove {file_path.name}: {e}")
                continue
        for item in violations.get("duplicate_files", []):
            try:
                duplicate_path = self.project_root / item["file"]
                if duplicate_path.exists():
                    duplicate_path.unlink()
                    fixed += 1
            except OSError as e:
                self.logger.debug(f"Failed to remove {duplicate_path.name}: {e}")
                continue
        return fixed

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for duplicate detection.
        SALVAGED: Hash calculation from legacy duplicate detection.
        """
        try:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except Exception as e:
            raise HygieneError(f"Failed to calculate hash for {file_path}: {str(e)}") from e

    def get_hygiene_report(self) -> dict[str, Any]:
        """
        Generate comprehensive hygiene report.
        SALVAGED: Reporting functionality from legacy HygieneValidatorAgent.
        """
        try:
            violations = self._analyze_hygiene_violations()
            report = {
                "summary": {
                    "total_files": sum(
                        1
                        for _ in self.project_root.rglob("*.py")
                        if not _.name.startswith(".") and "__pycache__" not in str(_)
                    ),
                    "empty_files": len(violations["empty_files"]),
                    "duplicate_files": len(violations["duplicate_files"]),
                    "large_files": len(violations["large_files"]),
                    "syntax_errors": len(violations["syntax_errors"]),
                    "total_violations": sum(len(v) for v in violations.values()),
                },
                "details": violations,
                "recommendations": self._generate_recommendations(violations),
            }
            return report
        except Exception as e:
            raise HygieneError(f"Failed to generate hygiene report: {str(e)}") from e

    def _generate_recommendations(self, violations: dict[str, list[dict[str, Any]]]) -> list[str]:
        """
        Generate recommendations based on violations found.
        SALVAGED: Recommendation engine from legacy hygiene validators.
        """
        recommendations = []
        if violations["empty_files"]:
            recommendations.append(f"Remove {len(violations['empty_files'])} empty files")
        if violations["duplicate_files"]:
            recommendations.append(f"Resolve {len(violations['duplicate_files'])} duplicate files")
        if violations["large_files"]:
            recommendations.append(f"Refactor {len(violations['large_files'])} large files (>1MB)")
        if violations["syntax_errors"]:
            recommendations.append(f"Fix {len(violations['syntax_errors'])} syntax errors")
        if not recommendations:
            recommendations.append("No hygiene violations found - codebase is clean!")
        return recommendations

    def validate_file_hygiene(self, file_path: Path) -> dict[str, Any]:
        """
        Validate hygiene of a specific file.
        SALVAGED: Individual file validation from legacy hygiene validators.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HygieneMixin.validate_file_hygiene")

        if not file_path.exists():
            raise HygieneError(f"File not found: {file_path}")
        try:
            violations = []
            if file_path.stat().st_size == 0:
                content = file_path.read_text(encoding="utf-8")
                if not content.strip():
                    violations.append("Empty file")
            if file_path.stat().st_size > 1024 * 1024:
                violations.append("Large file (>1MB)")
            try:
                import ast

                content = file_path.read_text(encoding="utf-8")
                ast.parse(content)
            except SyntaxError as e:
                violations.append(f"Syntax error: {e}")
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "is_clean": len(violations) == 0,
                "violations": violations,
                "size_bytes": file_path.stat().st_size,
            }
        except Exception as e:
            raise HygieneError(f"File hygiene validation failed for {file_path}: {str(e)}") from e
