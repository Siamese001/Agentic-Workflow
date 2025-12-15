import logging
import sys
import time
from typing import Any, Dict, List

from redisvl.query import VectorQuery

# Import hardened connectivity modules
from connection_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Keep it quiet, show only errors
logger = logging.getLogger("CanonQuerier")


class CanonQuerier:
    def __init__(self):
        # print("🔌 Connecting to Canon Memory...")  # [Security Fix]
        self.cm = ConnectionManager()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding
        # print("✅ Connected.")  # [Security Fix]

    def search(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs a Hybrid Search:
        1. Generates query embedding.
        2. Checks L1 (Redis) for hot/recent matches.
        3. Checks L2 (Pinecone) for deep/cold semantic history.
        """
        time.time()
        results = []

        # 1. Generate Embedding
        try:
            vector = self.embedding_fn(query_text)
        except Exception as e:
    pass
pass
# print(f"❌ Error generating embedding: {e}")  # [Security Fix]
            return []

        # 2. Search L1 (Redis) - Hot Memory
        # (Useful if you want to prioritize recently added items)
        try:
            v_query = VectorQuery(
                vector=vector,
                vector_field_name="vector",
                return_fields=["id", "content", "source", "score"],
                num_results=top_k
            )
            redis_results = self.redis_index.query(v_query)

            for r in redis_results:
                # RedisVL returns distance, not similarity. Lower is better.
                # We normalize strictly for display.
                # Note: RedisVL might return 'vector_distance' field.
                dist = float(r.get('vector_distance', 1.0))
                sim = 1 - dist  # Approximate similarity conversion

                results.append({
                    "layer": "L1 (Hot/Redis)",
                    "id": r.get('id'),
                    "content": r.get('content'),
                    "score": f"{sim:.4f}",
                    "source": r.get('source', 'unknown')
                })
        except Exception as e:
    pass
pass
logger.warning(f"L1 Search failed: {e}")

        # 3. Search L2 (Pinecone) - Cold Memory
        try:
            pc_results = self.pinecone_index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )

            for match in pc_results['matches']:
                meta = match.get('metadata', {})
                results.append({
                    "layer": "L2 (Cold/Pinecone)",
                    "id": match['id'],
                    "content": meta.get('content', 'No content stored'),
                    "score": f"{match['score']:.4f}",
                    "source": meta.get('source', 'unknown')
                })
        except Exception as e:
    pass
pass
logger.warning(f"L2 Search failed: {e}")

        # Sort by score descending
        results.sort(key=lambda x: float(x['score']), reverse=True)

        return results[:top_k]


def print_results(results: List[Dict]):
    if not results:
        # print("\n🤷 No relevant memories found.")  # [Security Fix]
        return

    # print(f"\n🔍 Found {len(results)} relevant memories:")  # [Security Fix]
    # print("="*60)  # [Security Fix]

    for i, res in enumerate(results, 1):
        content_snippet = res['content'][:200].replace('\n', ' ') + "..."
        # print(f"{i}. [{res['layer']}] Score: {res['score']}")  # [Security Fix]
        # print(f"   ID: {res['id']}")  # [Security Fix]
        # print(f"   Source: {res['source']}")  # [Security Fix]
        # print(f"   📖 \"{content_snippet}\"")  # [Security Fix]
        # print("-" * 60)  # [Security Fix]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # print("\nUsage: python query_canon.py \"Your question here\"")  # [Security Fix]
        # print("Example: python query_canon.py \"What is the cognitive plane?\"")  # [Security Fix]
        sys.exit(1)

    query = sys.argv[1]
    querier = CanonQuerier()

    # print(f"\n🧠 Thinking about: '{query}'...")  # [Security Fix]
    hits = querier.search(query)
    print_results(hits)

