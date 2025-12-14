"""
Connection Manager - Connectivity-Hardened Canon Validator

Robust connectivity handling for RedisVL (L1) and Pinecone (L2)
with proper error handling and authentication.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import required libraries
try:
    from redisvl.index import SearchIndex
    from redisvl.query import VectorQuery
    from redisvl.redis.connection import RedisConnection
    from redisvl.redis.utils import make_vector_key
    REDISVL_AVAILABLE = True
except ImportError:
    REDISVL_AVAILABLE = False
    RedisConnection = None  # Define as None if not available
    SearchIndex = None
    VectorQuery = None
    logging.warning("redisvl not installed - Redis functionality will be limited")

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    Pinecone = None  # Define as None if not available
    ServerlessSpec = None
    logging.warning("pinecone not installed - Pinecone functionality will be disabled")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not installed - using mock embeddings")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai not installed - OpenAI embeddings unavailable")

logger = logging.getLogger(__name__)


class ConnectionFactory:
    """
    Factory class for creating and managing database connections.
    
    Provides robust connection handling with retry logic and proper
    error handling for both RedisVL and Pinecone.
    """
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_redis_connection(cls) -> Union[RedisConnection, Any]:
        """
        Initialize and return RedisVL connection.
        
        Returns:
            RedisConnection instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if "redis" not in cls._instances:
            cls._instances["redis"] = cls._create_redis_connection()
        return cls._instances["redis"]
    
    @classmethod
    def _create_redis_connection(cls) -> RedisConnection:
        """Create Redis connection with retry logic."""
        if not REDISVL_AVAILABLE:
            raise ImportError("redisvl is required. Install with: pip install redisvl")
        
        # Get configuration
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Redis (attempt {attempt + 1}/{max_retries})")
                
                # Create connection
                conn = RedisConnection.from_url(redis_url)
                
                # Test connection
                conn.client.ping()
                
                logger.info("✅ Redis connection successful")
                return conn
                
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise ConnectionError(f"Failed to connect to Redis after {max_retries} attempts")
    
    @classmethod
    def get_pinecone_connection(cls) -> Union[Pinecone, Any]:
        """
        Initialize and return Pinecone connection.
        
        Returns:
            Pinecone instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if "pinecone" not in cls._instances:
            cls._instances["pinecone"] = cls._create_pinecone_connection()
        return cls._instances["pinecone"]
    
    @classmethod
    def _create_pinecone_connection(cls) -> Pinecone:
        """Create Pinecone connection with index management."""
        if not PINECONE_AVAILABLE:
            raise ImportError("pinecone-client is required. Install with: pip install pinecone-client")
        
        # Get configuration
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        env = os.getenv("PINECONE_ENV", "us-east-1-aws")
        index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        dimension = int(os.getenv("PINECONE_DIMENSION", "768"))
        
        try:
            logger.info("Connecting to Pinecone...")
            
            # Initialize Pinecone
            pc = Pinecone(api_key=api_key)
            
            # Check if index exists
            if index_name not in pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=env.split("-")[-2] if "-" in env else "us-east-1"
                    )
                )
                
                # Wait for index to be ready
                while not pc.describe_index(index_name).status['ready']:
                    time.sleep(1)
            
            logger.info("✅ Pinecone connection successful")
            return pc
            
        except Exception as e:
            logger.error(f"❌ Pinecone connection failed: {e}")
            raise ConnectionError(f"Failed to connect to Pinecone: {e}")
    
    @classmethod
    def get_embedding_function(cls) -> Callable[[str], List[float]]:
        """
        Get embedding function based on configuration.
        
        Returns:
            Function that converts text to embedding vector
        """
        provider = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
        
        if provider == "openai" and OPENAI_AVAILABLE:
            return cls._create_openai_embedding_function()
        elif provider == "sentence-transformers" and SENTENCE_TRANSFORMERS_AVAILABLE:
            return cls._create_sentence_transformer_function()
        else:
            logger.warning(f"Using mock embeddings - {provider} not available")
            return cls._create_mock_embedding_function()
    
    @classmethod
    def _create_openai_embedding_function(cls) -> Callable[[str], List[float]]:
        """Create OpenAI embedding function."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY required for OpenAI embeddings")
        
        client = openai.OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        def embed(text: str) -> List[float]:
            response = client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        
        return embed
    
    @classmethod
    def _create_sentence_transformer_function(cls) -> Callable[[str], List[float]]:
        """Create sentence transformer embedding function."""
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        logger.info(f"Loading sentence transformer model: {model_name}")
        model = SentenceTransformer(model_name)
        
        def embed(text: str) -> List[float]:
            return model.encode(text).tolist()
        
        return embed
    
    @classmethod
    def _create_mock_embedding_function(cls) -> Callable[[str], List[float]]:
        """Create mock embedding function for testing."""
        import hashlib
        
        def embed(text: str) -> List[float]:
            # Generate deterministic but pseudo-random embeddings
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert to 768-dimensional float array
            embedding = []
            for i in range(0, min(len(hash_bytes), 96), 4):
                chunk = hash_bytes[i:i+4]
                val = int.from_bytes(chunk, byteorder='big', signed=True)
                normalized = val / (2**31)
                embedding.extend([normalized] * 8)  # Repeat to reach 768
            
            # Pad or truncate to exactly 768 dimensions
            while len(embedding) < 768:
                embedding.append(0.0)
            return embedding[:768]
        
        return embed
    
    @classmethod
    def create_redis_index(cls, schema: Dict[str, Any]) -> Union[SearchIndex, Any]:
        """
        Create RedisVL search index.
        
        Args:
            schema: Index schema definition
            
        Returns:
            SearchIndex instance
        """
        conn = cls.get_redis_connection()
        
        # Default schema for Canon entries
        if not schema:
            schema = {
                "index": {
                    "name": "canon-index",
                    "prefix": "canon:",
                    "storage_type": "hash"
                },
                "fields": [
                    {"name": "embedding", "type": "vector", "attrs": {
                        "dims": 768,
                        "distance_metric": "cosine",
                        "algorithm": "HNSW",
                        "M": 16,
                        "EF_CONSTRUCTION": 128
                    }},
                    {"name": "failure_count", "type": "numeric"},
                    {"name": "success_count", "type": "numeric"},
                    {"name": "project_context", "type": "tag"},
                    {"name": "canon_rule_id", "type": "tag"},
                    {"name": "last_validated", "type": "numeric"}
                ]
            }
        
        try:
            index = SearchIndex.from_dict(schema)
            index.create(overwrite=True)
            logger.info(f"✅ Created Redis index: {schema['index']['name']}")
            return index
        except Exception as e:
            logger.error(f"❌ Failed to create Redis index: {e}")
            raise
    
    @classmethod
    def test_all_connections(cls) -> Dict[str, bool]:
        """
        Test all connections and return status.
        
        Returns:
            Dictionary with connection status
        """
        results = {}
        
        # Test Redis
        try:
            redis = cls.get_redis_connection()
            redis.client.ping()
            results["redis"] = True
            logger.info("✅ Redis connection test passed")
        except Exception as e:
            results["redis"] = False
            logger.error(f"❌ Redis connection test failed: {e}")
        
        # Test Pinecone
        try:
            pinecone = cls.get_pinecone_connection()
            indexes = pinecone.list_indexes()
            results["pinecone"] = True
            logger.info("✅ Pinecone connection test passed")
        except Exception as e:
            results["pinecone"] = False
            logger.error(f"❌ Pinecone connection test failed: {e}")
        
        # Test embedding function
        try:
            embed_func = cls.get_embedding_function()
            test_embedding = embed_func("test")
            if len(test_embedding) == 768:
                results["embeddings"] = True
                logger.info("✅ Embedding function test passed")
            else:
                results["embeddings"] = False
                logger.error(f"❌ Embedding dimension mismatch: {len(test_embedding)}")
        except Exception as e:
            results["embeddings"] = False
            logger.error(f"❌ Embedding function test failed: {e}")
        
        return results
    
    @classmethod
    def reset_connections(cls):
        """Reset all cached connections."""
        cls._instances.clear()
        logger.info("Connection cache reset")
