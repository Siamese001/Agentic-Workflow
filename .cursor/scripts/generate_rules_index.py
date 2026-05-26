#!/usr/bin/env python3
"""
RULES_INDEX Generator Script (W5.P1)

Generates deterministic RULES_INDEX.md from source-of-truth files:
- .cursor/rules/*.mdc (and legacy *.md if present)
- .cursor/skills/*/SKILL.md
- .cursor/workflows/*.md
- .cursor/hooks.json

Usage:
    python generate_rules_index.py --dry-run          # Print or write to temp artifact
    python generate_rules_index.py --check          # Compare to RULES_INDEX.md, exit nonzero on drift
    python generate_rules_index.py --write          # Update RULES_INDEX.md (destructive)
    python generate_rules_index.py --artifact PATH  # Write generated output to specific path

Default: --dry-run (no destructive changes)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).parent.parent.parent
WINDSURF_DIR = REPO_ROOT / ".cursor"
RULES_DIR = WINDSURF_DIR / "rules"
SKILLS_DIR = WINDSURF_DIR / "skills"
WORKFLOWS_DIR = WINDSURF_DIR / "workflows"
HOOKS_JSON = WINDSURF_DIR / "hooks.json"
RULES_INDEX_PATH = WINDSURF_DIR / "RULES_INDEX.md"


def extract_frontmatter(content: str) -> Tuple[Dict[str, any], str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    
    metadata = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            # Handle boolean
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            metadata[key] = value
    
    return metadata, body


def scan_rules() -> List[Dict]:
    """Scan .cursor/rules/*.mdc (and legacy *.md) and extract metadata."""
    rules = []
    
    if not RULES_DIR.exists():
        return rules
    
    rule_files = sorted(set(RULES_DIR.glob("*.mdc")) | set(RULES_DIR.glob("*.md")))
    for rule_file in rule_files:
        if rule_file.name.startswith("_"):
            continue
        
        try:
            content = rule_file.read_text(encoding="utf-8")
            metadata, body = extract_frontmatter(content)
            
            # Cursor .mdc: alwaysApply; legacy .md: trigger
            if metadata.get("alwaysApply") is True:
                trigger = "always_on"
            else:
                trigger = metadata.get("trigger", "model_decision")
            if not trigger:
                if "constitutional" in rule_file.name or "global" in rule_file.name:
                    trigger = "always_on"
                else:
                    trigger = "model_decision"
            
            # Check for deprecated/redirect
            is_deprecated = metadata.get("deprecated", False)
            redirect_to = metadata.get("redirect_to", None)
            
            rules.append({
                "filename": rule_file.name,
                "title": metadata.get("name", rule_file.stem.replace("-", " ").title()),
                "trigger": trigger,
                "deprecated": is_deprecated,
                "redirect_to": redirect_to,
                "description": metadata.get("description", ""),
                "size": len(content),
            })
        except Exception as e:
            print(f"Warning: Error reading {rule_file}: {e}", file=sys.stderr)
    
    return rules


def scan_skills() -> List[Dict]:
    """Scan .cursor/skills/*/SKILL.md and extract metadata."""
    skills = []
    
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_") or skill_dir.name.startswith("."):
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        try:
            content = skill_md.read_text(encoding="utf-8")
            metadata, body = extract_frontmatter(content)
            
            # Count files in skill directory
            file_count = len([f for f in skill_dir.rglob("*") if f.is_file()])
            
            # Check for standard files
            has_checklist = (skill_dir / "checklist.md").exists()
            has_procedure = (skill_dir / "procedure.md").exists()
            has_examples = (skill_dir / "examples").exists() or (skill_dir / "examples.md").exists()
            has_decision_tree = (skill_dir / "decision-tree.md").exists()
            
            # Check deprecated status
            is_deprecated = metadata.get("deprecated", False)
            redirect_to = metadata.get("redirect_to", None)
            
            # Check for deprecation notice in content
            has_deprecation_notice = "DEPRECATED" in content and redirect_to in content
            
            skills.append({
                "name": skill_dir.name,
                "title": metadata.get("name", skill_dir.name.replace("-", " ").title()),
                "description": metadata.get("description", ""),
                "deprecated": is_deprecated,
                "redirect_to": redirect_to,
                "has_deprecation_notice": has_deprecation_notice,
                "file_count": file_count,
                "has_checklist": has_checklist,
                "has_procedure": has_procedure,
                "has_examples": has_examples,
                "has_decision_tree": has_decision_tree,
                "size": len(content),
            })
        except Exception as e:
            print(f"Warning: Error reading {skill_md}: {e}", file=sys.stderr)
    
    return skills


def scan_workflows() -> List[Dict]:
    """Scan .cursor/workflows/*.md and extract metadata."""
    workflows = []
    
    if not WORKFLOWS_DIR.exists():
        return workflows
    
    for wf_file in sorted(WORKFLOWS_DIR.glob("*.md")):
        if wf_file.name.startswith("_"):
            continue
        
        try:
            content = wf_file.read_text(encoding="utf-8")
            metadata, body = extract_frontmatter(content)
            
            workflows.append({
                "filename": wf_file.name,
                "title": metadata.get("name", wf_file.stem.replace("-", " ").title()),
                "description": metadata.get("description", ""),
                "trigger": metadata.get("trigger", "model_decision"),
                "size": len(content),
            })
        except Exception as e:
            print(f"Warning: Error reading {wf_file}: {e}", file=sys.stderr)
    
    return workflows


def scan_hooks() -> Optional[Dict]:
    """Scan .cursor/hooks.json and extract counts."""
    if not HOOKS_JSON.exists():
        return None
    
    try:
        content = HOOKS_JSON.read_text(encoding="utf-8")
        hooks_data = json.loads(content)
        
        # hooks.json structure: {"hooks": {"lifecycle_stage": [hook_entries...], ...}}
        hooks_by_stage = hooks_data.get("hooks", {}) if isinstance(hooks_data, dict) else {}
        
        # Count lifecycle stages (top-level keys)
        lifecycle_stage_count = len(hooks_by_stage)
        
        # Count actual hook entries across all stages
        lifecycle_counts = {}
        hook_entry_count = 0
        survivor_count = 0
        replacement_count = 0
        deprecated_or_shim_count = 0
        
        for stage_name, hook_list in hooks_by_stage.items():
            if not isinstance(hook_list, list):
                continue
            
            lifecycle_counts[stage_name] = len(hook_list)
            hook_entry_count += len(hook_list)
            
            for hook in hook_list:
                if not isinstance(hook, dict):
                    continue
                
                if hook.get("survivor", False):
                    survivor_count += 1
                
                if hook.get("replacement_for"):
                    replacement_count += len(hook["replacement_for"])
                
                # Check for deprecated/shim status in metadata or tags
                metadata = hook.get("metadata", {})
                if metadata.get("deprecated") or metadata.get("shim") or hook.get("deprecated"):
                    deprecated_or_shim_count += 1
        
        return {
            "lifecycle_stage_count": lifecycle_stage_count,
            "hook_entry_count": hook_entry_count,
            "lifecycle_counts": lifecycle_counts,
            "survivor_count": survivor_count,
            "replacement_count": replacement_count,
            "deprecated_or_shim_count": deprecated_or_shim_count,
        }
    except Exception as e:
        print(f"Warning: Error reading {HOOKS_JSON}: {e}", file=sys.stderr)
        return None


def generate_index(rules: List[Dict], skills: List[Dict], workflows: List[Dict], hooks: Optional[Dict]) -> str:
    """Generate RULES_INDEX.md content."""
    lines = []
    
    # Header
    lines.append("# RULES_INDEX")
    lines.append("")
    lines.append("**Generated**: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    lines.append("")
    lines.append("This file is auto-generated by `.cursor/scripts/generate_rules_index.py`.")
    lines.append("Manual edits will be overwritten when the generator runs in --write mode.")
    lines.append("")
    lines.append("## Always-On Discipline")
    lines.append("")
    lines.append("SSOT anchor for rules that reference `#always-on-discipline`. Keep always-on")
    lines.append("`.mdc` files invariant-focused; put long procedures in skills/workflows.")
    lines.append("")
    lines.append("- **Tier-1 (always injected):** `AGENTS.md` + `000`–`003` `alwaysApply` rules only.")
    lines.append("- **Tier-2 (on demand):** other `.cursor/rules/*.mdc` via description/globs.")
    lines.append("- **Tier-3 (progressive):** `.cursor/skills/*/SKILL.md` — prefer `mcp-integration` sections over redirect stubs.")
    lines.append("- **Hooks (zero-token enforcement):** `.cursor/hooks.json` → `.cursor/hooks/*.py` + `.cursor/scripts/post_cursor_agent_*.py`.")
    lines.append("")
    lines.append("## Governance SSOT map")
    lines.append("")
    lines.append("| Concern | Canonical | Do not duplicate in |")
    lines.append("|---------|-----------|---------------------|")
    lines.append("| Always-on invariants | `AGENTS.md`, `000`–`003` `.mdc` | Skills, hook stderr |")
    lines.append("| MCP routing tables | `AGENTS.md` autogen + `mcp-integration` §1–§13 | Per-server redirect stubs |")
    lines.append("| Notion DB IDs | `AGENTS.md` NOTION-MAP | `notion` skill body |")
    lines.append("| Author-Gate pipeline | `003-cursor-author-gate-hitl.mdc` | `pre_user_prompt_author_gate_reminder` (replay only) |")
    lines.append("| Post-agent chain | `after_agent_governance_dispatch.py` | `_legacy_cursor/` hooks/scripts (archived W1) |")
    lines.append("| Plan paths | `plan-location.mdc` | `AGENTS.md` prose |")
    lines.append("")
    
    # Summary
    active_rules = [r for r in rules if not r["deprecated"]]
    deprecated_rules = [r for r in rules if r["deprecated"]]
    active_skills = [s for s in skills if not s["deprecated"]]
    deprecated_skills = [s for s in skills if s["deprecated"]]
    
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Category | Active | Deprecated | Total |")
    lines.append(f"|----------|--------|------------|-------|")
    lines.append(f"| Rules | {len(active_rules)} | {len(deprecated_rules)} | {len(rules)} |")
    lines.append(f"| Skills | {len(active_skills)} | {len(deprecated_skills)} | {len(skills)} |")
    lines.append(f"| Workflows | {len(workflows)} | — | {len(workflows)} |")
    if hooks:
        lines.append(f"| Hooks | {hooks['hook_entry_count']} | {hooks['deprecated_or_shim_count']} | {hooks['hook_entry_count']} |")
        lines.append(f"| Hook Lifecycle Stages | — | — | {hooks['lifecycle_stage_count']} |")
    lines.append("")
    
    # Rules Section
    lines.append("## Rules")
    lines.append("")
    
    # Active rules by trigger
    trigger_groups = {}
    for rule in active_rules:
        trigger = rule["trigger"]
        if trigger not in trigger_groups:
            trigger_groups[trigger] = []
        trigger_groups[trigger].append(rule)
    
    for trigger in sorted(trigger_groups.keys()):
        lines.append(f"### {trigger.replace('_', ' ').title()}")
        lines.append("")
        lines.append("| File | Name | Description |")
        lines.append("|------|------|-------------|")
        for rule in sorted(trigger_groups[trigger], key=lambda x: x["filename"]):
            desc = rule["description"][:60] + "..." if len(rule["description"]) > 60 else rule["description"]
            lines.append(f"| `{rule['filename']}` | {rule['title']} | {desc} |")
        lines.append("")
    
    # Deprecated rules
    if deprecated_rules:
        lines.append("### Deprecated / Redirected")
        lines.append("")
        lines.append("| File | Status | Redirect Target |")
        lines.append("|------|--------|-----------------|")
        for rule in sorted(deprecated_rules, key=lambda x: x["filename"]):
            status = "Deprecated" if rule["deprecated"] else "Redirect"
            target = rule["redirect_to"] or "—"
            lines.append(f"| `{rule['filename']}` | {status} | {target} |")
        lines.append("")
    
    # Skills Section
    lines.append("## Skills")
    lines.append("")
    
    # Active skills
    active_skills_sorted = sorted(active_skills, key=lambda x: x["name"])
    if active_skills_sorted:
        lines.append("### Active Skills")
        lines.append("")
        lines.append("| Skill | Files | Structure | Description |")
        lines.append("|-------|-------|-----------|-------------|")
        for skill in active_skills_sorted:
            structure = []
            if skill["has_checklist"]:
                structure.append("checklist")
            if skill["has_procedure"]:
                structure.append("procedure")
            if skill["has_examples"]:
                structure.append("examples")
            if skill["has_decision_tree"]:
                structure.append("decision-tree")
            struct_str = ", ".join(structure) if structure else "SKILL.md only"
            desc = skill["description"][:50] + "..." if len(skill["description"]) > 50 else skill["description"]
            lines.append(f"| `{skill['name']}` | {skill['file_count']} | {struct_str} | {desc} |")
        lines.append("")
    
    # Deprecated skill stubs
    if deprecated_skills:
        lines.append("### Deprecated / Redirect Stubs")
        lines.append("")
        lines.append("| Skill | Redirect Target | Notice Valid |")
        lines.append("|-------|-----------------|--------------|")
        for skill in sorted(deprecated_skills, key=lambda x: x["name"]):
            notice_status = "✅" if skill["has_deprecation_notice"] else "❌"
            lines.append(f"| `{skill['name']}` | `{skill['redirect_to']}` | {notice_status} |")
        lines.append("")
    
    # Workflows Section
    if workflows:
        lines.append("## Workflows")
        lines.append("")
        lines.append("| File | Name | Trigger | Description |")
        lines.append("|------|------|---------|-------------|")
        for wf in sorted(workflows, key=lambda x: x["filename"]):
            desc = wf["description"][:50] + "..." if len(wf["description"]) > 50 else wf["description"]
            lines.append(f"| `{wf['filename']}` | {wf['title']} | {wf['trigger']} | {desc} |")
        lines.append("")
    
    # Hooks Section
    if hooks:
        lines.append("## Hooks")
        lines.append("")
        lines.append(f"**Total Hook Entries**: {hooks['hook_entry_count']}")
        lines.append(f"**Lifecycle Stages**: {hooks['lifecycle_stage_count']}")
        lines.append("")
        
        if hooks["lifecycle_counts"]:
            lines.append("### By Lifecycle Stage")
            lines.append("")
            lines.append("| Stage | Hook Entries |")
            lines.append("|-------|---------------|")
            for stage, count in sorted(hooks["lifecycle_counts"].items()):
                lines.append(f"| {stage} | {count} |")
            lines.append("")
        
        lines.append("### Hook Metadata")
        lines.append("")
        lines.append(f"| Metric | Count |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Survivor Hooks | {hooks['survivor_count']} |")
        lines.append(f"| Replacement Mappings | {hooks['replacement_count']} |")
        lines.append(f"| Deprecated/Shim Hooks | {hooks['deprecated_or_shim_count']} |")
        lines.append("")
    
    # Consolidation Summary
    lines.append("## Consolidation Summary (W3/W4)")
    lines.append("")
    lines.append("### W3 Rule Consolidation")
    lines.append(f"- Pre-W3: Multiple overlapping rules")
    lines.append(f"- Post-W3: {len([r for r in rules if not r['deprecated']])} consolidated rules")
    lines.append("- Key: Constitutional, Global Rules, Author-Gate, ADG Analysis, Plan Lifecycle")
    lines.append("")
    
    lines.append("### W4 Skill Consolidation")
    lines.append(f"- Pre-W4: 13 individual MCP guide skills")
    lines.append(f"- Post-W4: 1 canonical `mcp-integration` + 13 redirect stubs")
    lines.append(f"- Exclusions preserved: `adg-sqlite`, `ledger-consulter`, `ledger-consulter-ask-user-question`")
    lines.append("")
    
    # Redirect/Stubs Summary
    lines.append("## Redirect / Stub Summary")
    lines.append("")
    
    all_deprecated = deprecated_rules + deprecated_skills
    if all_deprecated:
        lines.append("| Item | Type | Redirect Target |")
        lines.append("|------|------|-----------------|")
        for item in deprecated_rules:
            lines.append(f"| `{item['filename']}` | Rule | {item['redirect_to'] or '—'} |")
        for item in sorted(deprecated_skills, key=lambda x: x["name"]):
            lines.append(f"| `{item['name']}` | Skill | `{item['redirect_to']}` |")
        lines.append("")
    else:
        lines.append("No deprecated items.")
        lines.append("")
    
    # Generated Metadata
    lines.append("## Generated Metadata")
    lines.append("")
    lines.append("```json")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "generator_version": "W5.P1-1.0",
        "source_paths": {
            "rules": str(RULES_DIR.relative_to(REPO_ROOT)),
            "skills": str(SKILLS_DIR.relative_to(REPO_ROOT)),
            "workflows": str(WORKFLOWS_DIR.relative_to(REPO_ROOT)),
            "hooks": str(HOOKS_JSON.relative_to(REPO_ROOT)),
        },
        "counts": {
            "rules": len(rules),
            "skills": len(skills),
            "workflows": len(workflows),
            "hook_entries": hooks["hook_entry_count"] if hooks else 0,
            "hook_lifecycle_stages": hooks["lifecycle_stage_count"] if hooks else 0,
        },
    }
    lines.append(json.dumps(metadata, indent=2))
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate RULES_INDEX.md from Cursor governance sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --dry-run              # Print generated index (default)
    %(prog)s --check                # Compare to RULES_INDEX.md, exit nonzero on drift
    %(prog)s --write                # Update RULES_INDEX.md (destructive)
    %(prog)s --artifact PATH        # Write generated output to specific path
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", default=True,
                          help="Print generated index or write to temp artifact (default)")
    mode_group.add_argument("--check", action="store_true",
                          help="Compare generated to existing RULES_INDEX.md, exit nonzero on drift")
    mode_group.add_argument("--write", action="store_true",
                          help="Overwrite RULES_INDEX.md with generated content (destructive)")
    
    parser.add_argument("--artifact", type=str, metavar="PATH",
                       help="Write generated output to specific file path")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress non-error output")
    
    args = parser.parse_args()
    
    # If --write or --check specified, they override --dry-run default
    if args.write or args.check:
        args.dry_run = False
    
    # Scan sources
    if not args.quiet:
        print("Scanning sources...", file=sys.stderr)
    
    rules = scan_rules()
    skills = scan_skills()
    workflows = scan_workflows()
    hooks = scan_hooks()
    
    # Generate index
    generated_content = generate_index(rules, skills, workflows, hooks)
    
    if args.write:
        # Destructive write mode
        if not args.quiet:
            print(f"Writing to {RULES_INDEX_PATH}...", file=sys.stderr)
        RULES_INDEX_PATH.write_text(generated_content, encoding="utf-8")
        if not args.quiet:
            print("Done.", file=sys.stderr)
        return 0
    
    elif args.check:
        # Check mode - compare to existing
        if not RULES_INDEX_PATH.exists():
            print(f"ERROR: {RULES_INDEX_PATH} does not exist", file=sys.stderr)
            return 1
        
        existing_content = RULES_INDEX_PATH.read_text(encoding="utf-8")
        
        # Normalize for comparison (remove volatile timestamps; trim trailing WS)
        _generated_at_line = re.compile(r'^\s*"generated_at":\s*"[^"]+",?\s*$')

        def normalize(content: str) -> str:
            lines: list[str] = []
            for line in content.split("\n"):
                if line.startswith("**Generated**:"):
                    continue
                if _generated_at_line.match(line):
                    continue
                lines.append(line.rstrip())
            text = "\n".join(lines).strip()
            return text + "\n" if text else ""
        
        existing_normalized = normalize(existing_content)
        generated_normalized = normalize(generated_content)
        
        if existing_normalized == generated_normalized:
            if not args.quiet:
                print("OK: Generated content matches existing RULES_INDEX.md", file=sys.stderr)
            return 0
        else:
            print("DRIFT: Generated content differs from existing RULES_INDEX.md", file=sys.stderr)
            # Output diff summary
            import difflib
            diff = list(difflib.unified_diff(
                existing_normalized.splitlines(keepends=True),
                generated_normalized.splitlines(keepends=True),
                fromfile="existing",
                tofile="generated"
            ))
            print(f"Diff: {len(diff)} lines", file=sys.stderr)
            return 1
    
    else:
        # Dry-run mode (default)
        if args.artifact:
            # Write to artifact
            artifact_path = Path(args.artifact)
            artifact_path.write_text(generated_content, encoding="utf-8")
            if not args.quiet:
                print(f"Generated index written to: {artifact_path}", file=sys.stderr)
        else:
            # Print to stdout
            print(generated_content)
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
