#!/usr/bin/env python3
"""
Temporal Invalidation Tool
Section 5: Tool Contracts - TEMPORAL tool family
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TemporalInvalidationTool:
    """Apply temporal invalidation decisions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.default_validity = self.config.get("default_validity", "indefinite")
        self.conflict_resolution = self.config.get("conflict_resolution", "highest_confidence")
    
    def apply_invalidation(self, records: List[Dict[str, Any]], invalidation_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply invalidation rules to temporal records"""
        try:
            processed_records = []
            
            for record in records:
                processed_record = self._process_record_invalidation(record, invalidation_rules)
                processed_records.append(processed_record)
            
            logger.info(f"Applied invalidation to {len(processed_records)} records")
            return processed_records
            
        except Exception as e:
            logger.error(f"Invalidation application failed: {e}")
            return records
    
    def _process_record_invalidation(self, record: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process invalidation for a single record"""
        processed_record = record.copy()
        
        # Apply each invalidation rule
        for rule in rules:
            if self._rule_matches(record, rule):
                processed_record = self._apply_rule(processed_record, rule)
        
        return processed_record
    
    def _rule_matches(self, record: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if invalidation rule matches record"""
        rule_type = rule.get("type")
        
        if rule_type == "date_based":
            return self._check_date_rule(record, rule)
        elif rule_type == "condition_based":
            return self._check_condition_rule(record, rule)
        elif rule_type == "confidence_based":
            return self._check_confidence_rule(record, rule)
        
        return False
    
    def _check_date_rule(self, record: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check date-based invalidation rule"""
        record_date = record.get("valid_at")
        threshold_date = rule.get("threshold_date")
        
        if record_date and threshold_date:
            return record_date < threshold_date
        
        return False
    
    def _check_condition_rule(self, record: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check condition-based invalidation rule"""
        conditions = rule.get("conditions", {})
        
        for field, expected_value in conditions.items():
            if record.get(field) != expected_value:
                return False
        
        return True
    
    def _check_confidence_rule(self, record: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check confidence-based invalidation rule"""
        record_confidence = record.get("confidence", 1.0)
        min_confidence = rule.get("min_confidence", 0.5)
        
        return record_confidence < min_confidence
    
    def _apply_rule(self, record: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Apply invalidation rule to record"""
        action = rule.get("action", "invalidate")
        
        if action == "invalidate":
            record["invalid_at"] = rule.get("invalidation_date", datetime.now().isoformat())
            record["invalidation_reason"] = rule.get("reason", "Rule-based invalidation")
        elif action == "update_confidence":
            record["confidence"] = rule.get("new_confidence", 0.5)
        elif action == "flag":
            record["flagged"] = True
            record["flag_reason"] = rule.get("reason", "Flagged by rule")
        
        return record
    
    def resolve_conflicts(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts in temporal records"""
        try:
            # Group records by entity or identifier
            grouped_records = {}
            for record in records:
                key = record.get("entity_id", record.get("id", str(hash(str(record)))))
                if key not in grouped_records:
                    grouped_records[key] = []
                grouped_records[key].append(record)
            
            # Resolve conflicts within each group
            resolved_records = []
            for group_key, group_records in grouped_records.items():
                resolved_group = self._resolve_group_conflicts(group_records)
                resolved_records.extend(resolved_group)
            
            logger.info(f"Resolved conflicts in {len(resolved_records)} records")
            return resolved_records
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return records
    
    def _resolve_group_conflicts(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts within a group of records"""
        if self.conflict_resolution == "highest_confidence":
            # Sort by confidence and keep highest
            records.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            return records[:1]  # Keep only the highest confidence record
        elif self.conflict_resolution == "most_recent":
            # Sort by valid_at date and keep most recent
            records.sort(key=lambda x: x.get("valid_at", ""), reverse=True)
            return records[:1]
        else:
            # Keep all records with conflict markers
            for record in records:
                record["has_conflict"] = True
            return records
    
    def get_valid_records(self, records: List[Dict[str, Any]], as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get records that are valid as of a specific date"""
        try:
            if not as_of_date:
                as_of_date = datetime.now().isoformat()
            
            valid_records = []
            for record in records:
                if self._is_record_valid(record, as_of_date):
                    valid_records.append(record)
            
            logger.info(f"Found {len(valid_records)} valid records as of {as_of_date}")
            return valid_records
            
        except Exception as e:
            logger.error(f"Valid records retrieval failed: {e}")
            return []
    
    def _is_record_valid(self, record: Dict[str, Any], as_of_date: str) -> bool:
        """Check if record is valid as of given date"""
        valid_at = record.get("valid_at", "")
        invalid_at = record.get("invalid_at")
        
        # Check if record is valid as of the given date
        if valid_at and valid_at > as_of_date:
            return False
        
        if invalid_at and invalid_at <= as_of_date:
            return False
        
        return True

def create_temporal_invalidation_tool(config: Optional[Dict[str, Any]] = None) -> TemporalInvalidationTool:
    """Factory function to create temporal invalidation tool instance"""
    return TemporalInvalidationTool(config)

# Re-export components
__all__ = [
    'TemporalInvalidationTool', 'create_temporal_invalidation_tool'
]
