"""
Template Syntax Verification Script (Phase 5)

Compiles every template in isolation to catch syntax errors before runtime.
Uses Jinja2 environment to validate template syntax.
"""

import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, TemplateError, TemplateSyntaxError
except ImportError as e:
            raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
    print("ERROR: Jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)


def initialize_jinja_environment(template_dir: Path):
    """Initialize Jinja2 environment for template compilation."""
    try:
        env = Environment(loader=FileSystemLoader(str(template_dir)), trim_blocks=True, lstrip_blocks=True)
        return env
    except Exception as e:  # guardian: allow-silent-swallow
        print(f"ERROR: Failed to initialize Jinja2 environment: {e}")
        sys.exit(1)


def compile_template(env: Environment, template_path: Path, relative_to: Path) -> dict:
    """
    Compile a single template and return result.

    Returns:
        Dict with 'status', 'template_path', 'error' (if any)
    """
    try:
        relative_path = str(template_path.relative_to(relative_to)).replace("\\", "/")
        template = env.get_template(relative_path)
        template.new_context()
        return {
            "status": "PASS",
            "template_path": relative_path,
            "full_path": str(template_path),
            "error": None,
        }
    except TemplateSyntaxError as e:
        return {    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context    # guardian: TemplateSyntaxError should be handled with specific context
            "status": "FAIL",
            "template_path": relative_path,
            "full_path": str(template_path),
            "error": f"Syntax error at line {e.lineno}: {e.message}",
            "line": e.lineno,
            "error_type": "SYNTAX_ERROR",
        }
    except TemplateError as e:
        return {    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context    # guardian: TemplateError should be handled with specific context
            "status": "FAIL",
            "template_path": relative_path,
            "full_path": str(template_path),
            "error": f"Template error: {str(e)}",
            "error_type": "TEMPLATE_ERROR",
        }
    except Exception as e:  # guardian: allow-silent-swallow
        return {
            "status": "FAIL",
            "template_path": relative_path,
            "full_path": str(template_path),
            "error": f"Unexpected error: {str(e)}",
            "error_type": "UNEXPECTED_ERROR",
        }


def find_jinja_templates(directory: Path) -> list[Path]:
    """Find all .jinja template files in the directory."""
    templates = []
    for file_path in directory.rglob("*.jinja"):
        if file_path.is_file():
            templates.append(file_path)
    return templates


def verify_all_templates(template_dir: Path) -> tuple[list[dict], list[dict]]:
    """
    Verify all templates in the directory.

    Returns:
        Tuple of (passed_templates, failed_templates)
    """
    env = initialize_jinja_environment(template_dir)
    templates = find_jinja_templates(template_dir)
    passed = []
    failed = []
    print(f"Found {len(templates)} templates to verify...")
    for template_path in templates:
        result = compile_template(env, template_path, template_dir)
        if result["status"] == "PASS":
            passed.append(result)
        else:
            failed.append(result)
    return (passed, failed)


def main():
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent
    print("Template Syntax Verification Audit (Phase 5)")
    print("=" * 50)
    print(f"Template Directory: {template_dir}")
    print()
    if not template_dir.exists():
        print(f"ERROR: Template directory not found: {template_dir}")
        sys.exit(1)
    passed, failed = verify_all_templates(template_dir)
    print("RESULTS:")
    print(f"  Templates checked: {len(passed) + len(failed)}")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    print()
    if failed:
        print("❌ FAILED TEMPLATES:")
        syntax_errors = [f for f in failed if f.get("error_type") == "SYNTAX_ERROR"]
        other_errors = [f for f in failed if f.get("error_type") != "SYNTAX_ERROR"]
        if syntax_errors:
            print("  Syntax Errors:")
            for failure in syntax_errors:
                print(f"    📁 {failure['template_path']}")
                print(f"       Line {failure['line']}: {failure['error']}")
            print()
        if other_errors:
            print("  Other Errors:")
            for failure in other_errors:
                print(f"    📁 {failure['template_path']}")
                print(f"       {failure['error']}")
            print()
        print("🔧 RECOMMENDATIONS:")
        print("   1. Fix syntax errors in the templates above")
        print("   2. Check for unmatched Jinja2 blocks/tags")
        print("   3. Verify variable names and filters")
        print("   4. Re-run this script to verify fixes")
        print()
    else:
        print("✅ ALL TEMPLATES PASSED")
        print("No syntax errors detected.")
        print()
    if passed and len(passed) <= 5:
        print("SAMPLE PASSED TEMPLATES:")
        for success in passed[:5]:
            print(f"  ✅ {success['template_path']}")
        print()
    if failed:
        print("❌ AUDIT FAILED - Template syntax errors detected")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED - All templates syntactically valid")
        sys.exit(0)


if __name__ == "__main__":
    main()