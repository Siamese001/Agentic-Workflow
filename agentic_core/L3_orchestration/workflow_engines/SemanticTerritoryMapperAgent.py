"""
Semantic Territory Mapper Agent - Intelligent Brain
Maps files to their correct semantic territories using real Gemini embeddings.
This agent replaces mock logic with actual SubAtomicEngine integration.
"""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import redis
from agentic_core.config.blueprint_sovereign.sovereign_env import get_env
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
territory_examples: Any = {'agentic_core/L1_cognition': 'strategy planning reasoning mission decomposition', 'agentic_core/L3_orchestration': 'fission orchestration routing workflow manager', 'agentic_core/L4_state': 'memory cache pinecone redis historian audit', 'agentic_core/L5_safety': 'guardrail safety policy enforcer filter', 'apps_rg/agents': 'resume ranking narrative scoring jd match', 'apps_lic/agents': 'license compliance workflow validation', 'apps_shared/utils': 'shared helper validation adapter', 'scripts': 'operational tool cli integrity backup deploy'}

class SemanticTerritoryMapperAgent:
    """
    The Intelligent Brain that maps files to semantic territories
    using real Gemini embeddings and vector similarity search.
    """

    def __init__(self, project_root: Path, ctx=None):
        self.project_root = project_root
        self.ctx = ctx
        self.pinecone = PineconeSovereignAgent(project_root)
        env = get_env()
        self.redis = redis.from_url(env.REDIS_URL)
        self.key_stray_signals = {11: {'script', 'tool', 'cli', 'operational', 'backup'}, 12: {'test', 'fixture', 'mock'}, 13: {'heal', 'fix', 'prune'}, 15: {'strategy', 'reasoning', 'planner'}, 17: {'agent', 'manager', 'engine', 'healer'}, 19: {'script', 'test', 'heal'}}

    def _seed_territory_examples(self):
        """Seed the index with known territory examples for reference."""
        print(f'   [*] Seeding territory examples...')
        vectors = []
        for territory, example in TERRITORY_EXAMPLES.items():
            embedding = self.get_embedding(example)
            if embedding:
                vectors.append({'id': f'territory:{territory}', 'values': embedding, 'metadata': {'type': 'territory', 'path': territory, 'example': example}})
        if vectors:
            self.index.upsert(vectors)
            print(f'   [✓] Seeded {len(vectors)} territory examples')

    def get_embedding(self, text: str) -> List[float]:
        """
        Sovereign embedding — delegated to PineconeSovereignAgent.
        Uses Redis cache for performance.
        """
        cache_key: Any = f'embed:v2:{hashlib.sha256(text.encode()).hexdigest()}'
        cached: Any = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        embedding: Any = self.pinecone.get_embedding(text)
        self.redis.set(cache_key, json.dumps(embedding), ex=604800)
        return embedding

    def map_file_to_territory(self, file_path: Path, content: str=None) -> Tuple[str, float]:
        """
        Map a file to its most appropriate semantic territory.
        Returns (territory_path, confidence_score).
        """
        if not content:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content: Any = f.read()
            except:
                return ('unknown', 0.0)
        content_embedding: Any = self.get_embedding(content[:5000])
        if not content_embedding:
            return ('unknown', 0.0)
        try:
            results: Any = self.pinecone.index.query(vector=content_embedding, top_k=5, include_metadata=True)
            if results and results.get('matches'):
                best_match: Any = results['matches'][0]
                if best_match['score'] > 0.9:
                    territory: Any = best_match['metadata'].get('path', 'unknown')
                    confidence: Any = best_match['score']
                    return (territory, confidence)
        except Exception as e:
            print(f'   [!] Territory mapping failed: {e}')
        return ('unknown', 0.0)

    def suggest_territory_move(self, file_path: Path, current_location: str) -> Optional[str]:
        """
        Suggest a better territory for a file if it's misplaced.
        Returns suggested path or None if current location is appropriate.
        """
        try:
            content: Any = file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return None
        suggested_territory, confidence = self.map_file_to_territory(file_path, content)
        if suggested_territory != 'unknown' and confidence > 0.8:
            if suggested_territory not in str(current_location):
                return f'{suggested_territory}/{file_path.name}'
        return None

    def analyze_territory_coverage(self) -> Dict[str, any]:
        """
        Analyze the coverage of territories across the codebase.
        Returns statistics about territory distribution.
        """
        stats: Any = {'total_files': 0, 'mapped_files': 0, 'territory_distribution': {}, 'unmapped_files': []}
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            stats['total_files'] += 1
            territory, confidence = self.map_file_to_territory(py_file)
            if territory != 'unknown':
                stats['mapped_files'] += 1
                stats['territory_distribution'][territory] = stats['territory_distribution'].get(territory, 0) + 1
            else:
                stats['unmapped_files'].append(str(py_file.relative_to(self.project_root)))
        return stats

    async def execute(self) -> Any:
        """
        Main execution entry point.
        Analyzes and reports on territory mapping across the codebase.
        """
        print(f'\n   [*] SemanticTerritoryMapperAgent: Analyzing territory coverage...')
        stats: Any = self.analyze_territory_coverage()
        print(f'   [✓] Analysis complete:')
        print(f"      - Total files: {stats['total_files']}")
        print(f"      - Mapped files: {stats['mapped_files']}")
        print(f"      - Coverage: {stats['mapped_files'] / stats['total_files'] * 100:.1f}%")
        print(f'\n   Territory Distribution:')
        for territory, count in sorted(stats['territory_distribution'].items()):
            print(f'      - {territory}: {count} files')
        if stats['unmapped_files']:
            print(f"\n   [!] Unmapped files ({len(stats['unmapped_files'])}):")
            for file_path in stats['unmapped_files'][:5]:
                print(f'      - {file_path}')
            if len(stats['unmapped_files']) > 5:
                print(f"      ... and {len(stats['unmapped_files']) - 5} more")
        return stats
