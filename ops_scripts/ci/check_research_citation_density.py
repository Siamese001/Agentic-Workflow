"""CI gate: research citation-density floor (plan §P4.4).

Per plan §P4.4 acceptance: enforces ≥ 1 URL citation per 200 rendered
tokens in the latest ``company_research.json`` under
``artifacts/apps_research/runs/<ts>/``. Exits 1 on regression; 0 otherwise.

Usage:
    python ops_scripts/ci/check_research_citation_density.py
    python ops_scripts/ci/check_research_citation_density.py --runs-dir artifacts/apps_research
    python ops_scripts/ci/check_research_citation_density.py --path path/to/company_research.json

Constitutional §31 routing: gate lives under ``ops_scripts/ci/``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MIN_CITATIONS_PER_200_TOKENS: float = 1.0
_REPO_ROOT = Path(__file__).resolve().parents[2]

_WHITESPACE_TOKEN_RE = re.compile(r"\S+")


def _latest_brief(runs_dir: Path) -> Path | None:
    """Find the most recent ``company_research.json`` under ``runs_dir``."""
    if not runs_dir.exists():
        return None
    candidates = sorted(runs_dir.rglob("company_research.json"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _token_count(text: str) -> int:
    """Best-effort token count. Uses tiktoken if available, whitespace fallback otherwise."""
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return len(_WHITESPACE_TOKEN_RE.findall(text))


def _collect_text_and_urls(brief: dict) -> tuple[str, int]:
    """Flatten brief content into rendered text and count distinct URLs."""
    # Render text = all string values concatenated.
    def _walk(node, out: list[str]) -> None:
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, dict):
            for v in node.values():
                _walk(v, out)
        elif isinstance(node, list):
            for v in node:
                _walk(v, out)

    chunks: list[str] = []
    _walk(brief, chunks)
    rendered = " ".join(chunks)

    # URLs — pull from source_register first, then any URL-shaped string elsewhere.
    urls: set[str] = set()
    register = brief.get("source_register") or []
    if isinstance(register, list):
        for entry in register:
            if isinstance(entry, dict):
                url = str(entry.get("url", "") or "")
                if url:
                    urls.add(url)
            elif isinstance(entry, str) and entry.startswith(("http://", "https://")):
                urls.add(entry)
    # Fallback: detect http(s) URLs inline in the rendered text (covers
    # modes that inline their own URLs, e.g., long_form_renderer).
    for match in re.findall(r"https?://\S+", rendered):
        urls.add(match.rstrip(").,"))
    return rendered, len(urls)


def check_density(brief: dict, min_per_200: float = MIN_CITATIONS_PER_200_TOKENS) -> tuple[bool, dict]:
    """Return ``(passed, report_dict)`` for ``brief``.

    A brief passes when ``urls >= ceil(rendered_tokens / 200) * min_per_200``.
    """
    text, url_count = _collect_text_and_urls(brief)
    tokens = _token_count(text)
    # Avoid divide-by-zero; fewer than 200 tokens needs 0 citations floor.
    windows = max(1, tokens // 200)
    required = int(windows * min_per_200)
    passed = url_count >= required
    return passed, {
        "tokens": tokens,
        "urls": url_count,
        "required_urls": required,
        "density_per_200_tokens": round(url_count / windows, 3),
        "min_per_200_tokens": min_per_200,
        "passed": passed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_research_citation_density")
    parser.add_argument(
        "--runs-dir",
        default=str(_REPO_ROOT / "artifacts" / "apps_research"),
        help="Runs root (default: artifacts/apps_research)",
    )
    parser.add_argument("--path", default="", help="Explicit brief path (overrides --runs-dir)")
    parser.add_argument(
        "--min-per-200",
        type=float,
        default=MIN_CITATIONS_PER_200_TOKENS,
        help="Minimum URL citations per 200 rendered tokens (default 1.0)",
    )
    args = parser.parse_args(argv)

    if args.path:
        target = Path(args.path)
    else:
        target = _latest_brief(Path(args.runs_dir))

    if target is None or not target.exists():
        print(
            "[citation-density] no company_research.json found — gate skipped (exit 0)",
            file=sys.stderr,
        )
        return 0

    try:
        brief = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[citation-density] unreadable brief {target}: {exc}", file=sys.stderr)
        return 2

    passed, report = check_density(brief, min_per_200=args.min_per_200)
    report["brief_path"] = str(target)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
