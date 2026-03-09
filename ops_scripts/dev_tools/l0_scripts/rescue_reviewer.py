from __future__ import annotations

"""
Sovereign Rescue & Review (SRR)
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def _get_redis_sovereign_agent():
    """Lazy load RedisSovereignAgent to avoid L0 → L4 dependency."""
    import importlib

    module = importlib.import_module("agentic_core.L4_state.reasoning.RedisSovereignAgent")
    return module.RedisSovereignAgent


class RescueReviewer:
    """
    Sovereign judge of archived files — eternal purity through hash + semantics.
    """

    def __init__(self, project_root: Path):
        self.root = project_root
        self.archive_path = project_root / "archives/depth_violations"
        self.active_hashes = self._map_active_canon()
        try:
            _RedisCls = _get_redis_sovereign_agent()
            self.redis_gateway = _RedisCls(project_root)
            self.redis = self.redis_gateway.get_client()
            print("   [OK] SRR: Redis decision cache online.")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"   [!] Redis Link Failed: {e}")
            self.redis = None
        # guardian: allow-magic-config
        self.auto_home_threshold = 0.9
        # guardian: allow-magic-config
        self.auto_home_min_signals = 3

    def _map_active_canon(self) -> dict[str, str]:
        """Map every active .py file hash to its current path"""
        hash_map = {}
        targets = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "tests"]
        for folder in targets:
            path = self.root / folder
            if not path.exists():
                continue
            # Phase 6.6: Use ssot_discovery instead of rglob
            from agentic_core.utils.ssot_discovery_validator import get_python_files

            for py_file in get_python_files(path):
                try:
                    f_hash = hashlib.sha256(py_file.read_bytes()).hexdigest()
                    rel_path = str(py_file.relative_to(self.root))
                    hash_map[f_hash] = rel_path
                # guardian: allow-silent-swallow
                except:
                    pass
        print(f"   [OK] SRR: Mapped {len(hash_map)} active files for deduplication")
        return hash_map

    def review_and_heal(self, auto_home: bool = False) -> Any:
        """Reviews the archive and optionally rescues unique logic."""
        if not self.archive_path.exists():
            print("[OK] Archive is empty. Sovereignty is pure.")
            return
        print(f"\n--- SOVEREIGN ARCHIVE REVIEW (Auto-Home: {auto_home}) ---")
        # Phase 6.6: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        from agentic_core.L5_safety.config.structure_blueprint import (
            CANON_SIGNALS,
            DEFAULT_CORE_HEALING_TERRITORY,
        )

        for arch_file in get_python_files(self.archive_path):
            rel: Any = arch_file.relative_to(self.archive_path)
            content: Any = arch_file.read_text(encoding="utf-8", errors="ignore")
            f_hash: Any = hashlib.sha256(content.encode()).hexdigest()
            cache_key: Any = f"srr_decision:{f_hash}"
            if self.redis:
                cached: Any = self.redis.get(cache_key)
                if cached:
                    decision: Any = json.loads(cached)
                    print(f"   [CACHE HIT] {rel} -> {decision['Verdict']}")
                    if decision.get("action") == "moved":
                        continue
            if f_hash in self.active_hashes:
                print(f"[PURGE] {rel} -> REDUNDANT (Exists at: {self.active_hashes[f_hash]})")
                arch_file.unlink()
                continue
            print(f"[RESCUE] {rel} -> UNIQUE logic detected.")
            results: Any = []
            if results and results[0]["score"] >= 0.85:
                match: Any = results[0]
                territory: Any = match["metadata"]["territory"]
                conf: Any = match["score"]
                # Use territory-based healing instead of canon keys
                suggested_territory = DEFAULT_CORE_HEALING_TERRITORY
                sig_count = sum(1 for s in CANON_SIGNALS if s in content.lower())
                print(f"         SUGGESTION: {territory} (Conf: {conf:.2f}) -> {suggested_territory}")
                Verdict: Any = "MANUAL_REVIEW"
                if (
                    auto_home
                    and conf >= self.auto_home_threshold
                    and (sig_count >= self.auto_home_min_signals)
                ):
                    dest: Any = self._execute_rescue(arch_file, territory)
                    Verdict: Any = "RESCUED_AUTO"
                    print(f"         [HEALED] Rescued to -> {dest.relative_to(self.root)}")
                if self.redis:
                    self.redis.set(
                        cache_key,
                        json.dumps(
                            {
                                "Verdict": Verdict,
                                "action": "moved" if Verdict == "RESCUED_AUTO" else "stay",
                            },
                        ),
                        ex=604800,
                    )
            else:
                print("         VERDICT: Unknown logic. Manual review required.")

    def _execute_rescue(self, arch_file, territory):
        target_dir = self.root / territory
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / arch_file.name
        if dest.exists():
            dest = target_dir / f"{arch_file.stem}_rescued{arch_file.suffix}"
        arch_file.rename(dest)
        return dest

    def final_lockdown(self) -> Any:
        """Cleans up empty directories in the archive."""
        for dirpath, dirnames, filenames in os.walk(self.archive_path, topdown=False):
            if not dirnames and (not filenames):
                os.rmdir(dirpath)


if __name__ == "__main__":
    parser: Any = argparse.ArgumentParser(description="Sovereign Rescue & Review - Archive Purity Enforcer")
    parser.add_argument(
        "--auto-home",
        action="store_true",
        help="Automatically rescue high-confidence unique files to their suggested homes",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Project root path (default: current directory)",
    )
    args: Any = parser.parse_args()
    reviewer: Any = RescueReviewer(args.root)
    reviewer.review_and_heal(auto_home=args.auto_home)
    reviewer.final_lockdown()
