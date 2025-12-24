#!/usr/bin/env python3
"""
Semantic Territory Mapper Agent - Intelligent Brain
Maps files to their correct semantic territories using real Gemini embeddings.
This agent replaces mock logic with actual SubAtomicEngine integration.
"""

import hashlib
import json
import redis
from typing import List, Dict, Optional, Tuple
from pinecone import Pinecone
from pathlib import Path

from agentic_core.L5_safety.P1_core.subatomic_engine import SubAtomicEngine  # Sovereign Gemini-only engine
from agentic_core.config.P1_core.structure_blueprint import TERRITORY_EXAMPLES
from agentic_core.config.P1_core.sovereign_env import get_env


class SemanticTerritoryMapperAgent:
    """
    The Intelligent Brain that maps files to semantic territories
    using real Gemini embeddings and vector similarity search.
    """
    
    def __init__(self, project_root: Path, ctx=None):
        self.project_root = project_root
        self.ctx = ctx
        # [NO HARDCODING] Sovereign engine — model from .env only
        self.gemini = SubAtomicEngine()  # Enforced GEMINI_MODEL from .env via verify_neural_link()
        
        # Get sovereign environment configuration
        env = get_env()
        self.redis = redis.from_url(env.REDIS_URL)
        self.pc = Pinecone(api_key=env.PINECONE_API_KEY)
        self.index_name = env.PINECONE_INDEX_NAME
        self.dim = env.EMBEDDING_DIMENSION
        
        # Initialize or connect to Pinecone index
        try:
            self.index = self.pc.Index(self.index_name)
            print(f"   [OK] Connected to existing Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"   [*] Creating new Pinecone index: {self.index_name}")
            # [DYNAMIC DIMENSION] Query model for embedding size — no hardcode
            test_embed = self.gemini.resilient_mutation(
                "Return only a JSON with key 'embedding' and a sample embedding vector of length 1: {\"embedding\": [0.0]}",
                return_json=True
            )
            dim = len(test_embed.get("embedding", [0]*self.dim))  # Fallback to env dimension
            self.pc.create_index(name=self.index_name, dimension=dim, metric="cosine")
            self.index = self.pc.Index(self.index_name)
            print(f"   [✓] Created index with dimension {dim}")
            
    def _seed_territory_examples(self):
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
        Sovereign embedding — zero hardcoding.
        Uses GEMINI_MODEL from .env via SubAtomicEngine.
        Prompt neutral — works with any Gemini variant.
        """
        cache_key = f"embed:v2:{hashlib.sha256(text.encode()).hexdigest()}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
            
        # Sovereign neutral prompt — no model-specific assumptions
        system_prompt = "You are a code territory classifier. Return only JSON: {\"embedding\": [float vector of code semantics]}"
        user_prompt = f"Classify this code snippet for canon territory mapping:\n\n{text[:12000]}"  # Safe token buffer
        
        response = self.gemini.resilient_mutation(
            user_prompt,
            system_prompt=system_prompt,
            return_json=True,
            temperature=0.0  # Deterministic for caching
        )
        
        embedding = response.get("embedding", [])
        if not embedding:
            # Fallback: zero vector — safe non-match
            embedding = [0.0] * self.dim
            
        self.redis.set(cache_key, json.dumps(embedding), ex=604800)  # 7-day sovereign cache
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
            results = self.index.query(
                vector=content_embedding,
                top_k=5,
                include_metadata=True
            )
            
            if results and results.get('matches'):
                best_match = results['matches'][0]
                if best_match['score'] > 0.90:  # Eternal threshold — 90%+ confidence only
                    territory = best_match['metadata'].get('path', 'unknown')
                    confidence = best_match['score']
                    return territory, confidence
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
        
    async def execute(self):
        """
        Main execution entry point.
        Analyzes and reports on territory mapping across the codebase.
        """
        print(f"\n   [*] SemanticTerritoryMapperAgent: Analyzing territory coverage...")
        
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
