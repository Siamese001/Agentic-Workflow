"""
Canon Validator Service Manager
Manages external services (Redis, Pinecone, MCP) with graceful fallback.
"""
from typing import Any, Optional, Protocol, Dict, List


import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ServiceManager:
    """Manages external services (Redis, Pinecone, MCP) with graceful fallback."""
    redis_client: Optional[Any] = field(default=None)
    pinecone_index: Optional[Any] = field(default=None)
    mcp_clients: Dict[str, Any] = field(default_factory=dict)
    redis_fallback: Dict[str, Any] = field(default_factory=dict)
    mcp_init_pending: bool = field(default=False)
    
    def __post_init__(self):
        """Initialize services if available."""
        print("\n🔌 Initializing External Services...", flush=True)
        try:
            self._init_redis()
        except Exception as e:
            print(f"   [!]  Redis init failed: {e}", flush=True)
        
        try:
            self._init_pinecone()
        except Exception as e:
            print(f"   [!]  Pinecone init failed: {e}", flush=True)
        
        try:
            self._init_mcp()
        except Exception as e:
            print(f"   [!]  MCP init failed: {e}", flush=True)
    
    def _init_redis(self):
        """Initialize Redis client if available."""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
            self.redis_client.ping()
            print("   [OK] Redis connected - caching enabled")
        except Exception as e:
            if "10061" in str(e):
                print("   [!]  Redis connection refused (10061) - falling back to local cache")
                self.redis_client = None
                self.redis_fallback = {}
            else:
                self.redis_client = None
                print(f"   [!]  Redis unavailable: {e}")
    
    def _init_pinecone(self):
        """Initialize Pinecone for pattern learning."""
        try:
            from pinecone import Pinecone, ServerlessSpec
            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            
            index_name = "canon-memory-l2"
            cloud = "aws"
            region = "us-east-1"
            dimension = int(os.getenv('PINECONE_DIMENSION', '1536'))
            metric = os.getenv('PINECONE_METRIC', 'cosine')
            
            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(cloud=cloud, region=region)
                )
            self.pinecone_index = pc.Index(index_name)
            print(f"   [OK] Pinecone connected - pattern learning enabled ({region})")
        except Exception as e:
            self.pinecone_index = None
            print(f"   [!]  Pinecone unavailable: {e}")
    
    def _init_mcp(self):
        """Initialize MCP clients if available."""
        self.mcp_init_pending = True
    
    async def init_mcp_async(self):
        """Async initialization of MCP clients for Level 5 Swarm with full MCP bridge."""
        if not self.mcp_init_pending:
            return
        
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            print("   [!]  MCP not installed - using direct file I/O")
            self.mcp_init_pending = False
            return
        
        mcp_servers = {
            'file_server': {
                'command': 'python',
                'args': ['apps_shared/mcp_file_server.py'],
                'required': False
            },
            'gitkraken': {
                'type': 'windsurf',
                'server_name': 'GitKraken',
                'required': False
            },
            'brave_search': {
                'type': 'windsurf',
                'server_name': 'brave-search',
                'required': False,
                'env': {'BRAVE_SEARCH_API_KEY': os.getenv('BRAVE_SEARCH_API_KEY', '')}
            },
            'deepwiki': {
                'type': 'windsurf',
                'server_name': 'deepwiki',
                'required': False
            },
            'fetch': {
                'type': 'windsurf',
                'server_name': 'fetch',
                'required': False
            },
            'figma': {
                'type': 'windsurf',
                'server_name': 'figma-remote-mcp-server',
                'required': False,
                'env': {'FIGMA_TOKEN': os.getenv('FIGMA_TOKEN', '')}
            },
            'filesystem': {
                'type': 'windsurf',
                'server_name': 'filesystem',
                'required': False
            },
            'playwright': {
                'type': 'windsurf',
                'server_name': 'mcp-playwright',
                'required': False
            },
            'memory': {
                'type': 'windsurf',
                'server_name': 'memory',
                'required': False
            },
            'pinecone': {
                'type': 'windsurf',
                'server_name': 'pinecone-mcp-server',
                'required': False,
                'env': {'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY', '')}
            },
            'redis': {
                'type': 'windsurf',
                'server_name': 'redis',
                'required': False
            },
            'sequential_thinking': {
                'type': 'windsurf',
                'server_name': 'sequential-thinking',
                'required': False
            }
        }
        
        connected_servers = []
        windsurf_servers = []
        
        for server_name, config in mcp_servers.items():
            try:
                if 'env' in config:
                    missing_vars = [k for k, v in config['env'].items() if not v]
                    if missing_vars:
                        print(f"   [!]  {server_name} MCP skipped - missing env vars: {missing_vars}")
                        continue
                
                if config.get('type') == 'windsurf':
                    self.mcp_clients[server_name] = {
                        'type': 'windsurf',
                        'server_name': config['server_name'],
                        'available': True
                    }
                    windsurf_servers.append(server_name)
                    continue
                
                server_params = StdioServerParameters(
                    command=config['command'],
                    args=config['args'],
                    env=config.get('env')
                )
                
                async with asyncio.timeout(5.0):
                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            self.mcp_clients[server_name] = session
                            connected_servers.append(server_name)
                            
            except asyncio.TimeoutError:
                if config.get('required'):
                    print(f"   [!]  {server_name} MCP timed out - required server unavailable")
                    self.mcp_init_pending = False
                    return
            except FileNotFoundError:
                pass
            except Exception as e:
                if config.get('required'):
                    print(f"   [!]  {server_name} MCP failed: {e}")
                    self.mcp_init_pending = False
                    return
        
        all_servers = connected_servers + windsurf_servers
        if all_servers:
            status_msg = f"   [OK] MCP initialized - Connected: {', '.join(connected_servers)}"
            if windsurf_servers:
                status_msg += f" | Windsurf: {', '.join(windsurf_servers)}"
            print(status_msg)
        else:
            print("   [!]  No MCP servers connected - using direct file I/O")
        
        self.mcp_init_pending = False
    
    def get_cached_result(self, file_hash: str) -> Optional[Dict]:
        """Get cached validation result from Redis or fallback dict."""
        if self.redis_client:
            try:
                cached = self.redis_client.get(f"canon:validation:{file_hash}")
                return json.loads(cached) if cached else None
            except:
                pass
        return self.redis_fallback.get(f"canon:validation:{file_hash}")
    
    def cache_result(self, file_hash: str, result: Dict, ttl: int = None):
        """Cache validation result in Redis or fallback dict."""
        if ttl is None:
            ttl = int(os.getenv('CACHE_TTL', '3600'))
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"canon:validation:{file_hash}",
                    ttl,
                    json.dumps(result)
                )
            except:
                pass
        else:
            self.redis_fallback[f"canon:validation:{file_hash}"] = result
    
    def store_healing_pattern(self, violation: str, fix: str, success_rate: float):
        """Store successful healing pattern in Pinecone."""
        if not self.pinecone_index:
            return
        try:
            import openai
            text = f"Violation: {violation}\nFix: {fix}"
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            
            self.pinecone_index.upsert([{
                'id': f"pattern_{hash(text)}",
                'values': embedding,
                'metadata': {
                    'violation': violation,
                    'fix': fix,
                    'success_rate': success_rate,
                    'timestamp': time.time()
                }
            }])
        except:
            pass
    
    def find_similar_patterns(self, violation: str, top_k: int = None) -> List[Dict]:
        """Find similar healing patterns for a violation."""
        if top_k is None:
            top_k = int(os.getenv('PATTERN_MATCH_TOP_K', '3'))
        if not self.pinecone_index:
            return []
        try:
            import openai
            response = openai.Embedding.create(
                input=violation,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            
            results = self.pinecone_index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [{
                'fix': match['metadata']['fix'],
                'success_rate': match['metadata']['success_rate'],
                'similarity': match['score']
            } for match in results['matches']]
        except:
            return []
    
    def validate_ui_patterns(self, design_spec: Dict) -> List[str]:
        """Validate UI patterns using Figma MCP."""
        if 'figma' not in self.mcp_clients:
            return []
        try:
            figma_client = self.mcp_clients['figma']
            violations = []
            
            if 'components' in design_spec:
                for component in design_spec['components']:
                    if not figma_client.validate_component(component):
                        violations.append(f"Invalid component: {component['name']}")
            
            return violations
        except:
            return []
