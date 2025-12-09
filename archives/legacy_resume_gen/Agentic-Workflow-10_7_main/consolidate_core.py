import hashlib
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent
EXTRACT_DIR = REPO_ROOT / "_latest_extract"
CONSOLIDATED_DIR = REPO_ROOT / "consolidated_v10_7_Chat_GPT"

WHITELIST_FILENAMES = {
    "models.py",
    "state_adapter_stack.py",
    "context.py",
    "config.py",
    "constants.py",
    "exceptions.py",
    "services.py",
    "clients.py",
    "resilience.py",
    "robustness_stack.py",
    "agents.py",
}

WHITELIST_PREFIXES = [
    "telemetry",  # telemetry*.py
    "agent_orchestration_v",
    "rag_orchestration",
    "draft_orchestration",
    "main_v",
    "run_batch_v",
    "run_learning_v",
]

STACK_DIR_WHITELIST = {"stacks_v10_8", "stacks_v10_7", "stacks_common"}
EXCLUDED_DIRS = {".git", "tests", "tests_flat", "notebooks", "examples", "tmp", "old", "backup", "venv", "__pycache__"}

VERSION_PRIORITY = {"10_8": 2, "10_7": 1, None: 0}

BUCKET_ORDER = [
    "l1_cognition_runtime",
    "l2_action_runtime",
    "l3_orchestration_runtime",
    "l4_state_runtime",
    "l5_policy_safety_runtime",
    "rag_stack",
    "draft_stack",
    "bullet_stack",
    "safety_stack",
    "policy_stack",
    "orchestration_entrypoints",
    "shared_runtime_utils",
    "shared_models_and_schemas",
]

MAX_FILES = 20


def is_whitelisted(path: Path, rel_parts: List[str]) -> bool:
    name = path.name
    if any(part in STACK_DIR_WHITELIST for part in rel_parts):
        return name.endswith(".py")
    if name in WHITELIST_FILENAMES:
        return True
    for prefix in WHITELIST_PREFIXES:
        if name.startswith(prefix) and name.endswith(".py"):
            return True
    return False


def determine_version(rel_path: str) -> str:
    if "10_8" in rel_path:
        return "10_8"
    if "10_7" in rel_path:
        return "10_7"
    return None


def normalize_key(rel_path: Path) -> str:
    parts = []
    for part in rel_path.parts:
        part_clean = re.sub(r"10_[78]", "", part)
        part_clean = part_clean.replace("__", "_").strip("_")
        parts.append(part_clean)
    normalized = Path(*parts)
    return str(normalized)


def collect_candidates() -> Dict[str, Tuple[str, Path]]:
    candidates: Dict[str, Tuple[str, Path]] = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".") and d not in {EXTRACT_DIR.name, CONSOLIDATED_DIR.name}]
        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(REPO_ROOT)
            rel_parts = rel_path.parts
            rel_str = str(rel_path)
            version = determine_version(rel_str)
            if version is None and not any(part in STACK_DIR_WHITELIST for part in rel_parts):
                continue
            if not is_whitelisted(path, list(rel_parts)):
                continue
            key = normalize_key(rel_path)
            current = candidates.get(key)
            if current is None or VERSION_PRIORITY[version] > VERSION_PRIORITY[current[0]]:
                candidates[key] = (version, path)
    return candidates


def safe_copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def extract_files() -> Dict[str, Path]:
    if not EXTRACT_DIR.exists():
        EXTRACT_DIR.mkdir(parents=True)
    mapping: Dict[str, Path] = {}
    candidates = collect_candidates()
    for key, (version, src_path) in candidates.items():
        dest_path = EXTRACT_DIR / key
        safe_copy(src_path, dest_path)
        mapping[key] = dest_path
    return mapping


def sha256_for_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def assign_bucket(rel_path: Path) -> str:
    name = rel_path.name.lower()
    path_str = str(rel_path).lower()
    if "rag" in name or "rag" in path_str:
        return "rag_stack"
    if "draft" in name or "draft" in path_str:
        return "draft_stack"
    if "bullet" in name or "bullet" in path_str:
        return "bullet_stack"
    if "policy" in name or "policy" in path_str:
        return "policy_stack"
    if "safety" in name or "robust" in name or "resilience" in name:
        return "safety_stack"
    if any(k in name for k in ["state_adapter", "state"]):
        return "l4_state_runtime"
    if any(k in name for k in ["agent_orchestration", "rag_orchestration", "draft_orchestration", "main_v", "run_batch", "run_learning"]):
        return "orchestration_entrypoints"
    if name in {"models.py"}:
        return "shared_models_and_schemas"
    if name in {"config.py", "constants.py", "context.py", "exceptions.py", "telemetry.py", "telemetry_v10_7.py"} or name.startswith("telemetry"):
        return "l1_cognition_runtime"
    if name in {"services.py", "clients.py", "agents.py"}:
        return "l2_action_runtime"
    if "orchestration" in name:
        return "l3_orchestration_runtime"
    if name in {"resilience.py", "robustness_stack.py"}:
        return "l5_policy_safety_runtime"
    return "shared_runtime_utils"


def merge_sources(bucket: str, sources: List[Tuple[Path, str]]) -> None:
    output_path = CONSOLIDATED_DIR / f"{bucket}.py" if not bucket.endswith(".py") else CONSOLIDATED_DIR / bucket
    timestamp = datetime.utcnow().isoformat() + "Z"
    header_lines = [
        "# === CONSOLIDATED FILE ===",
        f"# TIMESTAMP: {timestamp}",
        f"# TARGET: {output_path.name}",
        "# SOURCE FILES:",
    ]
    for src_path, src_sha in sources:
        header_lines.append(f"# - {src_path} | SHA256: {src_sha}")
    header_lines.append("# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN")
    header_lines.append("\n")

    content_blocks = ["\n".join(header_lines)]
    seen_names = set()
    src_index = 0
    for src_path, src_sha in sources:
        src_index += 1
        content_blocks.append(f"# ==== BEGIN SOURCE: {src_path} (sha256={src_sha}) ====")
        with src_path.open("r", encoding="utf-8", errors="ignore") as f:
            adjusted_lines = []
            for line in f.readlines():
                match = re.match(r"^(\s*)(def|class)\s+(\w+)", line)
                if match:
                    indent, kind, name = match.groups()
                    new_name = name
                    if name in seen_names:
                        new_name = f"{name}__src{src_index}"
                        line = f"{indent}{kind} {new_name}{line[match.end():]}"
                    seen_names.add(new_name)
                adjusted_lines.append(line.rstrip("\n"))
            content_blocks.append("\n".join(adjusted_lines))
        content_blocks.append(f"# ==== END SOURCE: {src_path} ====")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(content_blocks) + "\n")


def consolidate(mapping: Dict[str, Path]) -> Dict[str, List[str]]:
    bucket_map: Dict[str, List[Tuple[Path, str]]] = {bucket: [] for bucket in BUCKET_ORDER}
    overflow_buckets: List[str] = []
    for key, path in sorted(mapping.items()):
        bucket = assign_bucket(Path(key))
        if bucket not in bucket_map:
            if len(bucket_map) + len(overflow_buckets) < MAX_FILES:
                overflow_name = f"extra_stack_group_{len(overflow_buckets)+1:02d}.py"
                bucket_map[overflow_name] = []
                overflow_buckets.append(overflow_name)
                bucket = overflow_name
            else:
                bucket = overflow_buckets[-1] if overflow_buckets else BUCKET_ORDER[-1]
        bucket_map.setdefault(bucket, [])
        bucket_map[bucket].append((path, sha256_for_file(path)))

    manifest_data: Dict[str, List[str]] = {}
    for bucket, sources in bucket_map.items():
        if not bucket.endswith(".py"):
            filename = f"{bucket}.py"
        else:
            filename = bucket
        manifest_data[filename] = [str(src[0]) for src in sources]
        merge_sources(bucket, sources)
    return manifest_data


def write_manifest(manifest_data: Dict[str, List[str]]) -> None:
    manifest_path = CONSOLIDATED_DIR / "MANIFEST.md"
    header = "| Final File | L-Layer | Source Files | Superseded? | Merge Rule |\n|---|---|---|---|---|\n"
    lines = [header]
    for final_file, sources in sorted(manifest_data.items()):
        if final_file.startswith("l1"):
            layer = "L1"
        elif final_file.startswith("l2"):
            layer = "L2"
        elif final_file.startswith("l3"):
            layer = "L3"
        elif final_file.startswith("l4"):
            layer = "L4"
        elif final_file.startswith("l5"):
            layer = "L5"
        else:
            layer = "stack"
        superseded = "10_8 overrides 10_7" if sources else "N/A"
        merge_rule = "Concatenated with collision suffix __srcN"
        src_list = "<br>".join(sources) if sources else "(none)"
        lines.append(f"| {final_file} | {layer} | {src_list} | {superseded} | {merge_rule} |\n")
    manifest_path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    extracted = extract_files()
    manifest_data = consolidate(extracted)
    write_manifest(manifest_data)


if __name__ == "__main__":
    main()
