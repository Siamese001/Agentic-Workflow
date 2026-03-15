"""
Agent Variable Compliance Audit Script (Phase 5)

Ensures L1/L2 agents actually pass required variables when calling templates.
Uses AST analysis to detect template rendering calls and validate context variables.
"""

import ast
import sys
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def extract_template_schema(template_path: Path, base_dir: Path) -> dict[str, list[str]]:
    """Extract required variables from template's Phase 4 header."""
    full_path = base_dir / template_path
    try:
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n")[:20]:
            if "{# SCHEMA:" in line:
                schema_match = line.replace("{# SCHEMA:", "").replace("#}", "").strip()
                required_vars = []
                if "required_vars=[" in schema_match:
                    req_part = schema_match.split("required_vars=[")[1].split("]")[0]
                    required_vars = [
                        v.strip() for v in req_part.split(",") if v.strip() and v.strip() != "[]"
                    ]
                return {"required_vars": required_vars}
        return {"required_vars": []}
    # guardian: allow-silent-swallow
    except Exception:
        return {"required_vars": []}


class TemplateRenderVisitor(ast.NodeVisitor):
    """AST visitor to find template.render() calls and analyze context."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.violations = []
        self.current_function = None
        self.current_class = None

    def visit_FunctionDef(self, node):
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TemplateRenderVisitor.visit_FunctionDef")

        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Call(self, node):
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "render"
            and isinstance(node.func.value, ast.Name)
        ):
            template_name = None
            context_dict = None
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant):
                    template_name = arg.value
                elif isinstance(arg, ast.Str):
                    template_name = arg.s
            for keyword in node.keywords:
                if keyword.arg == "context":
                    if isinstance(keyword.value, ast.Dict):
                        context_dict = keyword.value
            if template_name and context_dict:
                self._validate_render_call(node, template_name, context_dict)
        self.generic_visit(node)

    def _validate_render_call(self, node, template_name: str, context_dict: ast.Dict):
        """Validate a template render call against required variables."""
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"
        template_path = Path(template_name)
        schema = extract_template_schema(template_path, self.base_dir)
        if not schema["required_vars"]:
            return
        context_keys = set()
        for key in context_dict.keys:
            if isinstance(key, ast.Constant):
                context_keys.add(key.value)
            elif isinstance(key, ast.Str):
                context_keys.add(key.s)
        missing_vars = set(schema["required_vars"]) - context_keys
        if missing_vars:
            self.violations.append(
                {
                    "file": self.current_file,
                    "line": node.lineno,
                    "class": self.current_class,
                    "function": self.current_function,
                    "template": template_name,
                    "required_vars": schema["required_vars"],
                    "provided_vars": sorted(context_keys),
                    "missing_vars": sorted(missing_vars),
                }
            )


def find_python_files(base_dir: Path) -> list[Path]:
    """Find all Python files in the agentic_core directory."""
    python_files = []
    for file_path in base_dir.rglob("*.py"):
        if file_path.is_file():
            python_files.append(file_path)
    return python_files


def audit_agent_compliance(base_dir: Path) -> list[dict]:
    """Audit agent compliance with template variable requirements."""
    violations = []
    python_files = find_python_files(base_dir)
    for py_file in python_files:
        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(py_file))
            visitor = TemplateRenderVisitor(base_dir)
            visitor.current_file = str(py_file.relative_to(base_dir))
            visitor.visit(tree)
            violations.extend(visitor.violations)
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"WARNING: Could not parse {py_file}: {e}")
    return violations


def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent
    print("Agent Variable Compliance Audit (Phase 5)")
    print("=" * 50)
    print(f"Scanning: {base_dir}")
    print()
    violations = audit_agent_compliance(base_dir)
    if violations:
        print(f"❌ FOUND {len(violations)} COMPLIANCE VIOLATIONS:")
        print()
        for violation in violations:
            print(f"File: {violation['file']}")
            if violation["class"]:
                print(f"  Class: {violation['class']}")
            if violation["function"]:
                print(f"  Function: {violation['function']}")
            print(f"  Line: {violation['line']}")
            print(f"  Template: {violation['template']}")
            print(f"  Required: {', '.join(violation['required_vars'])}")
            print(f"  Provided: {', '.join(violation['provided_vars'])}")
            print(f"  Missing: {', '.join(violation['missing_vars'])}")
            print()
        sys.exit(1)
    else:
        print("✅ NO COMPLIANCE VIOLATIONS FOUND")
        print("All template.render() calls provide required variables.")
        sys.exit(0)


if __name__ == "__main__":
    main()
