#!/usr/bin/env python3
"""
Deterministic call-site mapping for discovered symbols.

Maps each discovered symbol to:
- Definition locations (from inventory)
- Reference locations (via ripgrep or Python scan)

Output: deterministic JSON with sorted ordering.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SCANNED_ROOTS = [
    "agentic_core",
    "tools",
    "ops_scripts",
]

EXCLUDED_ROOTS = {
    "tests",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "archives",
    ".backup",
}


def should_scan_path(path: Path, repo_root: Path) -> bool:
    """Check if path should be scanned."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return False

    parts = rel.parts
    if not parts:
        return False

    if parts[0] not in SCANNED_ROOTS:
        return False

    for excluded in EXCLUDED_ROOTS:
        if excluded in parts:
            return False

    return True


def load_inventory(inventory_path: Path) -> dict[str, Any]:
    """Load the inventory JSON."""
    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


RG_TIMEOUT_SECONDS = int(os.environ.get("AST_FUZZY_RG_TIMEOUT", "10"))


def find_references_ripgrep(symbol: str, repo_root: Path) -> list[tuple[str, int, str]]:
    """Find references using ripgrep with word boundary."""
    try:
        # Use ripgrep with word boundary and context
        cmd = [
            "rg",
            f"\\b{re.escape(symbol)}\\b",
            "--line-number",
            "--no-heading",
            "--max-count=1000",
            str(repo_root),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=RG_TIMEOUT_SECONDS)
        references = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            # Parse: path:line:content
            parts = line.split(":", 2)
            if len(parts) >= 3:
                try:
                    file_path = parts[0]
                    line_num = int(parts[1])
                    content = parts[2].strip()

                    # Normalize path
                    try:
                        rel_path = Path(file_path).relative_to(repo_root)
                        file_path = str(rel_path).replace("\\", "/")
                    except ValueError:
                        file_path = file_path.replace("\\", "/")

                    # Filter by scanned roots
                    if should_scan_path(Path(file_path), repo_root):
                        references.append((file_path, line_num, content[:100]))
                except (ValueError, IndexError):
                    pass

        return references

    except subprocess.TimeoutExpired:
        return []
    except FileNotFoundError:
        return []


def find_references_python(symbol: str, repo_root: Path) -> list[tuple[str, int, str]]:
    """Find references using Python file scanning (fallback)."""
    references = []
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")

    for root_dir in SCANNED_ROOTS:
        root_path = repo_root / root_dir
        if not root_path.exists():
            continue

        for py_file in root_path.rglob("*.py"):
            if not should_scan_path(py_file, repo_root):
                continue

            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                for line_num, line in enumerate(source.split("\n"), 1):
                    if pattern.search(line):
                        rel_path = str(py_file.relative_to(repo_root)).replace("\\", "/")
                        references.append((rel_path, line_num, line.strip()[:100]))
            except (UnicodeDecodeError, OSError):
                pass

    return references


def build_callsite_map(inventory: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Build call-site map for all discovered symbols."""
    symbols = {}

    # Extract all unique symbols
    for file_entry in inventory["files"]:
        for candidate in file_entry["candidates"]:
            name = candidate["name"]
            if name not in symbols:
                symbols[name] = {"definitions": [], "references": []}

            symbols[name]["definitions"].append(
                {"path": file_entry["path"], "line": candidate["line"], "kind": candidate["kind"]}
            )

    print(f"Found {len(symbols)} unique symbols")

    # Find references for each symbol
    for i, (symbol, data) in enumerate(sorted(symbols.items())):
        if i % 50 == 0:
            print(f"Processing symbol {i + 1}/{len(symbols)}: {symbol}")

        # Try ripgrep first, fall back to Python
        references = find_references_ripgrep(symbol, repo_root)
        if not references:
            references = find_references_python(symbol, repo_root)

        # Deduplicate and sort
        unique_refs = {}
        for path, line, content in references:
            key = (path, line)
            if key not in unique_refs:
                unique_refs[key] = content

        data["references"] = [
            {"path": path, "line": line, "snippet": content}
            for (path, line), content in sorted(unique_refs.items())
        ]

    return symbols


def main():
    """Main entry point."""
    repo_root = Path.cwd()
    inventory_path = repo_root / "docs" / "reports" / "sub" / "ast_fuzzy_inventory.json"

    if not inventory_path.exists():
        print(f"Error: {inventory_path} not found")
        return 1

    print("Loading inventory...")
    inventory = load_inventory(inventory_path)

    print("Building call-site map...")
    callsite_map = build_callsite_map(inventory, repo_root)

    # Build output with sorted keys
    output = {
        symbol: {
            "definitions": sorted(data["definitions"], key=lambda x: (x["path"], x["line"])),
            "references": sorted(data["references"], key=lambda x: (x["path"], x["line"])),
            "inbound_ref_count": len(data["references"]),
        }
        for symbol, data in sorted(callsite_map.items())
    }

    # Write output
    output_path = repo_root / "docs" / "reports" / "sub" / "ast_fuzzy_callsites.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Output written to: {output_path}")
    print(f"SHA256: {_file_sha256(output_path)}")

    # Print statistics
    total_symbols = len(output)
    total_refs = sum(v["inbound_ref_count"] for v in output.values())

    print("\nStatistics:")
    print(f"Total symbols: {total_symbols}")
    print(f"Total inbound references: {total_refs}")

    # Top 20 symbols by inbound ref count
    top_20 = sorted([(k, v["inbound_ref_count"]) for k, v in output.items()], key=lambda x: -x[1])[:20]

    print("\nTop 20 symbols by inbound reference count:")
    for symbol, count in top_20:
        print(f"  {symbol}: {count}")

    return 0


def _file_sha256(path: Path) -> str:
    """Compute SHA256 of file."""
    import hashlib

    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


if __name__ == "__main__":
    exit(main())
