"""
Analyze archives for files that look relevant to apps_rg, apps_lic, or shared territories.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from tqdm import tqdm

RESUME_KEYWORDS = {"resume", "cv", "ats", "job", "skill", "experience", "bullet", "section"}
OUTREACH_KEYWORDS = {"outreach", "linkedin", "recipient", "campaign", "personalization", "message", "sender"}
KNOWN_ARCHIVES: dict[str, str] = {
    "deprecated_2026_01_20": "Today's deprecated files",
    "misplaced_tests_2026_01_20": "Today's misplaced tests",
    "apps_lic": "Previously archived LIC files",
    "apps_rg": "Previously archived RG files",
    "apps_shared": "Previously archived shared files",
    "Reachout Engine Archive": "Legacy outreach engine",
}


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


def analyze_archive(archive_path: Path) -> list[dict]:
    if not archive_path.exists():
        print(f"Error: Path {archive_path} does not exist.")
        return []

    results: list[dict] = []
    for file_path in tqdm(sorted(archive_path.rglob("*.py")), desc="Processing", unit="file"):
        if "__pycache__" in file_path.parts:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace").lower()
        except (OSError, UnicodeDecodeError):
            continue

        has_resume = any(keyword in content for keyword in RESUME_KEYWORDS)
        has_outreach = any(keyword in content for keyword in OUTREACH_KEYWORDS)
        if not (has_resume or has_outreach):
            continue

        tag = "SHARED" if has_resume and has_outreach else "RG" if has_resume else "LIC"
        first_sig_line = ""
        try:
            with file_path.open("r", encoding="utf-8", errors="replace") as handle:
                for _ in range(50):
                    line = handle.readline()
                    if not line:
                        break
                    clean_line = line.strip()
                    if clean_line.startswith(("class ", "def ")):
                        first_sig_line = clean_line[:70]
                        break
        except OSError:
            first_sig_line = ""

        results.append(
            {
                "path": str(file_path.relative_to(archive_path)),
                "tag": tag,
                "first_line": first_sig_line,
                "has_resume": has_resume,
                "has_outreach": has_outreach,
            }
        )
    return results


def discover_subfolders(archives_root: Path) -> list[tuple[str, str]]:
    if not archives_root.exists():
        return []
    return [
        (entry.name, f"Discovered subfolder: {entry.name}")
        for entry in sorted(archives_root.iterdir())
        if entry.is_dir() and not entry.name.startswith(".")
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze archive folders for app-relevant recovery candidates."
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--archives-root", help="Override the default archives directory.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    archives_root = (
        Path(args.archives_root).expanduser().resolve()
        if args.archives_root
        else repo_root / "ops_scripts" / "archives"
    )
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else repo_root / "archive_analysis_candidates.json"
    )

    discovered = discover_subfolders(archives_root)
    archives_to_check: list[tuple[str, str]] = list(KNOWN_ARCHIVES.items())
    known_names = set(KNOWN_ARCHIVES)
    for name, description in discovered:
        if name not in known_names:
            archives_to_check.append((name, description))

    print("=" * 80)
    print("ARCHIVE ANALYSIS - FILES POTENTIALLY RELEVANT TO apps_* FOLDERS")
    print("=" * 80)

    all_restore_candidates: list[dict] = []
    for archive_name, description in tqdm(archives_to_check, desc="Analyzing archives", unit="archive"):
        archive_path = archives_root / archive_name
        if not archive_path.exists():
            continue
        results = analyze_archive(archive_path)
        if not results:
            continue

        print(f"\n## {archive_name} ({description})")
        print(f"   Found {len(results)} app-relevant files")
        print("-" * 60)
        for result in results[:15]:
            print(f"  [{result['tag']}] {result['path']}")
            if result["first_line"]:
                print(f"       -> {result['first_line']}")
        if len(results) > 15:
            print(f"  ... and {len(results) - 15} more files")

        all_restore_candidates.extend([{"archive": archive_name, **result} for result in results])

    print("\n" + "=" * 80)
    print("RESTORE RECOMMENDATIONS SUMMARY")
    print("=" * 80)
    rg_count = sum(1 for item in all_restore_candidates if item["tag"] == "RG")
    lic_count = sum(1 for item in all_restore_candidates if item["tag"] == "LIC")
    shared_count = sum(1 for item in all_restore_candidates if item["tag"] == "SHARED")
    print(f"\nTotal app-relevant files in archives: {len(all_restore_candidates)}")
    print(f"  - Resume Engine (RG):     {rg_count} files")
    print(f"  - Outreach Engine (LIC):  {lic_count} files")
    print(f"  - Shared (both):          {shared_count} files")

    _atomic_write(output_path, json.dumps(all_restore_candidates, indent=2) + "\n")
    print(f"\n💾 Candidate list saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
