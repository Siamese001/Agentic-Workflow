"""
Sovereign Client Stubs - Zero-Loss External Routing

All external I/O (Git, Pinecone, Redis, HTTP) routes through these clients.
Provides: Audit trail, budget enforcement, fallback, isolation.

Usage:
    from agentic_core.sovereign_clients import SovereignGitClient
    client = SovereignGitClient()
    result = client.execute('commit', message='Fix bug')
"""

from .git import SovereignGitClient
from .pinecone import SovereignPineconeClient
from .redis import SovereignRedisClient
from .http import SovereignHttpClient

__all__ = [
    'SovereignGitClient',
    'SovereignPineconeClient',
    'SovereignRedisClient',
    'SovereignHttpClient',
]
