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
from typing import Any, Dict, List, Optional

class TerritoryHealerAgent:
    """
    Enforces exhaustive territory compliance by detecting intra-territory strays.
    """

    def __init__(self, project_root: Path = None, ctx = None):
        self.root = project_root
        self.ctx = ctx
        from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_TO_FOLDER_MAP, ROOT_PROTECTED_FILES, SOVEREIGN_REGISTRY, CANON_SIGNALS
        # [PHASE 20] DEPRECATION: void_compliance.py removed - inline placement guidance
        def get_placement_guidance(content_preview):
            if any(x in content_preview for x in ['planner', 'strategy', 'reasoning', 'mission']):
                return 'agentic_core/L1_cognition'
            if 'node' in content_preview.lower() or 'execute' in content_preview:
                return 'agentic_core/L1_cognition/thought_engine'
            if any(x in content_preview for x in ['router', 'orchestrator', 'fission', 'hop']):
                return 'agentic_core/L3_orchestration'
            if any(x in content_preview for x in ['pinecone', 'redis', 'storage', 'cache']):
                return 'agentic_core/L4_state'
            return 'agentic_core/L1_cognition'
        self.key_folders = CANON_KEY_TO_FOLDER_MAP
        self.key_positive_signals = CANON_SIGNALS
        self.all_mapped_paths = {p for ps in self.key_folders.values() for p in ps if p != '*'}
        self.root_protected = ROOT_PROTECTED_FILES
        self.get_placement_guidance = get_placement_guidance
        self.root_archive = project_root / 'archives' / 'deprecated_code'
        self.root_archive.mkdir(parents=True, exist_ok=True)
        self.key_stray_signals = {11: {'script', 'tool', 'cli', 'operational', 'backup'}, 12: {'test', 'fixture', 'mock'}, 13: {'heal', 'fix', 'prune'}, 15: {'strategy', 'reasoning', 'planner'}, 17: {'agent', 'manager', 'engine', 'healer'}, 19: {'script', 'test', 'heal'}}

    def check_depth_precision(self, file_path: Path) -> Optional[dict]:
        """
        Check if file violates precision depth requirements.
        Only heal if root precision is violated.
        General min/max healing logic removed.
        """
        try:
            rel_path: Any = file_path.relative_to(self.root)
            parts: Any = rel_path.parts
            depth: Any = len(parts)
            agentic_core_exact_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']
            if parts[0] == 'agentic_core' and depth != agentic_core_exact_depth:
                return self._suggest_precision_move(file_path, agentic_core_exact_depth)
        except ValueError:
            pass
        return None

    def _suggest_precision_move(self, file_path: Path, target_depth: int) -> dict:
        """
        Suggest a move to achieve the required precision depth.
        """
        rel_path = file_path.relative_to(self.root)
        parts = rel_path.parts
        if parts[0] == 'agentic_core' and len(parts) < 4:
            suggested = self.get_placement_guidance('')
            target_path = self.root / suggested / rel_path.name
            return {'action': 'move', 'source': str(file_path), 'target': str(target_path), 'reason': f'Depth precision: agentic_core requires depth {target_depth}, found {len(parts)}'}
        elif parts[0] == 'agentic_core' and len(parts) > 4:
            target_path = self.root / parts[0] / parts[1] / parts[2] / parts[3] / rel_path.name
            return {'action': 'move', 'source': str(file_path), 'target': str(target_path), 'reason': f'Depth precision: agentic_core requires depth {target_depth}, found {len(parts)}'}
        return None

    def is_stray_in_territory(self, rel_path: str, content_lower: str, stem_lower: str) -> Optional[dict]:
        """
        Check if file is stray WITHIN its current key territory.
        Uses DOUBLE-LOCK: negative signals (what doesn't belong) + positive signals (what does belong).
        Returns move dict if stray, else None.
        """
        current_territory: Any = None
        for key, paths in self.key_folders.items():
            if any((rel_path.startswith(p + '/') or rel_path == p for p in paths)):
                current_territory: Any = key
                break
        if current_territory is None:
            return None
        stray_words: Any = self.key_stray_signals.get(current_territory, set())
        has_negative: Any = any((word in stem_lower or word in content_lower for word in stray_words))
        positive_words: Any = self.key_positive_signals.get(current_territory, set())
        positive_score: Any = sum((1 for word in positive_words if word in stem_lower or word in content_lower))
        if positive_score >= 3:
            return None
        if positive_score >= 2 and (not has_negative):
            return None
        if has_negative or positive_score < 2:
            move: Any = self._suggest_move(content_lower, rel_path, current_territory)
            if move:
                if has_negative:
                    move['reason'] += f' (negative signals detected)'
                if positive_score < 2:
                    move['reason'] += f' (weak positive: {positive_score}/3)'
                return move
        archive_dir: Any = self.root / 'archives/unknown_territory'
        archive_dir.mkdir(parents=True, exist_ok=True)
        return {'action': 'deprecate', 'source': str(self.root / rel_path), 'target': str(archive_dir / Path(rel_path).name), 'reason': f'Unknown territory — no positive signals (confidence {positive_score})'}

    def _suggest_move(self, content_lower: str, rel_path: str, current_territory: int) -> Optional[dict]:
        """
        Suggest better territory via semantic guidance.
        """
        suggested = self.get_placement_guidance(content_lower)
        target_key = None
        target_folder = suggested
        for k, folders in self.key_folders.items():
            if any((suggested.startswith(f) for f in folders)):
                target_key = k
                target_folder = next((f for f in folders if suggested.startswith(f)))
                break
        if target_key and target_key != current_territory:
            target = self.root / target_folder / Path(rel_path).name
            return {'action': 'move', 'source': str(self.root / rel_path), 'target': str(target), 'reason': f"Stray in Key {current_territory}: '{Path(rel_path).name}' belongs in Key {target_key} ({target_folder})"}
        return None

    def find_all_stray(self) -> List[dict]:
        """
        Scan entire codebase for stray files in wrong territories.
        """
        moves: Any = []
        for py_file in self.root.rglob('*.py'):
            if any((part.startswith('.') for part in py_file.parts)):
                continue
            rel: Any = py_file.relative_to(self.root)
            rel_str: Any = str(rel).replace('\\', '/')
            if rel.name in self.root_protected:
                continue
            if rel.name == '__init__.py':
                continue
            try:
                content: Any = py_file.read_text(encoding='utf-8', errors='ignore')
                content_lower: Any = content.lower()
                stem_lower: Any = py_file.stem.lower()
            except:
                continue
            is_mapped: Any = any((rel_str.startswith(p + '/') or rel_str == p for p in self.all_mapped_paths))
            if not is_mapped:
                archive_path: Any = self.root_archive / rel.name
                moves.append({'action': 'deprecate', 'source': str(py_file), 'target': str(archive_path), 'reason': f"Root stray archived: '{rel.name}'"})
                continue
            intra_stray: Any = self.is_stray_in_territory(rel_str, content_lower, stem_lower)
            if intra_stray:
                moves.append(intra_stray)
        return moves

    async def execute(self) -> Any:
        """
        Main execution entry point.
        Finds and executes all territory violations with cache purging.
        """
        print(f'\n   [*] TerritoryHealerAgent: Scanning for intra-territory strays...')
        stray_actions: Any = self.find_all_stray()
        if not stray_actions:
            print(f'   [✓] No territory violations detected')
            return
        print(f'\n   [!] Found {len(stray_actions)} territory violations:')
        for action in stray_actions[:10]:
            print(f"      - {action['reason']}")
            print(f"        {action['source']} → {action['target']}")
        if len(stray_actions) > 10:
            print(f'      ... and {len(stray_actions) - 10} more')
        try:
            from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
            from agentic_core.L4_state.validation_context.RedisSovereignAgent import RedisSovereignAgent
            redis_agent: Any = RedisSovereignAgent(self.root)
            pinecone_agent: Any = PineconeSovereignAgent(self.root)
        except Exception:
            redis_agent: Any = None
            pinecone_agent: Any = None
        moved: Any = [a for a in stray_actions if a['action'] == 'move']
        archived: Any = [a for a in stray_actions if a['action'] == 'deprecate']
        for action in moved:
            source_path: Any = Path(action['source'])
            target_path: Any = Path(action['target'])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(source_path, target_path)
            print(f'   [MOVED] {source_path.name} → {target_path.parent}')
            if redis_agent:
                redis_agent.invalidate_by_path(source_path)
            if pinecone_agent:
                pinecone_agent.purge_ghost_vector(source_path)
        for action in archived:
            source_path: Any = Path(action['source'])
            ctx.report('TerritoryHealer', 1, True, action['reason'])
            source_path.unlink(missing_ok=True)
            if redis_agent:
                redis_agent.invalidate_by_path(source_path)
            if pinecone_agent:
                pinecone_agent.purge_ghost_vector(source_path)
        if self.ctx:
            for action in stray_actions:
                self.ctx.report('TerritoryViolation', 20, True, f"Fixed: {action['reason']}")
        print(f'\n   [✓] Territory healing complete. Processed {len(stray_actions)} files.')
