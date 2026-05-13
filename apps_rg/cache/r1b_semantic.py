"""Semantic cache for section-level resume generation results.

Per W5C scope: Writeback of generated sections to semantic cache for future retrieval.
Enables cache hits on similar sections in future runs.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from typing import Any
from pathlib import Path


# Cache storage path
CACHE_DIR = Path(__file__).parent.parent.parent / "artifacts" / "apps_rg" / "semantic_cache"


def write_section_to_semantic_cache(
    section_id: str,
    cache_key: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Write a generated section to semantic cache.
    
    Enables future retrieval of similar sections based on context matching.
    
    Args:
        section_id: Canonical section ID (headline, executive_summary, etc.)
        cache_key: Deterministic hash key for this section+context combination
        content: Generated section content
        metadata: Additional context (target_company, target_role, timestamp, etc.)
    
    Returns:
        True if write successful, False otherwise
    """
    try:
        # Ensure cache directory exists
        section_cache_dir = CACHE_DIR / section_id
        section_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Build cache entry
        cache_entry = {
            "cache_key": cache_key,
            "section_id": section_id,
            "content": content,
            "metadata": metadata or {},
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "cache_version": "W5C",
        }
        
        # Write to file (key-based naming for direct lookup)
        cache_file = section_cache_dir / f"{cache_key}.json"
        cache_file.write_text(
            json.dumps(cache_entry, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Also write to index for enumeration
        index_file = section_cache_dir / "_index.jsonl"
        with open(index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "cache_key": cache_key,
                "target_company": metadata.get("target_company", "") if metadata else "",
                "target_role": metadata.get("target_role", "") if metadata else "",
                "cached_at": cache_entry["cached_at"],
            }) + "\n")
        
        return True
        
    except Exception as e:
        # Cache writes are non-fatal
        print(f"[SEMANTIC-CACHE-WARNING] Failed to write {section_id}/{cache_key}: {e}")
        return False


def read_section_from_semantic_cache(
    section_id: str,
    cache_key: str,
) -> dict[str, Any] | None:
    """Read a cached section by key.
    
    Args:
        section_id: Canonical section ID
        cache_key: Cache key to lookup
    
    Returns:
        Cache entry dict with 'content', 'metadata', etc., or None if not found
    """
    try:
        cache_file = CACHE_DIR / section_id / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        return json.loads(cache_file.read_text(encoding="utf-8"))
        
    except Exception as e:
        print(f"[SEMANTIC-CACHE-WARNING] Failed to read {section_id}/{cache_key}: {e}")
        return None


def find_similar_cached_sections(
    section_id: str,
    target_company: str,
    target_role: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find cached sections matching similar context.
    
    Simple string matching on company/role for now.
    Future: Use embeddings for semantic similarity.
    
    Args:
        section_id: Section type to search
        target_company: Target company to match
        target_role: Target role to match
        limit: Max results to return
    
    Returns:
        List of matching cache entries (most recent first)
    """
    try:
        index_file = CACHE_DIR / section_id / "_index.jsonl"
        if not index_file.exists():
            return []
        
        matches = []
        
        with open(index_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Simple matching: substring match on company/role
                    company_match = target_company.lower() in entry.get("target_company", "").lower()
                    role_match = target_role.lower() in entry.get("target_role", "").lower()
                    
                    if company_match or role_match:
                        # Load full content
                        full_entry = read_section_from_semantic_cache(
                            section_id, entry["cache_key"]
                        )
                        if full_entry:
                            matches.append(full_entry)
                except json.JSONDecodeError:
                    continue
        
        # Sort by recency and limit
        matches.sort(key=lambda x: x.get("cached_at", ""), reverse=True)
        return matches[:limit]
        
    except Exception as e:
        print(f"[SEMANTIC-CACHE-WARNING] Failed to search {section_id}: {e}")
        return []


def generate_section_cache_key(
    section_id: str,
    target_company: str,
    target_role: str,
    content_fingerprint: str,
) -> str:
    """Generate deterministic cache key for a section context.
    
    Args:
        section_id: Section type
        target_company: Target company
        target_role: Target role
        content_fingerprint: Hash of master resume content that generated this
    
    Returns:
        32-character hex cache key
    """
    key_payload = {
        "section_id": section_id,
        "target_company": target_company,
        "target_role": target_role,
        "content_fingerprint": content_fingerprint,
    }
    
    key_data = json.dumps(key_payload, sort_keys=True)
    return hashlib.sha256(key_data.encode()).hexdigest()[:32]
