#!/usr/bin/env python3
"""Canonical ingestion pipeline for ChromaDB collections.

Runs each ingest_*.py in dependency order using the same Python interpreter
this script is invoked with, so project dependencies (agentic_core,
chromadb, redis, openai, sentence_transformers) are always available.

Execution order is by dependency:
    1. ingest_code.py    - code_chunks collection (fast, no deps)
    2. ingest_docs.py    - docs collection (markdown under docs/)
    3. ingest_adg.py     - adg_artifacts collection (needs fresh
                           artifacts/adg/adg_indexed_*.sqlite)
    4. ingest_tests.py   - tests + guardrails collections
    5. ingest_traces.py  - traces collection from healing_contexts corpus
    6. ingest_runtime.py - runtime evidence (needs logs/ artifacts)
    7. ingest_history.py - git history / RCA (needs .git)

Optional (needs seed data at data/rag_seeds/*.txt):
    8. ingest_web_to_chroma.py
    9. ingest_web_to_chroma_enhanced.py

Usage:
    python tools/ingestion/pipeline.py                  # core (1-7)
    python tools/ingestion/pipeline.py --with-web       # core + web (1-9)
    python tools/ingestion/pipeline.py --only docs      # single stage
    python tools/ingestion/pipeline.py --dry-run        # print without running

Exit codes:
    0 - all requested stages succeeded
    1 - at least one stage failed (per-stage logs under logs/ingest/)
    2 - invalid arguments
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = REPO_ROOT / "logs" / "ingest"


@dataclass(frozen=True)
class Stage:
    """One ingestion stage with its script, CLI args, and required inputs."""

    name: str
    script: str
    args: tuple[str, ...] = ()
    required_paths: tuple[str, ...] = field(default_factory=tuple)
    required_env: tuple[str, ...] = field(default_factory=tuple)


# Default args per stage — rationale inline. User can override a single
# stage via --only and shell-quote their own flags, but these are the sensible
# batch defaults for running the full pipeline.
CORE_STAGES: tuple[Stage, ...] = (
    Stage(
        name="code",
        script="ingest_code.py",
        args=("--source-dir", "agentic_core"),
    ),
    Stage(
        name="docs",
        script="ingest_docs.py",
        args=("--source-dir", "docs", "--embedding-provider", "bge-m3"),
    ),
    Stage(name="adg", script="ingest_adg.py"),
    Stage(name="tests", script="ingest_tests.py"),
    Stage(
        name="traces",
        script="ingest_traces.py",
        required_paths=("data/corpus/healing_contexts_corpus.jsonl",),
    ),
    Stage(name="runtime", script="ingest_runtime.py"),
    Stage(name="history", script="ingest_history.py"),
)

WEB_STAGES: tuple[Stage, ...] = (
    Stage(
        name="web_to_chroma",
        script="ingest_web_to_chroma.py",
        required_paths=("data/rag_seeds/agentic_best_practices_urls.txt",),
    ),
    Stage(
        name="web_to_chroma_enhanced",
        script="ingest_web_to_chroma_enhanced.py",
        required_paths=("data/rag_seeds/agentic_best_practices_urls.txt",),
    ),
)

ALL_STAGES = {s.name: s for s in (*CORE_STAGES, *WEB_STAGES)}


# ANSI colors — constitutional rule 16 (progress bar + color)
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Env overrides for all subprocess children. These enable BGE-M3 local
# embeddings so ChromaDB ingestion works without an OpenAI key.
SUBPROCESS_ENV_DEFAULTS: dict[str, str] = {
    "EMBEDDING_ENABLED": "true",
    "EMBEDDING_DEVICE": "cuda",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ChromaDB ingestion scripts in dependency order.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--with-web",
        action="store_true",
        help="Include web ingestion stages (web_to_chroma, web_to_chroma_enhanced).",
    )
    parser.add_argument(
        "--only",
        choices=list(ALL_STAGES.keys()),
        help="Run a single stage instead of the full pipeline.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run, without executing them.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        default=True,
        help="(default) Continue running remaining stages after a failure.",
    )
    parser.add_argument(
        "--fail-fast",
        dest="continue_on_failure",
        action="store_false",
        help="Stop at the first stage failure.",
    )
    return parser


def select_stages(args: argparse.Namespace) -> list[Stage]:
    if args.only:
        return [ALL_STAGES[args.only]]
    if args.with_web:
        return list(CORE_STAGES) + list(WEB_STAGES)
    return list(CORE_STAGES)


def preflight_seed_lines(path: Path) -> int:
    """Return the count of non-comment, non-blank lines in a seed file.

    Used to distinguish an empty stub from a populated seed file.
    """
    if not path.is_file():
        return 0
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def run_stage(
    stage: Stage,
    idx: int,
    total: int,
    dry_run: bool,
    env: dict[str, str],
) -> tuple[str, float]:
    """Run one stage. Returns (status, elapsed_seconds).

    status is one of: "ok", "fail", "skip", "timeout".
    """
    pct = int(idx * 100 / total)
    log_file = LOG_DIR / f"{stage.name}.log"
    script_path = REPO_ROOT / "tools" / "ingestion" / stage.script

    header = (
        f"{BLUE}[{idx}/{total}  {pct:3d}%]{RESET} "
        f"stage={stage.name:<25} script={stage.script}"
    )
    print(header, flush=True)

    # Pre-flight: skip if any required input file is missing or an empty stub.
    for rel in stage.required_paths:
        abs_path = REPO_ROOT / rel
        if not abs_path.is_file():
            print(
                f"         {YELLOW}SKIP{RESET} missing required input: {rel}",
                flush=True,
            )
            return "skip", 0.0
        # For seed text files, an "empty" stub = no non-comment lines.
        if abs_path.suffix == ".txt" and preflight_seed_lines(abs_path) == 0:
            print(
                f"         {YELLOW}SKIP{RESET} seed file empty (comments-only): {rel}",
                flush=True,
            )
            return "skip", 0.0

    cmd = [sys.executable, str(script_path), *stage.args]

    if dry_run:
        print(f"         DRY-RUN: {' '.join(cmd)} > {log_file}", flush=True)
        return "ok", 0.0

    started = time.perf_counter()
    try:
        with log_file.open("w", encoding="utf-8") as log:
            result = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                stdout=log,
                stderr=subprocess.STDOUT,
                shell=False,
                check=False,
                env=env,
                timeout=3600,  # 1 hour per stage
            )
        elapsed = time.perf_counter() - started
        if result.returncode == 0:
            print(
                f"         {GREEN}OK{RESET}   elapsed={elapsed:.1f}s  log={log_file}",
                flush=True,
            )
            return "ok", elapsed
        print(
            f"         {RED}FAIL{RESET} rc={result.returncode} "
            f"elapsed={elapsed:.1f}s  log={log_file}",
            flush=True,
        )
        return "fail", elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - started
        print(
            f"         {RED}TIMEOUT{RESET} elapsed={elapsed:.1f}s  log={log_file}",
            flush=True,
        )
        return "timeout", elapsed


def main() -> int:
    args = build_parser().parse_args()
    stages = select_stages(args)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Compose subprocess env: start from parent env, apply defaults unless
    # the user has already set a value in their shell/.env.
    env = os.environ.copy()
    for key, value in SUBPROCESS_ENV_DEFAULTS.items():
        env.setdefault(key, value)

    print(f"Pipeline: {len(stages)} stages, logs -> {LOG_DIR}", flush=True)

    failed: list[str] = []
    skipped: list[str] = []
    total_elapsed = 0.0
    for idx, stage in enumerate(stages, start=1):
        status, elapsed = run_stage(stage, idx, len(stages), args.dry_run, env)
        total_elapsed += elapsed
        if status == "skip":
            skipped.append(stage.name)
        elif status != "ok":
            failed.append(stage.name)
            if not args.continue_on_failure:
                print(f"{RED}--fail-fast: stopping after {stage.name}{RESET}", flush=True)
                break

    print()
    if args.dry_run:
        print(f"{GREEN}DRY-RUN complete.{RESET} {len(stages)} stages planned.")
        return 0
    if failed:
        summary = f"{len(failed)}/{len(stages)} stages FAILED: {', '.join(failed)}"
        if skipped:
            summary += f"  ({len(skipped)} skipped: {', '.join(skipped)})"
        print(f"{RED}{summary}{RESET}")
        print(f"Inspect logs under {LOG_DIR}/")
        return 1
    ran = len(stages) - len(skipped)
    msg = f"All {ran} executed stages succeeded in {total_elapsed:.1f}s total."
    if skipped:
        msg += f"  ({len(skipped)} skipped: {', '.join(skipped)})"
    print(f"{GREEN}{msg}{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
