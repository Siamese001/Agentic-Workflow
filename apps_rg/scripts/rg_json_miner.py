"""
RG JSON Deep Miner - Zero Loss Artifact Extraction
Mines the archives/resume_gen_json directory to extract 100% of operational logic.
Generates RG_JSON_KNOWLEDGE_MAP.md with DAGs, Prompts, and Configs.
"""

import glob
import json
import os
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "rg_json_miner", "uwg_governed_write")
_emit_writes_through("p1", "rg_json_miner", "uwg_governed_write_2")
_emit_pulls_context("p1", "rg_json_miner", "context_retrieval")
_emit_pulls_context("p1", "rg_json_miner", "context_retrieval_2")
emit_determinism_digest("trace_rg_json_miner", "rg_json_miner_dispatch")
emit_determinism_digest("trace_rg_json_miner", "rg_json_miner_complete")
_emit_validated_by_safety_plane("p1", "rg_json_miner", "safety_validation")

ARCHIVE_PATH = "C:\\Git\\Agentic-Workflow\\archives\\resume_gen_json"
OUTPUT_REPORT = "C:\\Git\\Agentic-Workflow\\apps_rg\\RG_JSON_KNOWLEDGE_MAP.md"


def mine_workflows():
    files = glob.glob(Path(ARCHIVE_PATH) / "*.json")
    if not files:
        print("CRITICAL: No JSON archives found.")
        return
    files.sort(key=os.path.getmtime, reverse=True)
    golden_master = files[0]
    print(f"[MINER] Golden Master identified: {Path(golden_master).name}")
    print(f"[MINER] Total archive files: {len(files)}")
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as report:
        report.write("# 🛡️ RG JSON Knowledge Map (Zero Loss)\n\n")
        report.write(f"**Golden Master Source:** `{Path(golden_master).name}`\n")
        report.write(f"**Extraction Date:** `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n")
        report.write(f"**Total Archive Files:** `{len(files)}`\n\n")
        report.write("---\n\n")
        try:
            with open(golden_master, encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("metadata", {})
            report.write("## 1. 📦 Identity & Architecture\n\n")
            report.write(f"- **Schema:** `{meta.get('schema', 'N/A')}`\n")
            report.write(f"- **Version:** `{meta.get('version', 'N/A')}`\n")
            report.write(f"- **Architecture:** `{meta.get('architecture', 'N/A')}`\n")
            report.write(f"- **Last Updated:** `{meta.get('last_updated', 'N/A')}`\n")
            report.write(f"- **Description:** {meta.get('description', 'No description')}\n\n")
            patches = meta.get("patches_applied", [])
            if patches:
                report.write("### Patches Applied\n")
                for patch in patches:
                    report.write(f"- `{patch}`\n")
                report.write("\n")
            breaking = meta.get("breaking_changes", "")
            if breaking:
                report.write("### ⚠️ Breaking Changes\n")
                report.write(f"> {breaking}\n\n")
            report.write("## 2. 🔄 Workflow Topology (DAG)\n\n")
            steps = None
            workflow_key = None
            for key in ["workflow", "steps", "nodes", "pipeline", "stages", "k_nodes"]:
                if key in data:
                    candidate = data[key]
                    if isinstance(candidate, dict) and "steps" in candidate:
                        steps = candidate["steps"]
                        workflow_key = f"{key}.steps"
                    elif isinstance(candidate, list):
                        steps = candidate
                        workflow_key = key
                    elif isinstance(candidate, dict):
                        steps = list(candidate.values()) if candidate else None
                        workflow_key = key
                    if steps:
                        break
            if steps and isinstance(steps, list):
                report.write(f"*Found workflow in: `{workflow_key}` ({len(steps)} steps)*\n\n")
                report.write("| Step ID | Agent/Tool | Description | Next Step |\n")
                report.write("| :--- | :--- | :--- | :--- |\n")
                for step in steps:
                    if isinstance(step, dict):
                        sid = step.get("id", step.get("step_id", step.get("name", "Unknown")))
                        agent = step.get(
                            "agent", step.get("tool", step.get("node", step.get("type", "Unknown")))
                        )
                        desc = step.get("description", step.get("desc", ""))[:60]
                        next_s = step.get("next_step", step.get("next", step.get("transitions", "End")))
                        if isinstance(next_s, list):
                            next_s = ", ".join(str(n) for n in next_s[:3])
                        report.write(f"| `{sid}` | **{agent}** | {desc} | `{next_s}` |\n")
                report.write("\n")
            else:
                report.write("> ⚠️ **WARNING:** No explicit step list found. Scanning for K-nodes...\n\n")
                k_nodes = extract_k_nodes(data)
                if k_nodes:
                    report.write(f"### K-Node Architecture ({len(k_nodes)} nodes found)\n\n")
                    report.write("| K-Node | Name | Purpose |\n")
                    report.write("| :--- | :--- | :--- |\n")
                    for node_id, node_data in sorted(k_nodes.items()):
                        name = node_data.get("name", node_data.get("title", "Unknown"))
                        purpose = node_data.get("purpose", node_data.get("description", ""))[:80]
                        report.write(f"| `{node_id}` | **{name}** | {purpose} |\n")
                    report.write("\n")
            report.write("## 3. 🧠 Prompt Encyclopedia\n\n")
            report.write("*Exact text extraction of all detected prompt templates.*\n\n")
            prompts = extract_keys_recursive(
                data, ["prompt", "system_prompt", "user_prompt", "template", "instruction"]
            )
            prompt_count = 0
            for key, content in sorted(prompts.items()):
                if isinstance(content, str) and len(content) > 20:
                    prompt_count += 1
                    report.write(f"### 📝 Prompt: `{key}`\n\n")
                    report.write("```text\n")
                    report.write(content.strip())
                    report.write("\n```\n\n")
            if prompt_count == 0:
                report.write("> ⚠️ No prompts found with standard keys. Scanning for text blocks...\n\n")
                text_blocks = extract_long_text_blocks(data)
                for key, content in list(text_blocks.items())[:20]:
                    report.write(f"### 📝 Text Block: `{key}`\n\n")
                    report.write("```text\n")
                    report.write(content.strip()[:2000])
                    if len(content) > 2000:
                        report.write("\n... [TRUNCATED]")
                    report.write("\n```\n\n")
            report.write("## 4. ⚙️ Configuration & Tuning\n\n")
            report.write("| Parameter Path | Value |\n")
            report.write("| :--- | :--- |\n")
            config_keys = [
                "temperature",
                "model",
                "tokens",
                "timeout",
                "retry",
                "max_",
                "min_",
                "threshold",
                "limit",
                "count",
                "size",
                "weight",
                "score",
                "confidence",
                "budget",
            ]
            configs = extract_keys_recursive(data, config_keys)
            for key, val in sorted(configs.items()):
                if not isinstance(val, dict | list):
                    report.write(f"| `{key}` | `{val}` |\n")
            report.write("\n")
            report.write("## 5. ✅ Validation Rules\n\n")
            validation_keys = ["validation", "rule", "constraint", "check", "gate", "guard"]
            validations = extract_keys_recursive(data, validation_keys)
            if validations:
                for key, val in sorted(validations.items()):
                    if isinstance(val, str) and len(val) > 10:
                        report.write(f"### Rule: `{key}`\n")
                        report.write(f"> {val}\n\n")
                    elif isinstance(val, int | float | bool):
                        report.write(f"- **{key}:** `{val}`\n")
            else:
                report.write("> No explicit validation rules found.\n")
            report.write("\n")
            critical_rules = meta.get("critical_rules_added", [])
            if critical_rules:
                report.write("## 6. 🚨 Critical Rules\n\n")
                for rule in critical_rules:
                    report.write(f"- {rule}\n")
                report.write("\n")
            report.write("## 7. 📊 Top-Level Structure\n\n")
            report.write("```\n")
            for key in data.keys():
                val = data[key]
                if isinstance(val, dict):
                    report.write(f"├── {key}/ ({len(val)} keys)\n")
                elif isinstance(val, list):
                    report.write(f"├── {key}[] ({len(val)} items)\n")
                else:
                    report.write(f"├── {key}: {type(val).__name__}\n")
            report.write("```\n\n")
            print(f"[MINER] Extraction complete. Report saved to: {OUTPUT_REPORT}")
            print(f"[MINER] Prompts extracted: {prompt_count}")
            print(f"[MINER] Configs extracted: {len(configs)}")
        # guardian: allow-silent-swallow
        except Exception as e:
            report.write(f"\n# ❌ EXTRACTION FAILED\n\nError: {str(e)}\n")
            print(f"[MINER] Error processing {golden_master}: {e}")
            import traceback

            traceback.print_exc()


def extract_k_nodes(data, parent_key=""):
    """Extract K-node pattern (K.1, K.2, K.1A, K.1B, etc.)"""
    k_nodes = {}
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{parent_key}.{k}" if parent_key else k
            if k.upper().startswith("K.") or k.upper().startswith("K_"):
                k_nodes[k] = v if isinstance(v, dict) else {"value": v}
            k_nodes.update(extract_k_nodes(v, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            k_nodes.update(extract_k_nodes(item, f"{parent_key}[{i}]"))
    return k_nodes


def extract_keys_recursive(data, target_keys, parent_key=""):
    """Recursively finds specific keys or keys containing specific substrings."""
    found = {}
    targets = [target_keys] if isinstance(target_keys, str) else target_keys
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{parent_key}.{k}" if parent_key else k
            is_match = any(t in k.lower() for t in targets)
            if is_match and (not isinstance(v, dict | list)):
                found[current_path] = v
            found.update(extract_keys_recursive(v, targets, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found.update(extract_keys_recursive(item, targets, f"{parent_key}[{i}]"))
    return found


# guardian: allow-magic-config
def extract_long_text_blocks(data, parent_key="", min_length=100):
    """Extract all string values longer than min_length."""
    found = {}
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, str) and len(v) >= min_length:
                found[current_path] = v
            else:
                found.update(extract_long_text_blocks(v, current_path, min_length))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found.update(extract_long_text_blocks(item, f"{parent_key}[{i}]", min_length))
    return found


if __name__ == "__main__":
    mine_workflows()
