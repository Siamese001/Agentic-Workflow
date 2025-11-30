"""Temporal research pathways for outreach campaigns."""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TemporalSignal:
    """Temporal signal for research prioritization."""
    signal_type: str
    strength: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalEvidence:
    """Temporal evidence object."""
    evidence_id: str
    content: str
    temporal_signals: List[TemporalSignal] = field(default_factory=list)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

class TemporalKG:
    """Temporal Knowledge Graph for research pathways."""

    def __init__(self, adapter=None):
        """Initialize TemporalKG with optional adapter."""
        self.adapter = adapter
        self.temporal_data = {}
        self.signal_weights = {
            "recent_activity": 0.8,
            "industry_trends": 0.6,
            "company_growth": 0.7,
            "career_progression": 0.9
        }

    def add_temporal_signal(self, entity_id: str, signal: TemporalSignal) -> None:
        """Add temporal signal for an entity."""
        if entity_id not in self.temporal_data:
            self.temporal_data[entity_id] = []
        self.temporal_data[entity_id].append(signal)

    def get_temporal_signals(self, entity_id: str, signal_type: str = None) -> List[TemporalSignal]:
        """Get temporal signals for an entity."""
        signals = self.temporal_data.get(entity_id, [])
        if signal_type:
            signals = [s for s in signals if s.signal_type == signal_type]
        return signals

    def compute_temporal_weight(self, entity_id: str, archetype: str = None) -> float:
        """Compute temporal weight for entity based on signals."""
        signals = self.get_temporal_signals(entity_id)
        if not signals:
            return 0.5  # Default weight

        # Weight recent signals more heavily
        now = datetime.now()
        total_weight = 0.0
        signal_count = 0

        for signal in signals:
            # Decay based on age (older signals have less impact)
            age_days = (now - signal.timestamp).days
            decay_factor = max(0.1, 1.0 - (age_days / 365.0))  # Yearly decay

            signal_weight = self.signal_weights.get(signal.signal_type, 0.5)
            total_weight += signal.strength * signal_weight * decay_factor
            signal_count += 1

        if signal_count == 0:
            return 0.5

        # Apply archetype-specific adjustments
        base_weight = total_weight / signal_count
        if archetype == "C_LEVEL":
            base_weight *= 1.2  # C-level values temporal signals more
        elif archetype == "SENIOR_TA":
            base_weight *= 1.1

        return min(1.0, base_weight)

    def get_temporal_metadata(self, entity_id: str) -> Dict[str, Any]:
        """Get temporal metadata for entity."""
        signals = self.get_temporal_signals(entity_id)
        if not signals:
            return {"has_temporal_data": False}

        recent_signals = [s for s in signals if (datetime.now() - s.timestamp).days <= 30]
        signal_types = list(set(s.signal_type for s in signals))

        return {
            "has_temporal_data": True,
            "total_signals": len(signals),
            "recent_signals": len(recent_signals),
            "signal_types": signal_types,
            "latest_signal": max(signals, key=lambda s: s.timestamp).timestamp.isoformat() if signals else None
        }

class TemporalResearchPathway:
    """Temporal research pathway executor."""

    def __init__(self, temporal_kg: TemporalKG):
        """Initialize with temporal knowledge graph."""
        self.temporal_kg = temporal_kg
        self.pathway_config = {
            "max_temporal_lookback_days": 365,
            "min_signal_strength": 0.3,
            "temporal_weight_threshold": 0.5
        }

    def prioritize_research_targets(self, targets: List[Dict[str, Any]], archetype: str = None) -> List[Dict[str, Any]]:
        """Prioritize research targets based on temporal signals."""
        prioritized = []

        for target in targets:
            entity_id = target.get("entity_id", target.get("name", ""))
            temporal_weight = self.temporal_kg.compute_temporal_weight(entity_id, archetype)
            temporal_metadata = self.temporal_kg.get_temporal_metadata(entity_id)

            # Combine with base priority
            base_priority = target.get("priority", 0.5)
            combined_priority = (base_priority * 0.6) + (temporal_weight * 0.4)

            enriched_target = {
                **target,
                "temporal_weight": temporal_weight,
                "temporal_metadata": temporal_metadata,
                "combined_priority": combined_priority
            }
            prioritized.append(enriched_target)

        # Sort by combined priority
        prioritized.sort(key=lambda x: x["combined_priority"], reverse=True)
        return prioritized

    def add_company_temporal_signals(self, company_name: str, signals: List[TemporalSignal]) -> None:
        """Add temporal signals for a company."""
        entity_id = f"company:{company_name}"
        for signal in signals:
            self.temporal_kg.add_temporal_signal(entity_id, signal)

    def add_contact_temporal_signals(self, contact_name: str, company: str, signals: List[TemporalSignal]) -> None:
        """Add temporal signals for a contact."""
        entity_id = f"contact:{contact_name}:{company}"
        for signal in signals:
            self.temporal_kg.add_temporal_signal(entity_id, signal)
