"""Validate the governed Codex rule and hook surface without writing artifacts.

The manifest assigns every discovered rule and hook an owner, scope, load mode,
enforcement mode, lifecycle, and canonical source. It also classifies legacy
platform references so compatibility evidence cannot be mistaken for active
Codex policy.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_RELATIVE = Path(".codex/governance/governance_surface_manifest.json")
REQUIRED_FIELDS = frozenset(
    {"owner", "scope", "load_mode", "enforcement_mode", "lifecycle", "canonical_source"}
)
_HOOK_PATH_RE = re.compile(r"\.codex/hooks/([A-Za-z0-9_.-]+\.py)")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _surface_names(root: Path) -> tuple[list[str], list[str], set[str]]:
    rules = sorted(path.name for path in (root / ".codex/rules").glob("*.md"))
    hooks = sorted(path.name for path in (root / ".codex/hooks").glob("*.py"))
    hooks_config = _read_json(root / ".codex/hooks.json")
    registered: set[str] = set()
    for groups in (hooks_config.get("hooks") or {}).values():
        for group in groups or []:
            for hook in group.get("hooks") or []:
                match = _HOOK_PATH_RE.search(str(hook.get("command") or ""))
                if match:
                    registered.add(match.group(1))
    return rules, hooks, registered


def _resolved_metadata(
    name: str,
    *,
    defaults: dict[str, Any],
    overrides: dict[str, Any],
    relative_path: str,
) -> dict[str, Any]:
    item = dict(defaults)
    override = overrides.get(name, {})
    if isinstance(override, dict):
        item.update(override)
    if item.get("canonical_source") == "self":
        item["canonical_source"] = relative_path
    return item


def _canonical_source_failure(root: Path, item: dict[str, Any], *, kind: str, name: str) -> str | None:
    canonical_source = item.get("canonical_source")
    if not isinstance(canonical_source, str) or not canonical_source:
        return f"{kind} {name} has invalid canonical_source"
    canonical_path = Path(canonical_source)
    if canonical_path.is_absolute() or ".." in canonical_path.parts:
        return f"{kind} {name} canonical_source must be a repo-relative path: {canonical_source}"
    if not (root / canonical_path).is_file():
        return f"{kind} {name} canonical_source missing: {canonical_source}"
    return None


def _classify_legacy_references(root: Path, policy: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    terms = [str(term) for term in policy.get("legacy_terms", [])]
    if not terms:
        return {}, ["legacy_reference_policy.legacy_terms must not be empty"]
    pattern = re.compile(r"(?i)\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b")
    compatibility_prefixes = tuple(str(value).replace("\\", "/") for value in policy.get("compatibility_prefixes", []))
    historical_prefixes = tuple(str(value).replace("\\", "/") for value in policy.get("historical_prefixes", []))
    remediation_paths = {str(value).replace("\\", "/") for value in policy.get("remediation_required_paths", [])}
    classifications = {"compatibility_only": 0, "historical": 0, "remediation_required": 0}
    errors: list[str] = []

    for scan_root in policy.get("scan_roots", []):
        directory = root / str(scan_root)
        if not directory.is_dir():
            errors.append(f"legacy scan root missing: {scan_root}")
            continue
        for path in directory.rglob("*"):
            if not path.is_file() or path.name == MANIFEST_RELATIVE.name:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            matches = len(pattern.findall(text))
            if not matches:
                continue
            relative = path.relative_to(root).as_posix()
            if relative.startswith(historical_prefixes):
                classifications["historical"] += matches
            elif relative.startswith(compatibility_prefixes):
                classifications["compatibility_only"] += matches
            elif relative in remediation_paths:
                classifications["remediation_required"] += matches
            else:
                errors.append(f"unclassified legacy reference: {relative} ({matches} match(es))")
    return classifications, errors


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / MANIFEST_RELATIVE
    try:
        manifest = _read_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "rules": [], "hooks": [], "legacy_references": {}}

    if manifest.get("schema_version") != "codex-governance-surface/v1":
        errors.append("unsupported or missing schema_version")
    rule_defaults = manifest.get("rule_defaults")
    hook_defaults = manifest.get("hook_defaults")
    rule_overrides = manifest.get("rule_overrides", {})
    hook_overrides = manifest.get("hook_overrides", {})
    if not isinstance(rule_defaults, dict) or not isinstance(hook_defaults, dict):
        errors.append("rule_defaults and hook_defaults must be objects")
        return {"status": "FAIL", "errors": errors, "rules": [], "hooks": [], "legacy_references": {}}
    if not isinstance(rule_overrides, dict) or not isinstance(hook_overrides, dict):
        errors.append("rule_overrides and hook_overrides must be objects")
        return {"status": "FAIL", "errors": errors, "rules": [], "hooks": [], "legacy_references": {}}

    try:
        rules, hooks, registered = _surface_names(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "rules": [], "hooks": [], "legacy_references": {}}

    for name in sorted(set(rule_overrides) - set(rules)):
        errors.append(f"rule override has no matching file: {name}")
    for name in sorted(set(hook_overrides) - set(hooks)):
        errors.append(f"hook override has no matching file: {name}")

    resolved_rules: list[dict[str, Any]] = []
    for name in rules:
        item = _resolved_metadata(
            name,
            defaults=rule_defaults,
            overrides=rule_overrides,
            relative_path=f".codex/rules/{name}",
        )
        missing = sorted(field for field in REQUIRED_FIELDS if not isinstance(item.get(field), str) or not item[field])
        if missing:
            errors.append(f"rule {name} missing metadata: {', '.join(missing)}")
        canonical_failure = _canonical_source_failure(root, item, kind="rule", name=name)
        if canonical_failure:
            errors.append(canonical_failure)
        if item.get("load_mode") != "always_on":
            errors.append(f"rule {name} must be always_on, got {item.get('load_mode')!r}")
        resolved_rules.append({"path": f".codex/rules/{name}", **item})

    resolved_hooks: list[dict[str, Any]] = []
    for name in hooks:
        item = _resolved_metadata(
            name,
            defaults=hook_defaults,
            overrides=hook_overrides,
            relative_path=f".codex/hooks/{name}",
        )
        missing = sorted(field for field in REQUIRED_FIELDS if not isinstance(item.get(field), str) or not item[field])
        if missing:
            errors.append(f"hook {name} missing metadata: {', '.join(missing)}")
        canonical_failure = _canonical_source_failure(root, item, kind="hook", name=name)
        if canonical_failure:
            errors.append(canonical_failure)
        if name in registered and item.get("lifecycle") != "active":
            errors.append(f"registered hook {name} must be active, got {item.get('lifecycle')!r}")
        if name not in registered and item.get("lifecycle") not in {"manual_utility", "delegated"}:
            errors.append(f"unregistered hook {name} needs manual_utility or delegated lifecycle")
        resolved_hooks.append({"path": f".codex/hooks/{name}", "registered": name in registered, **item})

    policy = manifest.get("legacy_reference_policy")
    if not isinstance(policy, dict):
        errors.append("legacy_reference_policy must be an object")
        legacy_references: dict[str, int] = {}
    else:
        legacy_references, policy_errors = _classify_legacy_references(root, policy)
        errors.extend(policy_errors)

    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "rules": resolved_rules,
        "hooks": resolved_hooks,
        "legacy_references": legacy_references,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to validate")
    parser.add_argument("--json", action="store_true", help="Emit the resolved surface inventory as JSON")
    args = parser.parse_args(argv)
    result = validate(args.root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"governance-surface-manifest: {result['status']}")
        print(f"- rules: {len(result['rules'])}; hooks: {len(result['hooks'])}")
        print(f"- legacy references: {result['legacy_references']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
