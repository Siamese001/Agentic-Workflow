"""Inventory apps_lic prompt, template, schema, and Exit policy sources.

This is a W0 characterization helper for the apps_lic prompt-slot/X1-X3
SSOT drift plan. It reads files only and emits a deterministic Markdown
baseline with hashes, ownership classification, and drift observations.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


SLOT_RE = re.compile(
    r"\b(?:S0|I0|C0|U0|D0|E0|Y0|R0|M0|H0|N0|A0|L0|C03|SC|RI|X1[A-Z]?|X2|X3|G2[1-8])\b"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text) or {}
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return None


def classify(path: Path, root: Path) -> str:
    r = rel(path, root)
    name = path.name
    if "__pycache__" in r:
        return "ignored_generated_cache"
    if r.startswith("apps_lic/prompt_assembly/templates/"):
        return "renderable_prompt_template"
    if name in {"prompt_bom.yaml", "prompt_registry.yaml"}:
        return "registry_or_bom"
    if name in {"pa_binding.py", "lic_pa_compiler.py"}:
        return "runtime_prompt_assembly"
    if name in {"PromptTemplate.py", "prompts.json"}:
        return "legacy_fence_candidate"
    if "exit" in name.lower() or "validation" in name.lower() or "gate" in name.lower():
        return "exit_or_validation_contract"
    if "schema" in name.lower() or "output" in name.lower() or "whole_message_generation" in name:
        return "output_contract"
    if "recipient" in name.lower() or "archetype" in name.lower() or "message_type" in name.lower():
        return "recipient_or_message_policy"
    if "profile" in name.lower() or "rubric" in name.lower() or "threshold" in name.lower():
        return "profile_or_rubric"
    if r.startswith("agentic_core/"):
        return "core_reference"
    return "supporting_contract"


def candidate_files(root: Path) -> list[Path]:
    explicit = [
        "apps_lic/prompt_assembly/lic_pa_compiler.py",
        "apps_lic/prompt_assembly/prompt_bom.yaml",
        "apps_lic/config/prompt_registry.yaml",
        "apps_lic/config/prompts.json",
        "apps_lic/config/outreach_schema.json",
        "apps_lic/config/exit_rubric.yaml",
        "apps_lic/config/archetype_tone_policy.yaml",
        "apps_lic/config/archetype_tone_table.yaml",
        "apps_lic/runtime/bindings/pa_binding.py",
        "apps_lic/runtime/bindings/exit_binding.py",
        "apps_lic/runtime/bindings/w5_validation_exit_binding.py",
        "apps_lic/types/PromptTemplate.py",
        "apps_lic/types/recipient_archetype_mapping.py",
        "apps_lic/types/recipient_archetype_types.py",
        "apps_lic/types/recipient_policy_profile.py",
        "apps_lic/engines/generation_engine.py",
        "apps_lic/engines/generation_subject_policy.py",
        "apps_lic/engines/validation_exit.py",
        "apps_lic/engines/x1d_judge_policy.py",
        "apps_lic/engines/x1d_judge_feedback_regeneration.py",
        "agentic_core/L2_execution/reasoning/authority_validator.py",
        "agentic_core/L2_execution/reasoning/compiled_artifact.py",
        "agentic_core/L2_execution/reasoning/prompt_messages.py",
    ]
    files: set[Path] = {root / item for item in explicit}
    for pattern in [
        "apps_lic/prompt_assembly/templates/*",
        "apps_lic/config/domain_contract/*",
    ]:
        files.update(p for p in root.glob(pattern) if p.is_file())
    return sorted(p for p in files if p.exists() and p.is_file())


def extract_file_record(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    data = read_structured(path)
    slots = sorted({"X1" if item.startswith("X1") else item for item in SLOT_RE.findall(text)})
    record: dict[str, Any] = {
        "path": rel(path, root),
        "classification": classify(path, root),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "slots_or_exit_terms": slots,
    }
    if isinstance(data, dict):
        record["top_keys"] = sorted(str(k) for k in data.keys())
        if "required_slots" in data:
            record["declared_required_slots"] = data["required_slots"]
        if "optional_slots" in data:
            record["declared_optional_slots"] = data["optional_slots"]
        if "slot_definitions" in data and isinstance(data["slot_definitions"], dict):
            record["declared_slot_definitions"] = sorted(data["slot_definitions"])
        if "templates" in data and isinstance(data["templates"], dict):
            record["declared_templates"] = sorted(data["templates"].keys())
        if "output_contract" in data:
            record["output_contract"] = data["output_contract"]
        if "allowed_exit_dispositions" in data:
            record["allowed_exit_dispositions"] = data["allowed_exit_dispositions"]
        if "exit" in data and isinstance(data["exit"], dict):
            record["allowed_exit_dispositions"] = data["exit"].get("allowed_dispositions")
    return record


def drift_observations(records: list[dict[str, Any]], root: Path) -> list[str]:
    by_path = {r["path"]: r for r in records}
    observations: list[str] = []

    template_paths = sorted(
        r["path"]
        for r in records
        if r["path"].startswith("apps_lic/prompt_assembly/templates/")
    )
    registry = by_path.get("apps_lic/config/prompt_registry.yaml", {})
    declared_templates = set(registry.get("declared_templates", []))
    physical_templates = {Path(p).stem for p in template_paths}
    missing_from_registry = sorted(physical_templates - declared_templates)
    missing_on_disk = sorted(declared_templates - physical_templates)
    if missing_from_registry:
        observations.append(
            "Active template files missing from prompt_registry.yaml: "
            + ", ".join(missing_from_registry)
        )
    if missing_on_disk:
        observations.append(
            "Registry templates missing on disk: " + ", ".join(missing_on_disk)
        )

    bom = by_path.get("apps_lic/prompt_assembly/prompt_bom.yaml", {})
    bom_slots = (
        set(bom.get("declared_required_slots", []))
        | set(bom.get("declared_optional_slots", []))
        | set(bom.get("declared_slot_definitions", []))
    )
    template_slots = sorted(
        {
            slot
            for r in records
            if r["classification"] == "renderable_prompt_template"
            for slot in r["slots_or_exit_terms"]
            if not slot.startswith("G") and not slot.startswith("X")
        }
    )
    extra_template_slots = sorted(set(template_slots) - bom_slots)
    if extra_template_slots:
        observations.append(
            "Template slot terms not declared in prompt_bom.yaml: "
            + ", ".join(extra_template_slots)
        )

    x_terms = sorted(
        {
            slot
            for r in records
            for slot in r["slots_or_exit_terms"]
            if slot in {"X1", "X2", "X3"}
        }
    )
    if x_terms:
        observations.append(
            "X1/X2/X3 terms are present in Exit/runtime files and must remain non-prompt glossary terms: "
            + ", ".join(x_terms)
        )

    legacy = [
        r["path"]
        for r in records
        if r["classification"] == "legacy_fence_candidate"
    ]
    if legacy:
        observations.append("Legacy prompt sources requiring fence decision: " + ", ".join(legacy))

    if not observations:
        observations.append("No W0 drift observations detected.")
    return observations


def render_markdown(root: Path, records: list[dict[str, Any]], adg_note: str) -> str:
    generated = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    observations = drift_observations(records, root)
    counts: dict[str, int] = {}
    for record in records:
        counts[record["classification"]] = counts.get(record["classification"], 0) + 1

    lines: list[str] = [
        "# apps_lic Prompt Slot and X1-X3 W0 Inventory",
        "",
        f"Generated UTC: {generated}",
        f"Apps LIC root: `{root}`",
        "Plan: `plans/apps-lic-prompt-slot-x1x3-ssot-drift-4a9f2c.md`",
        "",
        "## Method",
        "",
        "- Read-only filesystem inventory of prompt, template, schema, recipient policy, runtime PA, and Exit policy sources.",
        "- SHA-256 hashes are computed from current file bytes.",
        "- YAML/JSON files are parsed for declared slots, templates, contracts, and Exit dispositions when available.",
        f"- ADG status: {adg_note}",
        "",
        "## Classification Counts",
        "",
        "| Classification | Files |",
        "|---|---:|",
    ]
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")

    lines.extend(["", "## Drift Observations", ""])
    for item in observations:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Inventory",
            "",
            "| Classification | Path | Slots / Exit Terms | SHA-256 |",
            "|---|---|---|---|",
        ]
    )
    for record in records:
        terms = ", ".join(record["slots_or_exit_terms"]) if record["slots_or_exit_terms"] else "-"
        lines.append(
            f"| {record['classification']} | `{record['path']}` | {terms} | `{record['sha256']}` |"
        )

    lines.extend(["", "## Structured Details", ""])
    for record in records:
        interesting = {
            key: record[key]
            for key in [
                "top_keys",
                "declared_required_slots",
                "declared_optional_slots",
                "declared_slot_definitions",
                "declared_templates",
                "output_contract",
                "allowed_exit_dispositions",
            ]
            if key in record and record[key] is not None
        }
        if not interesting:
            continue
        lines.append(f"### {record['path']}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(interesting, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apps-lic-root",
        default=r"C:\Git\Agentic-Workflow-apps_lic",
        help="Path to the apps_lic worktree.",
    )
    parser.add_argument("--out", help="Optional Markdown output path.")
    parser.add_argument(
        "--adg-note",
        default="not checked",
        help="ADG availability note to embed in the report.",
    )
    args = parser.parse_args()

    root = Path(args.apps_lic_root).resolve()
    if not root.exists():
        raise SystemExit(f"apps_lic root does not exist: {root}")

    records = [extract_file_record(path, root) for path in candidate_files(root)]
    markdown = render_markdown(root, records, args.adg_note)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
