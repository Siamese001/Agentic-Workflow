#!/usr/bin/env python3
"""
PineconeSovereignAgent - Eternal Sovereign Gateway to Pinecone

This agent serves as the sole gateway for all Pinecone operations in the system.
It handles index creation, health checks, embedding generation, and territory bootstrapping.
Zero drift, eternal readiness.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any

import numpy as np
from pinecone import Pinecone, ServerlessSpec

from agentic_core.config.P1_core.sovereign_env import get_env
from agentic_core.L4_state.validation_context.redis_sovereign_agent import RedisSovereignAgent
from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngine

class PineconeSovereignAgent:
    """
    Sovereign Pinecone controller — zero drift, eternal readiness.
    Centralizes all vector operations to prevent configuration drift.
    """
    
    def __init__(self, project_root: Optional[Path] = None, ctx=None):
        # Sovereign anchor: Ensure we know where we are in the territory
        self.project_root = project_root or Path(__file__).resolve().parents[4]
        self.status = "INITIALIZING"
        
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            self.status = "DEGRADED (Missing API Key)"
            print(f"   [!] PineconeSovereignAgent: API key missing.")
            return
        
        try:
            env = get_env(self.project_root)
            self.pc = Pinecone(api_key=api_key)
            self.index_name = env.PINECONE_INDEX_NAME
            self.dimension = env.EMBEDDING_DIMENSION
            self.cloud = env.PINECONE_CLOUD
            self.region = env.PINECONE_REGION
            self.gemini = SubAtomicEngine()
            self.status = "ONLINE"
        except Exception as e:
            self.status = f"DEGRADED ({str(e)})"
            print(f"   [!] PineconeSovereignAgent initialization failed: {e}")
            return
        
        # Store ValidationContext for precise sync operations
        self.ctx = ctx
        
        # [HYBRID CONFIG] 0.7 = 70% Semantic / 30% Keyword
        self.hybrid_alpha = float(os.getenv("HYBRID_ALPHA", "0.7"))

        # [REDIS LINK] Link the sovereign cache
        try:
            self.redis_gateway = RedisSovereignAgent(project_root)
            self.redis = self.redis_gateway.get_client()
        except Exception as e:
            print(f"   [!] Redis Link Failed: {e}")
            self.redis = None

        # Connect or create — the 'Eternal' part
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="dotproduct",  # Required for hybrid sparse/dense
                spec={"serverless": {"cloud": self.cloud, "region": self.region}}
            )
            print(f"   [OK] PineconeSovereignAgent: Created new index '{self.index_name}'")
        
        self.index = self.pc.Index(self.index_name)

        # Force sync with SSOT
        self.bootstrap_territory_vectors()

    def get_embedding(self, text: str, is_sanity_check: bool = False) -> List[float]:
        """
        Sovereign embedding — cached, deterministic, QUALITY-VALIDATED.
        
        Args:
            text: Text to embed
            is_sanity_check: If True, skip recursive sanity validation
            
        Returns:
            List of floats representing the embedding vector
        """
        cache_key = f"pc_embed:{hashlib.sha256(text.encode()).hexdigest()}"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Sovereign neutral prompt for embedding generation
        system_prompt = "You are a code territory classifier. Return only JSON: {\"embedding\": [float vector of code semantics]}"
        user_prompt = f"Classify this code snippet for canon territory mapping:\n\n{text[:12000]}"
        
        response = self.gemini.resilient_mutation(
            user_prompt,
            system_prompt=system_prompt,
            return_json=True,
            temperature=0.0  # Deterministic for consistency
        )
        
        embedding = response.get("embedding", [])
        
        # [ETERNAL QUALITY VALIDATION]
        # Skip recursive sanity check if we are currently IN a sanity check
        validated_embedding = self._validate_and_repair_embedding(embedding, text, skip_sanity=is_sanity_check)
        
        if self.redis:
            self.redis.set(cache_key, json.dumps(validated_embedding), ex=604800)
            
        return validated_embedding
    
    def _validate_and_repair_embedding(self, embedding: List[float], source_text: str, skip_sanity: bool = False) -> List[float]:
        """
        Sovereign embedding quality gate: Correct length, Non-zero variance, Reasonable norm.
        """
        # 1. Length validation
        if len(embedding) != self.dimension:
            if len(embedding) < self.dimension:
                embedding += [0.0] * (self.dimension - len(embedding))
            else:
                embedding = embedding[:self.dimension]
        
        arr = np.array(embedding, dtype=np.float32)
        
        # 2. Zero/near-zero vector check
        norm = np.linalg.norm(arr)
        if norm < 1e-6:
            print(f"   [!] Zero vector detected — fallback")
            return [0.0] * self.dimension
        
        # 3. Low variance check
        if np.std(arr) < 1e-4:
            print(f"   [!] Low variance embedding — degraded quality")
            return [0.0] * self.dimension
        
        # 4. Self-similarity sanity (avoiding infinite loops)
        if not skip_sanity and len(source_text) > 100:
            try:
                short_text = source_text[:500]
                # Call get_embedding with sanity flag to prevent recursion
                re_embed_raw = self.get_embedding(short_text, is_sanity_check=True)
                re_embed = np.array(re_embed_raw, dtype=np.float32)
                
                denom = (norm * np.linalg.norm(re_embed) + 1e-8)
                cosine_sim = np.dot(arr, re_embed) / denom
                
                if cosine_sim < 0.7:
                    print(f"   [!] Self-similarity low ({cosine_sim:.2f}) — invalidating")
                    return [0.0] * self.dimension
            except Exception as e:
                print(f"   [!] Sanity check failed: {e}")
        
        return arr.tolist()

    def _get_sparse_vector(self, text: str) -> Dict[str, Any]:
        """Extracts keywords from blueprint signals for hybrid search"""
        from agentic_core.config.P1_core.structure_blueprint import CANON_SIGNALS
        text_low = text.lower()
        # Simple TF-based sparse vector
        indices = []
        values = []
        for i, word in enumerate(sorted(list(CANON_SIGNALS))):
            count = text_low.count(word.lower())
            if count > 0:
                indices.append(i)
                values.append(float(count))
        return {"indices": indices, "values": values}

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Eternal precision: Combined Vector + Keyword search"""
        dense_vec = self.get_embedding(query)
        sparse_vec = self._get_sparse_vector(query)
        
        return self.index.query(
            vector=dense_vec,
            sparse_vector=sparse_vec,
            top_k=top_k,
            include_metadata=True
        ).to_dict()

    def purge_ghost_vector(self, file_path: Path):
        """Surgical strike to remove stale vector data"""
        file_id = f"file_{str(file_path.relative_to(Path('.').resolve())).replace('/', '_')}"
        try:
            self.index.delete(ids=[file_id])
        except Exception:
            pass

    def bootstrap_territory_vectors(self):
        """
        Syncs the index with the structure_blueprint.py constants.
        Safe to run multiple times (uses upsert).
        """
        from agentic_core.config.P1_core.structure_blueprint import TERRITORY_EXAMPLES
        
        vectors = []
        for territory, example in TERRITORY_EXAMPLES.items():
            emb = self.get_embedding(example)
            vec_id = f"territory_{hashlib.sha256(territory.encode()).hexdigest()[:16]}"
            vectors.append({
                "id": vec_id, 
                "values": emb, 
                "metadata": {"territory": territory, "type": "bootstrap"}
            })
        
        if vectors:
            self.index.upsert(vectors=vectors)
            print(f"   [OK] PineconeSovereignAgent: Bootstrapped {len(vectors)} territories")

    async def upsert_sovereign_chunks(self, chunks: List[Dict], namespace: str = "canon"):
        """
        L4: Secure, idempotent upsert into the vector memory
        """
        vectors = []
        for chunk in chunks:
            # Generate a content-based ID for idempotency
            content_hash = hashlib.sha256(chunk["text"].encode('utf-8')).hexdigest()
            
            vectors.append({
                "id": content_hash,
                "values": chunk["values"],
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["metadata"].get("source", "unknown"),
                    "ingested_at": chunk["metadata"].get("ingested_at")
                }
            })
        
        # Batch upsert in sizes of 100
        for i in range(0, len(vectors), 100):
            self.index.upsert(vectors=vectors[i:i+100], namespace=namespace)
    
    def upsert_file_vector(self, file_path: Path, territory_hint: Optional[str] = None):
        """Upsert single file — used during healing"""
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        emb = self.get_embedding(content)
        
        # Final quality gate
        if all(abs(x) < 1e-8 for x in emb):
            print(f"   [!] Skipping upsert for {file_path} — invalid embedding")
            return
        
        file_id = f"file_{file_path.relative_to(Path('.').resolve())}".replace("/", "_")
        metadata = {"file_path": str(file_path), "type": "file"}
        if territory_hint:
            metadata["territory"] = territory_hint
        
        self.index.upsert(vectors=[{"id": file_id, "values": emb, "metadata": metadata}])
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Runtime retrieval for agents needing to 'find' logic.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        q_emb = self.get_embedding(query)
        results = self.index.query(vector=q_emb, top_k=top_k, include_metadata=True)
        return results.to_dict() if hasattr(results, 'to_dict') else results
    
    def health_check(self) -> Dict:
        """Enhanced health check with sample quality assessment"""
        stats = self.index.describe_index_stats()
        
        # Sample vector sanity
        sample_query = self.index.query(vector=[0.1]*self.dimension, top_k=1, include_values=True)
        sample_quality = "good"
        if sample_query['matches'] and np.linalg.norm(sample_query['matches'][0]['values']) < 0.1:
            sample_quality = "degraded"
        
        return {
            "vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness,
            "sample_quality": sample_quality
        }

    async def execute(self, ctx=None):
        """
        Health check for the validator loop.
        Reports index status and vector count with quality metrics.
        """
        try:
            health = self.health_check()
            print(f"   [OK] PineconeSovereignAgent: {health['vectors']} vectors online (quality: {health['sample_quality']})")
            
            if ctx:
                ctx.report("VectorHealth", 1, True, 
                          f"Pinecone Index {self.index_name}: {health['vectors']} vectors, quality={health['sample_quality']}")
        except Exception as e:
            print(f"   [!] PineconeSovereignAgent health check failed: {e}")
            if ctx:
                ctx.report("VectorHealth", 1, False, f"Pinecone health check failed: {str(e)}")
