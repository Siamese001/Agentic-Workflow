"""Audit all Jinja templates in prompt_governance/ for wiring across the repo."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PG_DIR = REPO / "agentic_core" / "prompt_governance"


def find_all_templates():
    """Find all .jinja files in prompt_governance/."""
    return sorted(PG_DIR.rglob("*.jinja"))


def search_references(template_name: str, exclude_dirs=None):
    """Search all .py files in repo for references to this template name."""
    exclude_dirs = exclude_dirs or {".git", "__pycache__", ".healing_backups", "node_modules"}
    refs = []
    for py_file in REPO.rglob("*.py"):
        if any(d in py_file.parts for d in exclude_dirs):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # guardian: allow-silent-swallow -- file read errors are non-critical; skip unreadable files
            continue
        if template_name in content:
            for i, line in enumerate(content.splitlines(), 1):
                if template_name in line:
                    refs.append((py_file.relative_to(REPO), i, line.strip()))
    return refs


def check_deprecated(template_path):
    """Check if template has DEPRECATED header."""
    try:
        content = template_path.read_text(encoding="utf-8")[:500]
        return "DEPRECATED" in content
    except (ValueError, TypeError, RuntimeError) as e:
        return False


def check_registry(template_name):
    """Check if template is in registry.json."""
    import json

    reg_path = PG_DIR / "registry" / "registry.json"
    if not reg_path.exists():
        return False
    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        return template_name in reg.get("prompts", {})
    except (ValueError, TypeError, RuntimeError) as e:
        return False


def main():
    templates = find_all_templates()
    print(f"Total .jinja templates in prompt_governance/: {len(templates)}\n")

    categories = {
        "templates": [],
        "meta_prompts": [],
        "security/adversarial": [],
    }
    for t in templates:
        rel = t.relative_to(PG_DIR).as_posix()
        if rel.startswith("security/adversarial"):
            categories["security/adversarial"].append(t)
        elif rel.startswith("meta_prompts"):
            categories["meta_prompts"].append(t)
        elif rel.startswith("templates"):
            categories["templates"].append(t)

    wired = []
    unwired = []
    deprecated_only = []

    for cat_name, cat_templates in categories.items():
        print(f"\n{'=' * 70}")
        print(f"CATEGORY: {cat_name} ({len(cat_templates)} templates)")
        print(f"{'=' * 70}")

        for t in cat_templates:
            name = t.name
            rel = t.relative_to(PG_DIR).as_posix()
            is_deprecated = check_deprecated(t)
            in_registry = check_registry(name)
            refs = search_references(name)
            # Filter out self-references (the template file itself via .py scripts that glob)
            code_refs = [r for r in refs if not str(r[0]).endswith(".jinja")]

            status = "WIRED" if code_refs else ("DEPRECATED" if is_deprecated else "UNWIRED")
            icon = {"WIRED": "+", "DEPRECATED": "~", "UNWIRED": "!"}[status]

            print(f"\n  [{icon}] {rel}")
            print(f"      Registry: {'YES' if in_registry else 'NO'}")
            print(f"      Deprecated: {'YES' if is_deprecated else 'NO'}")
            print(f"      Code references: {len(code_refs)}")
            for ref_file, ref_line, ref_text in code_refs[:5]:
                print(f"        -> {ref_file}:{ref_line}  {ref_text[:100]}")
            if len(code_refs) > 5:
                print(f"        ... and {len(code_refs) - 5} more")

            if status == "WIRED":
                wired.append(rel)
            elif status == "DEPRECATED":
                deprecated_only.append(rel)
            else:
                unwired.append(rel)

    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total templates:  {len(templates)}")
    print(f"  WIRED (used):     {len(wired)}")
    print(f"  DEPRECATED:       {len(deprecated_only)}")
    print(f"  UNWIRED (unused): {len(unwired)}")

    if unwired:
        print("\n  UNWIRED TEMPLATES (need wiring or deprecation):")
        for u in unwired:
            print(f"    ! {u}")

    if deprecated_only:
        print("\n  DEPRECATED TEMPLATES (documentation-only):")
        for d in deprecated_only:
            print(f"    ~ {d}")

    if wired:
        print("\n  WIRED TEMPLATES:")
        for w in wired:
            print(f"    + {w}")


if __name__ == "__main__":
    main()
