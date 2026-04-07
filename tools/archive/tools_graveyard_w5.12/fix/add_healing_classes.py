#!/usr/bin/env python3
"""Add System Learning classes to execute_ssot.py"""

with open('agentic_core/L0_routing/scripts/execute_ssot.py', encoding='utf-8') as f:
    content = f.read()

# Check if classes already exist
if 'class HealingOutcomeAggregator' in content:
    print("HealingOutcomeAggregator already exists")
else:
    # Add the classes at the end
    classes_to_add = '''


# =============================================================================
# System Learning Infrastructure (Healing Outcome Aggregation)
# =============================================================================

@dataclass
class HealingOutcomeEvent:
    """Event representing a healing outcome."""
    healer_id: str
    tier: str
    failure_type: str
    success: bool
    timestamp_utc: int


class HealingOutcomeAggregator:
    """Aggregates healing outcome events for meta-learning."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._events: list = []

    def ingest(self, event: HealingOutcomeEvent) -> None:
        """Add an event to the aggregator."""
        self._events.append(event)
        # Trim to window size
        if len(self._events) > self.window_size:
            self._events = self._events[-self.window_size:]

    def snapshot(self) -> dict:
        """Return a deterministic snapshot of aggregated outcomes."""
        if not self._events:
            return {
                'window_size': self.window_size,
                'event_count': 0,
                'success_rate': 0.0,
                'by_tier': {},
                'by_failure_type': {},
            }

        # Calculate statistics
        success_count = sum(1 for e in self._events if e.success)
        by_tier: dict[str, dict] = {}
        by_failure_type: dict[str, dict] = {}

        for event in self._events:
            # Tier aggregation
            if event.tier not in by_tier:
                by_tier[event.tier] = {'total': 0, 'success': 0}
            by_tier[event.tier]['total'] += 1
            if event.success:
                by_tier[event.tier]['success'] += 1

            # Failure type aggregation
            if event.failure_type not in by_failure_type:
                by_failure_type[event.failure_type] = {'total': 0, 'success': 0}
            by_failure_type[event.failure_type]['total'] += 1
            if event.success:
                by_failure_type[event.failure_type]['success'] += 1

        return {
            'window_size': self.window_size,
            'event_count': len(self._events),
            'success_rate': success_count / len(self._events),
            'by_tier': by_tier,
            'by_failure_type': by_failure_type,
        }


@dataclass
class HealingOutcomeRecord:
    """Record format for healing outcome storage."""
    schema_version: str
    created_utc: int
    window_size: int
    snapshot: dict
    proposal: dict


class InMemoryHealingOutcomeIntakeStore:
    """In-memory store for healing outcomes."""

    def __init__(self):
        self._records: list = []

    def store(self, record: HealingOutcomeRecord) -> None:
        """Store a healing outcome record."""
        self._records.append(record)

    def get_all(self) -> list:
        """Get all stored records."""
        return self._records.copy()


class HealingOutcomeIntakeAdapter:
    """Adapter for building healing outcome records."""

    def __init__(self, store: InMemoryHealingOutcomeIntakeStore):
        self._store = store

    def build_record(
        self,
        aggregator: HealingOutcomeAggregator,
        created_utc: int,
        source: str,
    ) -> HealingOutcomeRecord:
        """Build a healing outcome record from an aggregator."""
        snapshot = aggregator.snapshot()

        # Generate proposal based on outcomes
        proposal = self._generate_proposal(snapshot, source)

        record = HealingOutcomeRecord(
            schema_version='1.0',
            created_utc=created_utc,
            window_size=snapshot['window_size'],
            snapshot=snapshot,
            proposal=proposal,
        )

        # Store the record
        self._store.store(record)

        return record

    def _generate_proposal(self, snapshot: dict, source: str) -> dict:
        """Generate a meta-learning proposal from snapshot data."""
        if snapshot['event_count'] == 0:
            return {
                'type': 'no_data',
                'recommendation': 'Collect more healing outcomes',
                'source': source,
            }

        # Find best performing tier
        best_tier = None
        best_rate = 0.0
        for tier, stats in snapshot['by_tier'].items():
            rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            if rate > best_rate:
                best_rate = rate
                best_tier = tier

        # Find most common failure type
        most_common_failure = None
        max_count = 0
        for failure_type, stats in snapshot['by_failure_type'].items():
            if stats['total'] > max_count:
                max_count = stats['total']
                most_common_failure = failure_type

        return {
            'type': 'healing_strategy',
            'success_rate': snapshot['success_rate'],
            'best_tier': best_tier,
            'best_tier_rate': best_rate,
            'most_common_failure': most_common_failure,
            'source': source,
        }
'''

    with open('agentic_core/L0_routing/scripts/execute_ssot.py', 'a', encoding='utf-8') as f:
        f.write(classes_to_add)

    print("Added System Learning infrastructure classes to execute_ssot.py")
