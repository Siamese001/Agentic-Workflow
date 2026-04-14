"""
Analyze apps_shared/base_agents and classify files by functional disposition.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path

from tqdm import tqdm


class AgentDispositionAnalyzer:
    """Analyze agent files for functional DNA classification."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.classifications: dict[str, list[str]] = {
            "CORE_FOUNDATION": [],
            "ACTIVE_SPECIALISTS": [],
            "STATELESS_TOOLS": [],
            "LEGACY_ARTIFACTS": [],
        }
        self.analysis_details: dict[str, dict] = {}

    def analyze_file(self, file_path: Path) -> tuple[str, dict]:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError:
                return ("LEGACY_ARTIFACTS", {"reason": "Syntax error - likely legacy code"})

            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            return self._classify_disposition(file_path.name, content, classes, imports, functions)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return ("LEGACY_ARTIFACTS", {"reason": f"Error reading file: {exc}"})

    def _extract_classes(self, tree: ast.AST) -> list[dict]:
        classes: list[dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in node.bases]
                classes.append(
                    {
                        "name": node.name,
                        "bases": bases,
                        "is_agent": node.name.endswith("Agent"),
                        "is_dataclass": any(
                            (isinstance(dec, ast.Name) and dec.id == "dataclass")
                            or (isinstance(dec, ast.Attribute) and dec.attr == "dataclass")
                            for dec in node.decorator_list
                        ),
                        "has_agent_suffix": "Agent" in node.name,
                        "line_count": max(
                            0,
                            (
                                getattr(node, "end_lineno", getattr(node, "lineno", 0))
                                - getattr(node, "lineno", 0)
                                + 1
                            ),
                        ),
                    }
                )
        return classes

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend(f"{module}.{alias.name}" if module else alias.name for alias in node.names)
        return imports

    def _extract_functions(self, tree: ast.AST) -> list[dict]:
        functions: list[dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "is_method": node.name.startswith("_")
                        or node.name in {"__init__", "_process", "run_phase"},
                        "args_count": len(node.args.args),
                    }
                )
        return functions

    def _classify_disposition(
        self,
        filename: str,
        content: str,
        classes: list[dict],
        imports: list[str],
        functions: list[dict],
    ) -> tuple[str, dict]:
        legacy_indicators = {"deprecated", "v107", "v12", "old", "legacy", "obsolete"}
        if any(indicator in content.lower() for indicator in legacy_indicators):
            return ("LEGACY_ARTIFACTS", {"reason": "Contains legacy/deprecated markers"})

        core_patterns = {
            "mixin",
            "base",
            "interface",
            "protocol",
            "abstract",
            "healerMixin".lower(),
            "mcphardenedmixin",
            "subatomictestingmixin",
            "canon_base_agent_interface",
            "foundation",
        }
        if any(pattern in filename.lower() or pattern in content.lower() for pattern in core_patterns):
            return ("CORE_FOUNDATION", {"reason": "Contains core foundation patterns"})

        agent_classes = [item for item in classes if item["is_agent"] or item["has_agent_suffix"]]
        if agent_classes and len(classes) == 1:
            has_init = any(func["name"] == "__init__" for func in functions)
            has_process = any(func["name"] in {"_process", "run_phase", "execute"} for func in functions)
            if has_init and (has_process or len(functions) > 3):
                return (
                    "ACTIVE_SPECIALISTS",
                    {
                        "reason": "Complete agent with initialization and processing logic",
                        "agent_class": agent_classes[0]["name"],
                        "import_count": len(imports),
                    },
                )

        if not agent_classes and functions:
            return (
                "STATELESS_TOOLS",
                {"reason": "Functional utilities without agent state", "function_count": len(functions)},
            )

        validator_patterns = {"validator", "validatoragent", "enforcer", "healer", "detector"}
        if any(pattern in filename.lower() for pattern in validator_patterns):
            if agent_classes:
                return ("ACTIVE_SPECIALISTS", {"reason": "Specialized validator/enforcer agent"})
            return ("STATELESS_TOOLS", {"reason": "Validation utility functions"})

        return ("LEGACY_ARTIFACTS", {"reason": "Unclear classification - treating as legacy"})

    def analyze_directory(self) -> dict:
        if not self.base_path.exists():
            return {"error": f"Directory {self.base_path} does not exist"}

        python_files = sorted(self.base_path.glob("*.py"))
        results = {
            "total_files": len(python_files),
            "classifications": self.classifications.copy(),
            "analysis_details": {},
            "summary": {},
        }

        for file_path in tqdm(python_files, desc="Processing", unit="file"):
            if file_path.name == "__init__.py":
                continue
            classification, details = self.analyze_file(file_path)
            self.classifications[classification].append(file_path.name)
            self.analysis_details[file_path.name] = {"classification": classification, "details": details}

        results["classifications"] = self.classifications
        results["analysis_details"] = self.analysis_details
        results["summary"] = {category: len(files) for category, files in self.classifications.items()}
        return results


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze apps_shared/base_agents for disposition planning.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--base-path", help="Override the default apps_shared/base_agents scan root.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    base_path = (
        Path(args.base_path).expanduser().resolve()
        if args.base_path
        else repo_root / "apps_shared" / "base_agents"
    )
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else repo_root / "agent_disposition_analysis.json"
    )

    print("🔍 GLOBAL CORE EVICTION & AGENT DISPOSITION ANALYSIS")
    print("=" * 60)

    analyzer = AgentDispositionAnalyzer(base_path)
    results = analyzer.analyze_directory()
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return 1

    print(f"📊 Total Files Analyzed: {results['total_files']}")
    print("\n📋 CLASSIFICATION SUMMARY:")
    print("-" * 40)
    for category, count in results["summary"].items():
        print(f"{category.replace('_', ' ')}: {count} files")

    print("\n📄 DETAILED DISPOSITION:")
    print("-" * 40)
    for category, filenames in results["classifications"].items():
        if not filenames:
            continue
        print(f"\n🏷️ {category.replace('_', ' ')} ({len(filenames)} files):")
        for filename in sorted(filenames):
            details = results["analysis_details"][filename]["details"]
            reason = details.get("reason", "No specific reason")
            print(f"   • {filename} - {reason}")

    _atomic_write(output_path, json.dumps(results, indent=2) + "\n")
    print(f"\n💾 Analysis saved to: {output_path}")
    print("\n✅ Analysis complete - Ready for disposition execution!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
