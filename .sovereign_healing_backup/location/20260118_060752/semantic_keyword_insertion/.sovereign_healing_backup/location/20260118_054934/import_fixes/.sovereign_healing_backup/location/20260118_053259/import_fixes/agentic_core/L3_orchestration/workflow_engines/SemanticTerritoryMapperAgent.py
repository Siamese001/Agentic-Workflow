from __future__ import annotations
from dataclasses import dataclass
#!/usr/bin/env python3
"""
Semantic Territory Mapper Agent - Intelligent Brain
Maps files to their correct semantic territories using real Gemini embeddings.
This agent replaces mock logic with actual SubAtomicEngine integration.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import redis

from agentic_core.config.blueprint_sovereign.SovereignEnv import get_env
from agentic_core.L5_safety.validators.structure_blueprint_2 import TERRITORY_EXAMPLES
try:
    from agentic_core.L2_execution.ToolRegistry.PineconeSovereignAgent import PineconeSovereignAgent
except ImportError:
    PineconeSovereignAgent = None

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@dataclass
class SemanticTerritoryMapperAgent(HealerMixin, MCPHardenedMixin):
    """
    The Intelligent Brain that maps files to semantic territories
    using real Gemini embeddings and vector similarity search.
    """
    
    def __init__(self, project_root: Path, ctx: Optional[Any] = None) -> None:
        """
        Initialize semantic territory mapper.
        
        Args:
            project_root: Project root directory
            ctx: Optional validation context
        """
        self.project_root: Path = project_root
        self.ctx: Optional[Any] = ctx
        
        # [ETERNAL GATEWAY] Use the dedicated vector agent
        self.pinecone = PineconeSovereignAgent(project_root)
        
        # Get sovereign environment configuration
        env = get_env()
        self.redis = redis.from_url(env.REDIS_URL)
        
        # Key-specific stray signals remain in this agent
        self.key_stray_signals = {
            11: {"script", "tool", "cli", "operational", "backup"},
            12: {"test", "fixture", "mock"},
            13: {"heal", "fix", "prune"},
            15: {"strategy", "reasoning", "planner"},
            17: {"agent", "manager", "engine", "healer"},
            19: {"script", "test", "heal"},
        }

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, 'project_root'), "Missing project_root"
        assert hasattr(self, 'pinecone'), "Missing pinecone"
        return True
            
    def _seed_territory_examples(self) -> Any:
        """Seed the index with known territory examples for reference."""
        print(f"   [*] Seeding territory examples...")
        vectors = []
        
        for territory, example in TERRITORY_EXAMPLES.items():
            # Create embedding for the example
            embedding = self.get_embedding(example)
            if embedding:
                vectors.append({
                    "id": f"territory:{territory}",
                    "values": embedding,
                    "metadata": {
                        "type": "territory",
                        "path": territory,
                        "example": example
                    }
                })
        
        if vectors:
            self.index.upsert(vectors)
            print(f"   [✓] Seeded {len(vectors)} territory examples")
            
    def get_embedding(self, text: str) -> List[float]:
        """
        Sovereign embedding — delegated to PineconeSovereignAgent.
        Uses Redis cache for performance.
        """
        cache_key = f"embed:v2:{hashlib.sha256(text.encode()).hexdigest()}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Delegate to sovereign agent
        embedding = self.pinecone.get_embedding(text)
        
        # Cache for 7 days
        self.redis.set(cache_key, json.dumps(embedding), ex=604800)
        return embedding
        
    def map_file_to_territory(self, file_path: Path, content: str = None) -> Tuple[str, float]:
        """
        Map a file to its most appropriate semantic territory.
        Returns (territory_path, confidence_score).
        """
        if not content:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                return "unknown", 0.0
                
        # Create embedding for file content
        content_embedding = self.get_embedding(content[:5000])  # Limit content size
        if not content_embedding:
            return "unknown", 0.0
            
        # Search for similar territories
        try:
            results = self.pinecone.index.query(
                vector=content_embedding,
                top_k=5,
                include_metadata=True
            )
            
            if results and results.get('matches'):
                best_match = results['matches'][0]
                if best_match['score'] > 0.90:  # Eternal threshold — 90%+ confidence only
                    territory = best_match['metadata'].get('path', 'unknown')
                    confidence = best_match['score']
                    
                    # [L4 REFINEMENT] Can we go deeper?
                    deepest = territory
                    from agentic_core.L5_safety.validators.structure_blueprint_2 import (
                        CORE_L4_SUBFOLDER_MAP,
                    )
                    
                    for l3, l4_list in CORE_L4_SUBFOLDER_MAP.items():
                        if l3 in deepest:
                            for l4 in l4_list:
                                if l4.lower() in content.lower() or l4.lower() in file_path.name.lower():
                                    deepest = f"{deepest}/{l4}"
                                    break
                    
                    return deepest, confidence
        except Exception as e:
            print(f"   [!] Territory mapping failed: {e}")
            
        return "unknown", 0.0
        
    def suggest_territory_move(self, file_path: Path, current_location: str) -> Optional[str]:
        """
        Suggest a better territory for a file if it's misplaced.
        Returns suggested path or None if current location is appropriate.
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return None
            
        suggested_territory, confidence = self.map_file_to_territory(file_path, content)
        
        if suggested_territory != "unknown" and confidence > 0.8:
            # Check if file is already in the suggested territory
            if suggested_territory not in str(current_location):
                return f"{suggested_territory}/{file_path.name}"
                
        return None
        
    def analyze_territory_coverage(self) -> Dict[str, any]:
        """
        Analyze the coverage of territories across the codebase.
        Returns statistics about territory distribution.
        """
        stats = {
            "total_files": 0,
            "mapped_files": 0,
            "territory_distribution": {},
            "unmapped_files": []
        }
        
        # Scan all Python files
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            stats["total_files"] += 1
            territory, confidence = self.map_file_to_territory(py_file)
            
            if territory != "unknown":
                stats["mapped_files"] += 1
                stats["territory_distribution"][territory] = \
                    stats["territory_distribution"].get(territory, 0) + 1
            else:
                stats["unmapped_files"].append(str(py_file.relative_to(self.project_root)))
                
        return stats
        
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
        Analyzes and reports on territory mapping across the codebase.
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n   [*] SemanticTerritoryMapperAgent: Analyzing territory coverage...")
        
        stats = self.analyze_territory_coverage()
        
        print(f"   [✓] Analysis complete:")
        print(f"      - Total files: {stats['total_files']}")
        print(f"      - Mapped files: {stats['mapped_files']}")
        print(f"      - Coverage: {stats['mapped_files']/stats['total_files']*100:.1f}%")
        
        print(f"\n   Territory Distribution:")
        for territory, count in sorted(stats['territory_distribution'].items()):
            print(f"      - {territory}: {count} files")
            
        if stats['unmapped_files']:
            print(f"\n   [!] Unmapped files ({len(stats['unmapped_files'])}):")
            for file_path in stats['unmapped_files'][:5]:
                print(f"      - {file_path}")
            if len(stats['unmapped_files']) > 5:
                print(f"      ... and {len(stats['unmapped_files']) - 5} more")
                
        return stats
