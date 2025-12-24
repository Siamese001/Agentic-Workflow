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
from typing import List, Optional, Dict


class TerritoryHealerAgent:
    """
    Enforces exhaustive territory compliance by detecting intra-territory strays.
    """
    
    def __init__(self, project_root: Path, ctx):
        self.root = project_root
        self.ctx = ctx
        
        from agentic_core.config.P1_core.structure_blueprint import (
            CANON_KEY_TO_FOLDER_MAP, ROOT_PROTECTED_FILES,
            TERRITORY_EXAMPLES  # For semantic hints
        )
        from agentic_core.runtime.shared.void_compliance import get_placement_guidance
        
        self.key_folders = CANON_KEY_TO_FOLDER_MAP
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

    def is_stray_in_territory(self, rel_path: str, content_lower: str, stem_lower: str) -> Optional[dict]:
        """
        Check if file is stray WITHIN its current key territory.
        Returns move dict if stray, else None.
        """
        current_territory = None
        for key, paths in self.key_folders.items():
            if any(rel_path.startswith(p + "/") or rel_path == p for p in paths):
                current_territory = key
                break
        
        if current_territory is None:
            return None  # Already handled by unmapped drift check

        # Get stray signals for this key
        stray_words = self.key_stray_signals.get(current_territory, set())
        if stray_words and any(word in stem_lower or word in content_lower for word in stray_words):
            # Suggest better territory via semantic guidance
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

    async def execute(self):
        """
        Main execution entry point.
        Finds and reports all territory violations.
        """
        print(f"\n   [*] TerritoryHealerAgent: Scanning for intra-territory strays...")
        
        moves = self.find_all_stray()
        
        if not moves:
            print(f"   [✓] No territory violations detected")
            return
        
        print(f"\n   [!] Found {len(moves)} territory violations:")
        for move in moves[:10]:  # Show first 10
            print(f"      - {move['reason']}")
            print(f"        {move['source']} → {move['target']}")
        
        if len(moves) > 10:
            print(f"      ... and {len(moves) - 10} more")
        
        # Report to context if available
        if self.ctx:
            for move in moves:
                self.ctx.report("TerritoryViolation", 20, False, move['reason'])
        
        print(f"\n   [INFO] Run with --heal flag to apply territory moves")
        
        return moves
