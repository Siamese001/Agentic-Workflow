"""Post-setup-worktree hook: bootstrap a new Windsurf worktree environment.

Triggered by hooks.json post_setup_worktree when a new worktree is created.
Stdlib only — no external dependencies.

Exit 0 always (bootstrap failures are advisory, never block worktree creation).

Actions performed:
  1. Copy .env from repo root to worktree root (if it exists and worktree copy is absent).
  2. Verify Python dependencies are importable (sanity check only — does not install).
  3. Emit a checklist of manual steps the user should complete.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parents[2]


def _get_worktree_root(payload: dict) -> Path | None:
    """Extract worktree path from hook payload."""
    worktree_path = payload.get("worktree_path") or payload.get("worktreePath") or payload.get("path")
    if worktree_path:
        return Path(worktree_path)
    return None


def _copy_env(src_root: Path, worktree: Path) -> None:
    """Copy .env from repo root to worktree if absent."""
    src = src_root / ".env"
    dst = worktree / ".env"
    if not src.exists():
        print("[worktree_bootstrap] No .env in repo root — skipping copy.", flush=True)
        return
    if dst.exists():
        print(f"[worktree_bootstrap] .env already exists in worktree: {dst}", flush=True)
        return
    try:
        shutil.copy2(str(src), str(dst))
        print(f"[worktree_bootstrap] Copied .env -> {dst}", flush=True)
    except OSError as exc:
        print(f"[worktree_bootstrap] WARNING: could not copy .env: {exc}", flush=True)


def _verify_core_imports() -> list[str]:
    """Verify critical packages are importable. Returns list of missing packages."""
    missing: list[str] = []
    packages = ["pytest", "redis", "chromadb", "opentelemetry"]
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing


def _print_checklist(worktree: Path | None, missing_packages: list[str]) -> None:
    """Emit the manual bootstrap checklist."""
    print("\n[worktree_bootstrap] === WORKTREE BOOTSTRAP CHECKLIST ===", flush=True)
    if worktree:
        print(f"  Worktree: {worktree}", flush=True)
    print("  [ ] Verify .env is populated with required API keys", flush=True)
    print("  [ ] Run: python tools/generate_full_adg.py  (regenerate ADG for this worktree)", flush=True)
    print("  [ ] Run: python tools/adg/adg_redis_ingest.py --force  (warm Redis cache)", flush=True)
    print("  [ ] Confirm Redis is running: redis-cli ping", flush=True)
    if missing_packages:
        print(
            f"  [!] Missing packages (install before testing): {', '.join(missing_packages)}",
            flush=True,
        )
    print("[worktree_bootstrap] ==========================================\n", flush=True)


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read().strip()
    payload: dict = {}
    if raw:
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                payload = {}
        except json.JSONDecodeError:  # guardian: allow-silent-swallow -- stdin parse: non-fatal, empty payload used
            pass

    worktree = _get_worktree_root(payload)

    if worktree and worktree.exists():
        _copy_env(repo_root, worktree)
    else:
        print(
            "[worktree_bootstrap] No worktree path in payload or path does not exist — skipping .env copy.",
            flush=True,
        )

    missing = _verify_core_imports()
    if missing:
        print(
            f"[worktree_bootstrap] WARNING: missing packages in current env: {', '.join(missing)}",
            flush=True,
        )

    _print_checklist(worktree, missing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
