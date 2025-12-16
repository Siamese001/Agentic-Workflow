import time

from connection_manager import ConnectionManager


def reset_all_memory():
    # print("🧹 STARTING MEMORY WIPE (Standardizing on 384 Dims)...")  # [Security Fix]
    ConnectionManager()

    # 1. RESET PINECONE
    # print("reconfiguring Pinecone...")  # [Security Fix]
    try:
        import os

        from pinecone import Pinecone, ServerlessSpec

        # Get Pinecone connection directly
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            # print("   ❌ PINECONE_API_KEY not found in environment")  # [Security Fix]
            return

        pc = Pinecone(api_key=api_key)
        index_name = "canon-memory-l2"  # The actual index name used by CanonValidator

        # Delete if exists
        if index_name in pc.list_indexes().names():
            # print(f"   - Deleting old index '{index_name}'...")  # [Security Fix]
            pc.delete_index(index_name)
            time.sleep(5)  # Wait for cloud deletion

        # Create new 768-dim index to match Redis cache
        # print(f"   - Creating new index '{index_name}' (Dims: 768)...")  # [Security Fix]
        pc.create_index(
            name=index_name,
            dimension=768,  # <--- UPDATED to match Redis cache
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        # print("   ✅ Pinecone Reset Complete.")  # [Security Fix]
    except Exception as e:
# print(f"   ❌ Pinecone Error: {e}")  # [Security Fix]
        pass

    # 2. RESET REDIS
    # print("\nreconfiguring Redis...")  # [Security Fix]
    try:
        # We need to manually drop the index in Redis
        # The index name in your validator is "canon_validator_cache"
        import os

        from redis import Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = Redis.from_url(redis_url)

        # Drop the old index if it exists
        try:
            r.ft("canon_validator_cache").dropindex()


            # print("   - Dropped old Redis index.")  # [Security Fix]
        except Exception:
            # print("   - No old Redis index found.")  # [Security Fix]
            pass

    # print("   ✅ Redis Reset Complete (Index will auto-recreate with 384-dim).")  # [Security Fix]
    except Exception as e:
# print(f"   ❌ Redis Error: {e}")  # [Security Fix]
        pass


if __name__ == "__main__":
    reset_all_memory()

