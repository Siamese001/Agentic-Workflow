from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class SenderProfile:
    sender_id: str
    first_name: str
    last_name: str
    title: str
    linkedin_url: str
    created_at: datetime
    updated_at: datetime
    message_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DomainMemory:
    company: str
    industry: str
    insights: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MessageLineage:
    message_id: str
    parent_message_id: Optional[str]
    message_type: str
    recipient_id: str
    timestamp: datetime
    final_output: str
    execution_trace: List[Dict[str, Any]]
    success: bool

class LICMemory:
    def __init__(self):
        self.sender_profiles: Dict[str, SenderProfile] = {}
        self.domain_memories: Dict[str, DomainMemory] = {}
        self.message_lineages: Dict[str, MessageLineage] = {}
        self.state_snapshots: Dict[str, Dict[str, Any]] = {}
        
    def store_sender_profile(self, sender_info: Dict[str, Any]) -> SenderProfile:
        sender_id = sender_info.get("sender_id", f"sender_{datetime.now().timestamp()}")
        
        if sender_id in self.sender_profiles:
            profile = self.sender_profiles[sender_id]
            profile.updated_at = datetime.now()
        else:
            profile = SenderProfile(
                sender_id=sender_id,
                first_name=sender_info.get("first_name", ""),
                last_name=sender_info.get("last_name", ""),
                title=sender_info.get("title", ""),
                linkedin_url=sender_info.get("linkedin_url", ""),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.sender_profiles[sender_id] = profile
            
        return profile
    
    def get_sender_profile(self, sender_id: str) -> Optional[SenderProfile]:
        return self.sender_profiles.get(sender_id)
    
    def store_domain_memory(self, company: str, industry: str, insights: List[Dict[str, Any]]):
        domain_key = f"{company}_{industry}"
        
        if domain_key in self.domain_memories:
            domain_memory = self.domain_memories[domain_key]
            domain_memory.insights.extend(insights)
            domain_memory.last_updated = datetime.now()
        else:
            domain_memory = DomainMemory(
                company=company,
                industry=industry,
                insights=insights
            )
            self.domain_memories[domain_key] = domain_memory
            
        return domain_memory
    
    def get_domain_memory(self, company: str, industry: str) -> Optional[DomainMemory]:
        domain_key = f"{company}_{industry}"
        return self.domain_memories.get(domain_key)
    
    def store_message_lineage(self, message_id: str, parent_message_id: Optional[str], message_type: str, recipient_id: str, final_output: str, execution_trace: List[Dict[str, Any]], success: bool):
        lineage = MessageLineage(
            message_id=message_id,
            parent_message_id=parent_message_id,
            message_type=message_type,
            recipient_id=recipient_id,
            timestamp=datetime.now(),
            final_output=final_output,
            execution_trace=execution_trace,
            success=success
        )
        self.message_lineages[message_id] = lineage
        
        sender_profile = self.get_sender_profile(recipient_id)
        if sender_profile:
            sender_profile.message_history.append({
                "message_id": message_id,
                "message_type": message_type,
                "timestamp": datetime.now().isoformat(),
                "success": success
            })
            
        return lineage
    
    def get_message_lineage(self, message_id: str) -> Optional[MessageLineage]:
        return self.message_lineages.get(message_id)
    
    def save_state_snapshot(self, message_id: str, state_data: Dict[str, Any]):
        snapshot = {
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "state_data": state_data
        }
        self.state_snapshots[message_id] = snapshot
        
    def restore_state_snapshot(self, message_id: str) -> Optional[Dict[str, Any]]:
        snapshot = self.state_snapshots.get(message_id)
        return snapshot["state_data"] if snapshot else None
    
    def get_sender_message_history(self, sender_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        profile = self.get_sender_profile(sender_id)
        if not profile:
            return []
            
        return profile.message_history[-limit:]
    
    def get_company_insights(self, company: str) -> List[Dict[str, Any]]:
        insights = []
        for domain_memory in self.domain_memories.values():
            if domain_memory.company == company:
                insights.extend(domain_memory.insights)
        return insights
    
    def cleanup_old_snapshots(self, days_to_keep: int = 30):
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        to_remove = []
        for message_id, snapshot in self.state_snapshots.items():
            snapshot_time = datetime.fromisoformat(snapshot["timestamp"]).timestamp()
            if snapshot_time < cutoff_time:
                to_remove.append(message_id)
                
        for message_id in to_remove:
            del self.state_snapshots[message_id]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        total_sender_profiles = len(self.sender_profiles)
        total_domain_memories = len(self.domain_memories)
        total_message_lineages = len(self.message_lineages)
        total_state_snapshots = len(self.state_snapshots)
        
        total_messages_in_history = sum(len(profile.message_history) for profile in self.sender_profiles.values())
        total_insights = sum(len(domain.insights) for domain in self.domain_memories.values())
        
        successful_messages = sum(1 for lineage in self.message_lineages.values() if lineage.success)
        success_rate = successful_messages / total_message_lineages if total_message_lineages > 0 else 0
        
        return {
            "sender_profiles": total_sender_profiles,
            "domain_memories": total_domain_memories,
            "message_lineages": total_message_lineages,
            "state_snapshots": total_state_snapshots,
            "total_messages_in_history": total_messages_in_history,
            "total_insights": total_insights,
            "successful_messages": successful_messages,
            "success_rate": success_rate
        }
    
    def export_memory_data(self) -> Dict[str, Any]:
        return {
            "sender_profiles": {
                sender_id: {
                    "sender_id": profile.sender_id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "title": profile.title,
                    "linkedin_url": profile.linkedin_url,
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat(),
                    "message_history": profile.message_history
                }
                for sender_id, profile in self.sender_profiles.items()
            },
            "domain_memories": {
                domain_key: {
                    "company": domain.company,
                    "industry": domain.industry,
                    "insights": domain.insights,
                    "last_updated": domain.last_updated.isoformat()
                }
                for domain_key, domain in self.domain_memories.items()
            },
            "message_lineages": {
                message_id: {
                    "message_id": lineage.message_id,
                    "parent_message_id": lineage.parent_message_id,
                    "message_type": lineage.message_type,
                    "recipient_id": lineage.recipient_id,
                    "timestamp": lineage.timestamp.isoformat(),
                    "final_output": lineage.final_output,
                    "execution_trace": lineage.execution_trace,
                    "success": lineage.success
                }
                for message_id, lineage in self.message_lineages.items()
            },
            "statistics": self.get_memory_statistics()
        }
