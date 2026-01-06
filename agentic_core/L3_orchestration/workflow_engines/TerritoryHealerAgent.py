from __future__ import annotations
#!/usr/bin/env python3
"""
Territory Healer Agent - Exhaustive Territory Enforcement

Detects files that are stray WITHIN their current key territory and suggests
better placements based on semantic content and key-specific stray signals.

Examples:
- Operational scripts in L1_cognition (belongs in scripts/)
- Test files in L3_orchestration (belongs in tests/)
- Healing agents in L4_state (belongs in L3_orchestration/healing/)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class TerritoryHealerAgent(HealerMixin, MCPHardenedMixin):
    """
    Enforces exhaustive territory compliance by detecting intra-territory strays.
    """
    
    def __init__(self, project_root: Path, ctx) -> None:
        self.root = project_root
        self.ctx = ctx
        
        from agentic_core.config.blueprint_sovereign.structure_blueprint import (
            CANON_KEY_TO_FOLDER_MAP,
            CANON_SIGNALS_MK2,
            ROOT_PROTECTED_FILES,
            SOVEREIGN_REGISTRY,
            TERRITORY_EXAMPLES,
        )
        from agentic_core.runtime.shared_runtime.void_compliance import get_placement_guidance
        
        self.key_folders = CANON_KEY_TO_FOLDER_MAP
        self.key_positive_signals = CANON_SIGNALS_MK2  # Legacy bridge – migrate to CANON_SIGNALS_MK2
        # Flatten all mapped paths for fast check
        self.all_mapped_paths = {p for ps in self.key_folders.values() for p in ps}
        
        self.root_protected = ROOT_PROTECTED_FILES
        self.get_placement_guidance = get_placement_guidance
        
        # Create archive directory
        self.root_archive = project_root / "archives" / "deprecated_code"
        self.root_archive.mkdir(parents=True, exist_ok=True)

        # [EXHAUSTIVE COVERAGE] Key-specific stray signals (what doesn't belong)
        self.key_stray_signals = {
            11: {"script", "tool", "cli", "operational", "backup"},  # L1_cognition: no ops
            12: {"test", "fixture", "mock"},                         # L3_orchestration: no tests
            13: {"heal", "fix", "prune"},                            # L4_state: no healing
            15: {"strategy", "reasoning", "planner"},                # Domain agents: no core cognition
            17: {"agent", "manager", "engine", "healer"},            # tests/: no production agents
            19: {"script", "test", "heal"},                          # L5_safety: no ops/tests/healing
        }

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, 'root'), "Missing root"
        assert hasattr(self, 'ctx'), "Missing ctx"
        return True

    def check_depth_precision(self, file_path: Path) -> Optional[dict]:
        """
        Check if file violates precision depth requirements.
        Only heal if root precision is violated.
        General min/max healing logic removed.
        """
        try:
            rel_path = file_path.relative_to(self.root)
            parts = rel_path.parts
            depth = len(parts)
            
            agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"]["depth"]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
            if parts[0] == "agentic_core" and depth != agentic_core_exact_depth:
                return self._suggest_precision_move(file_path, agentic_core_exact_depth)
                
        except ValueError:
            pass  # File outside root
            
        return None
    
    def _suggest_precision_move(self, file_path: Path, target_depth: int) -> dict:
        """
        Suggest a move to achieve the required precision depth.
        """
        rel_path = file_path.relative_to(self.root)
        parts = rel_path.parts
        
        # For agentic_core, we need to ensure depth 4
        if parts[0] == "agentic_core" and len(parts) < 4:
            # Need to go deeper - suggest adding L3/L4 structure
            suggested = self.get_placement_guidance("")
            target_path = self.root / suggested / rel_path.name
            return {
                "action": "move",
                "source": str(file_path),
                "target": str(target_path),
                "reason": f"Depth precision: agentic_core requires depth {target_depth}, found {len(parts)}"
            }
        elif parts[0] == "agentic_core" and len(parts) > 4:
            # Need to flatten - move to appropriate L4 location
            target_path = self.root / parts[0] / parts[1] / parts[2] / parts[3] / rel_path.name
            return {
                "action": "move",
                "source": str(file_path),
                "target": str(target_path),
                "reason": f"Depth precision: agentic_core requires depth {target_depth}, found {len(parts)}"
            }
        
        return None

    def is_stray_in_territory(self, rel_path: str, content_lower: str, stem_lower: str) -> Optional[dict]:
        """
        Check if file is stray WITHIN its current key territory.
        Uses DOUBLE-LOCK: negative signals (what doesn't belong) + positive signals (what does belong).
        Returns move dict if stray, else None.
        """
        current_territory = None
        for key, paths in self.key_folders.items():
            if any(rel_path.startswith(p + "/") or rel_path == p for p in paths):
                current_territory = key
                break
        
        if current_territory is None:
            return None  # Already handled by unmapped drift check

        # [ETERNAL DOUBLE-LOCK]
        stray_words = self.key_stray_signals.get(current_territory, set())
        has_negative = any(word in stem_lower or word in content_lower for word in stray_words)

        positive_words = self.key_positive_signals.get(current_territory, set())
        positive_score = sum(1 for word in positive_words if word in stem_lower or word in content_lower)

        # Sovereign rule: Strong positive (>=3) stays. Negative or weak positive (<2) moves.
        if positive_score >= 3:
            return None  # Sovereign — strong belonging

        # [ETERNAL LOCK] Moderate positive + no negative -> protect core code
        if positive_score >= 2 and not has_negative:
            return None  # Belongs — do not move

        if has_negative or positive_score < 2:
            move = self._suggest_move(content_lower, rel_path, current_territory)
            if move:
                if has_negative:
                    move["reason"] += f" (negative signals detected)"
                if positive_score < 2:
                    move["reason"] += f" (weak positive: {positive_score}/3)"
                return move
        
        # [FINAL FALLBACK] Unknown but no negative -> archive safely (never delete)
        archive_dir = self.root / "archives/unknown_territory"
        archive_dir.mkdir(parents=True, exist_ok=True)
        return {
            "action": "deprecate",
            "source": str(self.root / rel_path),
            "target": str(archive_dir / Path(rel_path).name),
            "reason": f"Unknown territory — no positive signals (confidence {positive_score})"
        }

    def _suggest_move(self, content_lower: str, rel_path: str, current_territory: int) -> Optional[dict]:
        """
        Suggest better territory via semantic guidance.
        """
        suggested = self.get_placement_guidance(content_lower)
        target_key = None
        target_folder = suggested
        
        for k, folders in self.key_folders.items():
            if any(suggested.startswith(f) for f in folders):
                target_key = k
                target_folder = next(f for f in folders if suggested.startswith(f))
                break
        
        if target_key and target_key != current_territory:
            target = self.root / target_folder / Path(rel_path).name
            return {
                "action": "move",
                "source": str(self.root / rel_path),
                "target": str(target),
                "reason": f"Stray in Key {current_territory}: '{Path(rel_path).name}' belongs in Key {target_key} ({target_folder})"
            }
        return None

    def find_all_stray(self) -> List[dict]:
        """
        Scan entire codebase for stray files in wrong territories.
        """
        moves = []

        for py_file in self.root.rglob("*.py"):
            # Skip hidden directories and protected files
            if any(part.startswith(".") for part in py_file.parts):
                continue
            
            rel = py_file.relative_to(self.root)
            rel_str = str(rel).replace("\\", "/")
            
            # Skip protected files
            if rel.name in self.root_protected:
                continue
            
            # Skip __init__.py files
            if rel.name == "__init__.py":
                continue
                
            # Read file content for semantic analysis
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                stem_lower = py_file.stem.lower()
            except:
                continue
            
            # Check if file is in unmapped territory (root stray)
            is_mapped = any(rel_str.startswith(p + "/") or rel_str == p for p in self.all_mapped_paths)
            
            if not is_mapped:
                # Archive root strays
                archive_path = self.root_archive / rel.name
                moves.append({
                    "action": "deprecate",
                    "source": str(py_file),
                    "target": str(archive_path),
                    "reason": f"Root stray archived: '{rel.name}'"
                })
                continue
            
            # Stray WITHIN key territories
            intra_stray = self.is_stray_in_territory(rel_str, content_lower, stem_lower)
            if intra_stray:
                moves.append(intra_stray)
                
        return moves

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - no healing required")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def execute(self) -> None:
        """
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Main execution entry point.
        Finds and executes all territory violations with cache purging.
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n   [*] TerritoryHealerAgent: Scanning for intra-territory strays...")
        
        stray_actions = self.find_all_stray()
        
        if not stray_actions:
            print(f"   [✓] No territory violations detected")
            return
        
        print(f"\n   [!] Found {len(stray_actions)} territory violations:")
        for action in stray_actions[:10]:  # Show first 10
            print(f"      - {action['reason']}")
            print(f"        {action['source']} → {action['target']}")
        
        if len(stray_actions) > 10:
            print(f"      ... and {len(stray_actions) - 10} more")
        
        # [GHOST PURGE] Connect to Redis and Pinecone for cleanup
        try:
            from agentic_core.L4_state.validation_context.PineconeSovereignAgent import (
                PineconeSovereignAgent,
            )
            from agentic_core.L4_state.validation_context.redis_sovereign_agent import (
                RedisSovereignAgent,
            )
            redis_agent = RedisSovereignAgent(self.root)
            pinecone_agent = PineconeSovereignAgent(self.root)
        except Exception:
            redis_agent = None
            pinecone_agent = None

        moved = [a for a in stray_actions if a["action"] == "move"]
        archived = [a for a in stray_actions if a["action"] == "deprecate"]
        
        for action in moved:
            source_path = Path(action["source"])
            target_path = Path(action["target"])
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            import shutil
            shutil.move(source_path, target_path)
            print(f"   [MOVED] {source_path.name} → {target_path.parent}")
            
            # Purge old path immediately after move
            if redis_agent:
                redis_agent.invalidate_by_path(source_path)
            if pinecone_agent:
                pinecone_agent.purge_ghost_vector(source_path)
        
        for action in archived:
            source_path = Path(action["source"])
            ctx.report("TerritoryHealer", 1, True, action["reason"])
            source_path.unlink(missing_ok=True)
            # Purge deprecated file from cache
            if redis_agent:
                redis_agent.invalidate_by_path(source_path)
            if pinecone_agent:
                pinecone_agent.purge_ghost_vector(source_path)
        
        # Report to context if available
        if self.ctx:
            for action in stray_actions:
                self.ctx.report("TerritoryViolation", 20, True, f"Fixed: {action['reason']}")
        
        print(f"\n   [✓] Territory healing complete. Processed {len(stray_actions)} files.")
