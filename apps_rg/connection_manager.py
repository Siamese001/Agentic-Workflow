import os
import logging
from typing import Any, Optional, Callable
from redis import Redis
from redisvl.index import SearchIndex

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionFactory:
    """Factory for managing connectivity to Redis, Pinecone, and LLM services."""

    @staticmethod
    def get_redis_connection() -> Any:
        """
        Returns a connected Redis client instance.
        Ensures we return the client object, not the function itself.
        """
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        try:
            logger.info(f"🔌 Connecting to Redis at {redis_url}...")
            # Use specific password if provided, else rely on URL
            password = os.getenv("REDIS_PASSWORD")
            client = Redis.from_url(redis_url, password=password, decode_responses=True)
            if client.ping():
                logger.info("✅ Redis connection successful")
                return client
        except Exception as e:
            logger.error(f"❌ Redis Connection Failed: {e}")
            raise ConnectionError(f"Redis Unreachable: {e}")

    @staticmethod
    def get_pinecone_client() -> Any:
        """
        Initializes and returns the Pinecone client.
        Used for handshake tests and index management.
        """
        try:
            from pinecone import Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY is not set")

            pc = Pinecone(api_key=api_key)
            logger.info("✅ Pinecone client connection successful")
            return pc
        except ImportError:
            logger.error("❌ Pinecone library not installed")
            raise ImportError("Please install pinecone-client")
        except Exception as e:
            logger.error(f"❌ Pinecone connection failed: {e}")
            raise e

    @staticmethod
    def get_pinecone_connection() -> Any:
        """
        Initializes and returns the Pinecone index object.
        Resolves 'no attribute get_pinecone_connection' error.
        """
        try:
            from pinecone import Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY is not set")

            pc = Pinecone(api_key=api_key)
            index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
            index = pc.Index(index_name)
            logger.info(f"✅ Pinecone index '{index_name}' connection successful")
            return index
        except ImportError:
            logger.error("❌ Pinecone library not installed")
            raise ImportError("Please install pinecone-client")
        except Exception as e:
            logger.error(f"❌ Pinecone connection failed: {e}")
            raise e

    @staticmethod
    def get_embedding_function() -> Callable:
        """
        Returns the embedding function based on provider.
        Fixes the 'mock' provider dependency error.
        """
        provider = os.getenv("EMBEDDING_PROVIDER", "mock").lower()

        if provider == "mock":
            logger.info("🔧 Using mock embedding function (768 dims)")
            return lambda x: [0.1] + [0.0] * 767

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
                return lambda x: client.embeddings.create(input=[x], model=model).data[0].embedding
            except Exception as e:
                logger.error(f"❌ OpenAI Embedding initialization failed: {e}")
                return lambda x: [0.0] * 768

        return lambda x: [0.0] * 768

    @staticmethod
    def get_redis_client() -> Any:
        """
        Alias for get_redis_connection for backward compatibility.
        """
        return ConnectionFactory.get_redis_connection()

    @property
    def get_embedding(self) -> Callable:
        """
        Alias for get_embedding_function for backward compatibility.
        Returns the embedding function directly when accessed as property.
        """
        return ConnectionFactory.get_embedding_function()

    @staticmethod
    def create_redis_index(schema: Optional[Any] = None) -> SearchIndex:
        """
        Creates a RedisVL SearchIndex.
        Requires Redis Stack (RediSearch) to avoid FT._LIST errors.
        """
        index_name = os.getenv("REDIS_INDEX_NAME", "canon_index")
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

        # Default schema if none provided
        if not schema:
            schema = {
                "index": {"name": index_name, "prefix": "canon"},
                "fields": [
                    {"name": "content", "type": "text"},
                    {"name": "vector", "type": "vector", "attrs": {"dims": 768, "algorithm": "hnsw"}}
                ]
            }

        try:
            index = SearchIndex.from_dict(schema)
            index.connect(redis_url)

            # This triggers FT._LIST internally
            if not index.exists():
                index.create(overwrite=True)
                logger.info(f"📁 Created new Redis index: {index_name}")
            else:
                logger.info(f"📂 Connected to existing Redis index: {index_name}")

            return index
        except Exception as e:
            logger.error(f"❌ Failed to create Redis index: {e}")
            raise e

# Backward compatibility aliases
ConnectionManager = ConnectionFactory
ConnectionFactory.get_redis_client = staticmethod(ConnectionFactory.get_redis_connection)
ConnectionFactory.get_redis_index = staticmethod(ConnectionFactory.create_redis_index)
ConnectionFactory.get_pinecone_index = staticmethod(ConnectionFactory.get_pinecone_connection)

