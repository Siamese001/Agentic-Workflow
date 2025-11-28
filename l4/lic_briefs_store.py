"""LIC Briefs Store - L4 memory/state for strategic briefs storage and retrieval.

Implements nuclear prompt requirements for deterministic briefs storage:
- Store and retrieve strategic briefs derived from LIC research for reuse
- L4 only: may use existing persistence abstractions
- Async interface for brief management operations
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LICBrief:
    """Strategic brief derived from LIC research."""
    id: str                              # unique brief identifier
    company_name: str                    # target company name
    role_title: str                      # target role title
    content: str                         # brief content/summary
    tags: List[str]                      # searchable tags
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICBriefsStore:
    """L4 memory store for LIC strategic briefs.
    
    Provides async interface for storing and retrieving briefs
    using existing persistence abstractions.
    """
    
    def __init__(self, persistence_client: Optional[Any] = None) -> None:
        """Initialize LIC briefs store with persistence client."""
        self.persistence_client = persistence_client
        
        if not self.persistence_client:
            logger.warning("No persistence client provided to LICBriefsStore - operations will be no-ops")
    
    async def save_brief(self, brief: LICBrief) -> None:
        """Save a strategic brief to persistent storage.
        
        Args:
            brief: The brief to save
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - skipping save")
            return
        
        try:
            # Prepare brief for persistence
            brief_data = {
                "id": brief.id,
                "company_name": brief.company_name,
                "role_title": brief.role_title,
                "content": brief.content,
                "tags": brief.tags,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    **brief.metadata,
                },
            }
            
            # Use existing persistence client save interface
            await self.persistence_client.save(
                key=f"lic_brief:{brief.id}",
                data=brief_data,
            )
            
            # Also save by company for efficient lookup
            company_key = f"lic_briefs_by_company:{brief.company_name.lower()}"
            existing_briefs = await self.persistence_client.get(company_key) or {"brief_ids": []}
            if brief.id not in existing_briefs["brief_ids"]:
                existing_briefs["brief_ids"].append(brief.id)
                await self.persistence_client.save(key=company_key, data=existing_briefs)
            
            logger.debug(f"Saved brief {brief.id} for {brief.company_name}")
            
        except Exception as e:
            logger.error(f"Failed to save brief {brief.id}: {e}")
    
    async def get_briefs_for_company(self, company_name: str) -> List[LICBrief]:
        """Get all briefs for a specific company.
        
        Args:
            company_name: The company name to search for
            
        Returns:
            List of briefs for the specified company
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - returning empty list")
            return []
        
        try:
            # Get brief IDs for this company
            company_key = f"lic_briefs_by_company:{company_name.lower()}"
            company_data = await self.persistence_client.get(company_key)
            
            if not company_data or not company_data.get("brief_ids"):
                return []
            
            # Retrieve each brief
            briefs = []
            for brief_id in company_data["brief_ids"]:
                brief = await self.get_brief(brief_id)
                if brief:
                    briefs.append(brief)
            
            logger.debug(f"Retrieved {len(briefs)} briefs for {company_name}")
            return briefs
            
        except Exception as e:
            logger.error(f"Failed to get briefs for company {company_name}: {e}")
            return []
    
    async def get_brief(self, brief_id: str) -> Optional[LICBrief]:
        """Get a specific brief by ID.
        
        Args:
            brief_id: The ID of the brief to retrieve
            
        Returns:
            The brief if found, None otherwise
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - cannot get brief")
            return None
        
        try:
            # Retrieve brief data from persistence
            brief_data = await self.persistence_client.get(f"lic_brief:{brief_id}")
            
            if not brief_data:
                return None
            
            # Convert back to LICBrief object
            brief = LICBrief(
                id=brief_data["id"],
                company_name=brief_data["company_name"],
                role_title=brief_data["role_title"],
                content=brief_data["content"],
                tags=brief_data["tags"],
                metadata=brief_data.get("metadata", {}),
            )
            
            return brief
            
        except Exception as e:
            logger.error(f"Failed to get brief {brief_id}: {e}")
            return None
    
    async def search_briefs_by_tags(self, tags: List[str]) -> List[LICBrief]:
        """Search briefs by tags.
        
        Args:
            tags: List of tags to search for
            
        Returns:
            List of briefs matching the specified tags
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - returning empty list")
            return []
        
        if not tags:
            return []
        
        try:
            # This is a simplified implementation - in practice, you'd want
            # a more efficient search using indexes or a search service
            all_briefs = await self._get_all_briefs()
            
            # Filter by tag matches
            matching_briefs = []
            tags_lower = [tag.lower() for tag in tags]
            
            for brief in all_briefs:
                brief_tags_lower = [tag.lower() for tag in brief.tags]
                if any(tag in brief_tags_lower for tag in tags_lower):
                    matching_briefs.append(brief)
            
            logger.debug(f"Found {len(matching_briefs)} briefs matching tags {tags}")
            return matching_briefs
            
        except Exception as e:
            logger.error(f"Failed to search briefs by tags {tags}: {e}")
            return []
    
    async def delete_brief(self, brief_id: str) -> None:
        """Delete a brief by ID.
        
        Args:
            brief_id: The ID of the brief to delete
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - skipping delete")
            return
        
        try:
            # Get the brief first to update company index
            brief = await self.get_brief(brief_id)
            if not brief:
                return
            
            # Delete the brief
            await self.persistence_client.delete(f"lic_brief:{brief_id}")
            
            # Update company index
            company_key = f"lic_briefs_by_company:{brief.company_name.lower()}"
            company_data = await self.persistence_client.get(company_key)
            
            if company_data and brief_id in company_data.get("brief_ids", []):
                company_data["brief_ids"].remove(brief_id)
                await self.persistence_client.save(key=company_key, data=company_data)
            
            logger.debug(f"Deleted brief {brief_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete brief {brief_id}: {e}")
    
    async def update_brief(self, brief: LICBrief) -> None:
        """Update an existing brief.
        
        Args:
            brief: The brief to update (must have existing ID)
        """
        if not self.persistence_client:
            logger.debug("No persistence client available - skipping update")
            return
        
        try:
            # Check if brief exists
            existing = await self.get_brief(brief.id)
            if not existing:
                logger.warning(f"Brief {brief.id} not found for update")
                return
            
            # Update with new timestamp
            brief.metadata["updated_at"] = datetime.now().isoformat()
            
            # Save the updated brief
            await self.save_brief(brief)
            
            logger.debug(f"Updated brief {brief.id}")
            
        except Exception as e:
            logger.error(f"Failed to update brief {brief.id}: {e}")
    
    async def _get_all_briefs(self) -> List[LICBrief]:
        """Get all briefs (internal helper method)."""
        if not self.persistence_client:
            return []
        
        try:
            # This is a simplified implementation - in practice, you'd want
            # to maintain a global index or use a more efficient method
            all_briefs = []
            
            # Scan through all brief keys (this is inefficient for large datasets)
            # In a real implementation, you'd maintain an index
            keys = await self.persistence_client.list_keys("lic_brief:")
            
            for key in keys:
                brief_id = key.replace("lic_brief:", "")
                brief = await self.get_brief(brief_id)
                if brief:
                    all_briefs.append(brief)
            
            return all_briefs
            
        except Exception as e:
            logger.error(f"Failed to get all briefs: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the briefs store connection.
        
        Returns:
            Health status information
        """
        health_status = {
            "available": self.persistence_client is not None,
            "connected": False,
            "error": None,
            "total_briefs": 0,
        }
        
        if not self.persistence_client:
            health_status["error"] = "No persistence client configured"
            return health_status
        
        try:
            # Attempt a simple operation to check connectivity
            await self.persistence_client.get("health_check")
            health_status["connected"] = True
            
            # Count total briefs
            all_briefs = await self._get_all_briefs()
            health_status["total_briefs"] = len(all_briefs)
            
        except Exception as e:
            health_status["connected"] = False
            health_status["error"] = str(e)
            logger.error(f"Briefs store health check failed: {e}")
        
        return health_status
