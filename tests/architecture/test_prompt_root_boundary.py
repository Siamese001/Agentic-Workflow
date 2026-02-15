"""Test guard to prevent reintroduction of removed prompt roots."""

import subprocess
import sys
from pathlib import Path


def test_no_nondoc_references_to_removed_prompt_roots():
    """Fail if any NON-DOC files reference data/prompts/ or data/prompt_libraries/."""
    repo_root = Path(__file__).parent.parent.parent

    # Search for references to removed roots, excluding docs and archives
    patterns = ["data/prompts/", "data/prompt_libraries/"]

    all_matches = []

    for pattern in patterns:
        # Use PowerShell on Windows for deterministic search
        if sys.platform == "win32":
            cmd = [
                "powershell",
                "-Command",
                "Get-ChildItem -Recurse | "
                "Where-Object { $_.FullName -notlike '*docs*' -and $_.FullName -notlike '*archives*' -and $_.FullName -notlike '*test*' -and $_.FullName -notlike '*__pycache__*' -and $_.FullName -notlike '*meta_prompts*' -and $_.FullName -notlike '*data/manifests*' -and $_.FullName -notlike '*data/prompt_governance/prompt_injections*' } | "
                f"Select-String -Pattern '{pattern}' | "
                "Select-Object @{Name='Path';Expression={$_.Path.Replace((Get-Location).Path + '\\', '').Replace('\\', '/')}}, LineNumber, Line",
            ]
        else:
            # Use ripgrep on Unix systems
            excluded_dirs = ["docs/**", "archives/**", "tests/**"]
            cmd = ["rg", "-n", pattern, "--type", "text"] + [f"--glob=!{d}" for d in excluded_dirs]

        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)

        if result.stdout.strip():
            matches = result.stdout.strip().split("\n")
            for match in matches:
                if match.strip() and not match.startswith("Path") and not match.startswith("----"):
                    # Filter out any remaining docs references
                    if not any(
                        excl in match
                        for excl in [
                            "docs/",
                            "meta_prompts/",
                            "data/manifests/",
                            "data/prompt_governance/prompt_injections/",
                        ]
                    ):
                        all_matches.append(f"{pattern}: {match}")

    if all_matches:
        # Group by pattern for clearer output
        by_pattern = {}
        for match in all_matches:
            pattern = match.split(":")[0]
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(match)

        error_msg = "Found non-doc references to removed prompt roots:\n"
        for pattern, matches in by_pattern.items():
            error_msg += f"\n{pattern} references:\n"
            for match in matches:
                error_msg += f"  {match.split(':', 1)[1]}\n"

        error_msg += "\nThese references must be removed to maintain SSOT boundary integrity."
        raise AssertionError(error_msg)
