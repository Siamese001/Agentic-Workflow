"""
Atomic Blackboard - Thread-Safe State Management for Canon Validator

This module provides the central "Blackboard" pattern for managing validation state
across concurrent healing operations. Features:

- Lease-based locking to prevent race conditions
- Health score tracking per file
- Regression guard to prevent error increases
- Redis (HOT BRAIN) for fast caching and locks
- Pinecone (DEEP BRAIN) for pattern learning
"""
import os
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class FileHealthScore:
    """Health score for a single file."""
    file_path: str
    current_violations: int
    last_healed_timestamp: float
    healing_attempts: int = 0
    last_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'file_path': self.file_path,
            'current_violations': self.current_violations,
            'last_healed_timestamp': self.last_healed_timestamp,
            'healing_attempts': self.healing_attempts,
            'last_hash': self.last_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileHealthScore':
        """Create from dictionary."""
        return cls(
            file_path=data['file_path'],
            current_violations=data['current_violations'],
            last_healed_timestamp=data['last_healed_timestamp'],
            healing_attempts=data.get('healing_attempts', 0),
            last_hash=data.get('last_hash', '')
        )


@dataclass
class HealingLease:
    """Represents a healing lease on a file."""
    file_path: str
    agent_name: str
    acquired_at: float
    expires_at: float
    lease_id: str
    
    def is_expired(self) -> bool:
        """Check if lease has expired."""
        return time.time() > self.expires_at
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        return max(0, self.expires_at - time.time())


class AtomicBlackboard:
    """
    Thread-safe blackboard for managing validation state.
    
    Features:
    - Lease-based file locking (30-second default)
    - Health score tracking per file
    - Regression guard (rejects fixes that increase errors)
    - Redis for hot caching and locks
    - Pinecone for pattern learning
    """
    
    def __init__(self, redis_client=None, pinecone_index=None):
        """
        Initialize blackboard.
        
        Args:
            redis_client: Redis client for hot caching
            pinecone_index: Pinecone index for pattern learning
        """
        self.redis_client = redis_client
        self.pinecone_index = pinecone_index
        self.redis_fallback: Dict[str, Any] = {}  # Local fallback if Redis unavailable
        
        # Lease configuration
        self.lease_duration = int(os.getenv('HEALING_LEASE_DURATION', '30'))  # 30 seconds
        self.max_backoff = int(os.getenv('MAX_LEASE_BACKOFF', '60'))  # 60 seconds max wait
        
        # Health score configuration
        self.health_score_ttl = int(os.getenv('HEALTH_SCORE_TTL', '86400'))  # 24 hours
    
    # ============================================================================
    # LEASE LOCKING SYSTEM
    # ============================================================================
    
    def acquire_lease(self, file_path: str, agent_name: str) -> Optional[HealingLease]:
        """
        Acquire a healing lease on a file.
        
        Args:
            file_path: Path to file to lock
            agent_name: Name of agent requesting lease
            
        Returns:
            HealingLease if acquired, None if file is locked
        """
        lock_key = f"lock:{file_path}"
        lease_id = f"{agent_name}:{time.time()}"
        
        acquired_at = time.time()
        expires_at = acquired_at + self.lease_duration
        
        if self.redis_client:
            try:
                # Try to set lock with NX (only if not exists) and EX (expiration)
                acquired = self.redis_client.set(
                    lock_key,
                    lease_id,
                    nx=True,  # Only set if key doesn't exist
                    ex=self.lease_duration  # Expire after lease_duration seconds
                )
                
                if acquired:
                    return HealingLease(
                        file_path=file_path,
                        agent_name=agent_name,
                        acquired_at=acquired_at,
                        expires_at=expires_at,
                        lease_id=lease_id
                    )
                else:
                    # Lock exists, check who owns it
                    existing_lease = self.redis_client.get(lock_key)
                    if existing_lease:
                        print(f"      🔒 File locked by {existing_lease.split(':')[0]}")
                    return None
            except Exception as e:
                print(f"      ⚠️ Redis lease acquisition failed: {e}")
                # Fall through to local fallback
        
        # Local fallback (not thread-safe across processes)
        if lock_key not in self.redis_fallback:
            self.redis_fallback[lock_key] = {
                'lease_id': lease_id,
                'expires_at': expires_at
            }
            return HealingLease(
                file_path=file_path,
                agent_name=agent_name,
                acquired_at=acquired_at,
                expires_at=expires_at,
                lease_id=lease_id
            )
        else:
            # Check if existing lease expired
            existing = self.redis_fallback[lock_key]
            if time.time() > existing['expires_at']:
                # Expired, acquire it
                self.redis_fallback[lock_key] = {
                    'lease_id': lease_id,
                    'expires_at': expires_at
                }
                return HealingLease(
                    file_path=file_path,
                    agent_name=agent_name,
                    acquired_at=acquired_at,
                    expires_at=expires_at,
                    lease_id=lease_id
                )
            return None
    
    def release_lease(self, lease: HealingLease) -> bool:
        """
        Release a healing lease.
        
        Args:
            lease: Lease to release
            
        Returns:
            True if released successfully
        """
        lock_key = f"lock:{lease.file_path}"
        
        if self.redis_client:
            try:
                # Only delete if we own the lock
                existing = self.redis_client.get(lock_key)
                if existing == lease.lease_id:
                    self.redis_client.delete(lock_key)
                    return True
                return False
            except Exception as e:
                print(f"      ⚠️ Redis lease release failed: {e}")
                # Fall through to local fallback
        
        # Local fallback
        if lock_key in self.redis_fallback:
            if self.redis_fallback[lock_key]['lease_id'] == lease.lease_id:
                del self.redis_fallback[lock_key]
                return True
        return False
    
    def extend_lease(self, lease: HealingLease, additional_seconds: int = None) -> bool:
        """
        Extend an existing lease.
        
        Args:
            lease: Lease to extend
            additional_seconds: Additional seconds to add (default: lease_duration)
            
        Returns:
            True if extended successfully
        """
        if additional_seconds is None:
            additional_seconds = self.lease_duration
        
        lock_key = f"lock:{lease.file_path}"
        
        if self.redis_client:
            try:
                # Only extend if we own the lock
                existing = self.redis_client.get(lock_key)
                if existing == lease.lease_id:
                    self.redis_client.expire(lock_key, additional_seconds)
                    lease.expires_at = time.time() + additional_seconds
                    return True
                return False
            except Exception as e:
                print(f"      ⚠️ Redis lease extension failed: {e}")
                # Fall through to local fallback
        
        # Local fallback
        if lock_key in self.redis_fallback:
            if self.redis_fallback[lock_key]['lease_id'] == lease.lease_id:
                self.redis_fallback[lock_key]['expires_at'] = time.time() + additional_seconds
                lease.expires_at = time.time() + additional_seconds
                return True
        return False
    
    def wait_for_lease(self, file_path: str, agent_name: str, max_wait: int = None) -> Optional[HealingLease]:
        """
        Wait for a lease with exponential backoff.
        
        Args:
            file_path: Path to file to lock
            agent_name: Name of agent requesting lease
            max_wait: Maximum seconds to wait (default: max_backoff)
            
        Returns:
            HealingLease if acquired, None if timeout
        """
        if max_wait is None:
            max_wait = self.max_backoff
        
        backoff = 1  # Start with 1 second
        total_waited = 0
        
        while total_waited < max_wait:
            lease = self.acquire_lease(file_path, agent_name)
            if lease:
                return lease
            
            # Exponential backoff
            wait_time = min(backoff, max_wait - total_waited)
            print(f"      ⏳ Waiting {wait_time}s for lease on {os.path.basename(file_path)}...")
            time.sleep(wait_time)
            
            total_waited += wait_time
            backoff *= 2  # Double the backoff
        
        print(f"      ⏰ Timeout waiting for lease on {os.path.basename(file_path)}")
        return None
    
    # ============================================================================
    # HEALTH SCORE TRACKING
    # ============================================================================
    
    def get_health_score(self, file_path: str) -> Optional[FileHealthScore]:
        """
        Get health score for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileHealthScore if exists, None otherwise
        """
        score_key = f"health:{file_path}"
        
        if self.redis_client:
            try:
                data = self.redis_client.get(score_key)
                if data:
                    return FileHealthScore.from_dict(json.loads(data))
            except Exception as e:
                print(f"      ⚠️ Redis health score retrieval failed: {e}")
                # Fall through to local fallback
        
        # Local fallback
        if score_key in self.redis_fallback:
            return FileHealthScore.from_dict(self.redis_fallback[score_key])
        
        return None
    
    def update_health_score(
        self,
        file_path: str,
        current_violations: int,
        file_hash: str = ""
    ) -> FileHealthScore:
        """
        Update health score for a file.
        
        Args:
            file_path: Path to file
            current_violations: Current number of violations
            file_hash: Hash of file content
            
        Returns:
            Updated FileHealthScore
        """
        score_key = f"health:{file_path}"
        
        # Get existing score or create new
        existing = self.get_health_score(file_path)
        
        if existing:
            score = FileHealthScore(
                file_path=file_path,
                current_violations=current_violations,
                last_healed_timestamp=time.time(),
                healing_attempts=existing.healing_attempts + 1,
                last_hash=file_hash
            )
        else:
            score = FileHealthScore(
                file_path=file_path,
                current_violations=current_violations,
                last_healed_timestamp=time.time(),
                healing_attempts=1,
                last_hash=file_hash
            )
        
        # Store in Redis or fallback
        if self.redis_client:
            try:
                self.redis_client.setex(
                    score_key,
                    self.health_score_ttl,
                    json.dumps(score.to_dict())
                )
            except Exception as e:
                print(f"      ⚠️ Redis health score update failed: {e}")
                # Fall through to local fallback
                self.redis_fallback[score_key] = score.to_dict()
        else:
            self.redis_fallback[score_key] = score.to_dict()
        
        return score
    
    # ============================================================================
    # REGRESSION GUARD
    # ============================================================================
    
    def check_regression(
        self,
        file_path: str,
        new_violations: int,
        new_hash: str
    ) -> Tuple[bool, str]:
        """
        Check if a mutation would cause regression (increase errors).
        
        Args:
            file_path: Path to file
            new_violations: Number of violations after fix
            new_hash: Hash of new file content
            
        Returns:
            Tuple of (is_valid, reason)
        """
        existing = self.get_health_score(file_path)
        
        if not existing:
            # No previous score, accept the change
            return True, "No previous health score"
        
        # Check if violations increased
        if new_violations > existing.current_violations:
            increase = new_violations - existing.current_violations
            return False, f"Regression: Violations increased by {increase} ({existing.current_violations} → {new_violations})"
        
        # Check if file hash is same (no actual change)
        if new_hash and new_hash == existing.last_hash:
            return False, "No change: File hash unchanged"
        
        return True, f"Improvement: Violations decreased from {existing.current_violations} to {new_violations}"
    
    def revert_file(self, file_path: str, backup_content: str) -> bool:
        """
        Revert file to previous content after regression detected.
        
        Args:
            file_path: Path to file
            backup_content: Previous file content to restore
            
        Returns:
            True if reverted successfully
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"      ↩️  Reverted {os.path.basename(file_path)} due to regression")
            return True
        except Exception as e:
            print(f"      ❌ Failed to revert {file_path}: {e}")
            return False
    
    # ============================================================================
    # PATTERN LEARNING (PINECONE DEEP BRAIN)
    # ============================================================================
    
    def store_healing_pattern(
        self,
        violation_key: int,
        violation_desc: str,
        fix_code: str,
        success_rate: float = 1.0
    ):
        """
        Store successful healing pattern in Pinecone.
        
        Args:
            violation_key: Canon key that was fixed
            violation_desc: Description of violation
            fix_code: The successful fix
            success_rate: Success rate of this pattern (0.0-1.0)
        """
        if not self.pinecone_index:
            return
        
        try:
            import openai
            
            # Create embedding of the violation description
            text = f"Canon Key {violation_key}: {violation_desc}"
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            
            # Store in Pinecone
            pattern_id = f"pattern_{violation_key}_{hash(text)}"
            self.pinecone_index.upsert([
                {
                    'id': pattern_id,
                    'values': embedding,
                    'metadata': {
                        'violation_key': violation_key,
                        'violation_desc': violation_desc,
                        'fix': fix_code[:1000],  # Store first 1000 chars
                        'success_rate': success_rate,
                        'timestamp': time.time()
                    }
                }
            ])
            print(f"      💾 Stored healing pattern for Key {violation_key} in Pinecone")
        except Exception as e:
            print(f"      ⚠️ Failed to store pattern in Pinecone: {e}")
    
    def find_similar_patterns(
        self,
        violation_desc: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find similar healing patterns from Pinecone.
        
        Args:
            violation_desc: Description of current violation
            top_k: Number of similar patterns to return
            
        Returns:
            List of similar patterns with metadata
        """
        if not self.pinecone_index:
            return []
        
        try:
            import openai
            
            # Create embedding of the violation description
            response = openai.Embedding.create(
                input=violation_desc,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            
            # Query Pinecone
            results = self.pinecone_index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract patterns
            patterns = []
            for match in results.matches:
                patterns.append({
                    'score': match.score,
                    'violation_key': match.metadata.get('violation_key'),
                    'violation_desc': match.metadata.get('violation_desc'),
                    'fix': match.metadata.get('fix'),
                    'success_rate': match.metadata.get('success_rate', 1.0)
                })
            
            return patterns
        except Exception as e:
            print(f"      ⚠️ Failed to query Pinecone: {e}")
            return []
    
    # ============================================================================
    # CACHING (REDIS HOT BRAIN)
    # ============================================================================
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached validation result."""
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                return json.loads(cached) if cached else None
            except:
                pass
        
        return self.redis_fallback.get(cache_key)
    
    def cache_result(self, cache_key: str, result: Dict, ttl: int = 3600):
        """Cache validation result."""
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, ttl, json.dumps(result))
                return
            except:
                pass
        
        self.redis_fallback[cache_key] = result
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get blackboard statistics."""
        stats = {
            'redis_connected': self.redis_client is not None,
            'pinecone_connected': self.pinecone_index is not None,
            'fallback_entries': len(self.redis_fallback),
            'lease_duration': self.lease_duration,
            'max_backoff': self.max_backoff
        }
        
        if self.redis_client:
            try:
                stats['redis_keys'] = self.redis_client.dbsize()
            except:
                pass
        
        return stats
