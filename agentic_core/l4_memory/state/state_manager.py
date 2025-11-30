"""
State Manager Implementation for Memory Layer
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ..short_term.memory import ShortTermMemory
from ..long_term.memory import LongTermMemory


class StateType(Enum):
    """Types of state that can be managed"""
    WORKFLOW = "workflow"
    SESSION = "session"
    TASK = "task"
    USER = "user"
    SYSTEM = "system"


@dataclass
class StateTransition:
    """A transition between states"""
    from_state: str
    to_state: str
    timestamp: datetime
    context: Dict[str, Any]
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class StateManager:
    """State manager for coordinating between short-term and long-term memory"""
    
    def __init__(self, short_term_memory: ShortTermMemory = None, long_term_memory: LongTermMemory = None):
        self.short_term = short_term_memory or ShortTermMemory()
        self.long_term = long_term_memory or LongTermMemory()
        self.current_states: Dict[str, str] = {}
        self.state_history: List[StateTransition] = []
        self.state_validators: Dict[str, Callable] = {}
        self.state_handlers: Dict[str, Callable] = {}
        self.created_at = datetime.now()
        self.stats = {
            "state_transitions": 0,
            "validations_performed": 0,
            "handlers_executed": 0
        }
    
    def set_state(self, state_type: str, state_value: str, context: Dict[str, Any] = None) -> bool:
        """Set a state value"""
        try:
            # Validate state transition if validator exists
            if state_type in self.state_validators:
                validator = self.state_validators[state_type]
                if not validator(state_value, context or {}):
                    return False
            
            # Record transition
            old_state = self.current_states.get(state_type)
            if old_state != state_value:
                transition = StateTransition(
                    from_state=old_state or "None",
                    to_state=state_value,
                    timestamp=datetime.now(),
                    context=context or {}
                )
                self.state_history.append(transition)
                self.stats["state_transitions"] += 1
            
            # Set the state
            self.current_states[state_type] = state_value
            
            # Store in short-term memory with metadata
            state_key = f"state_{state_type}"
            state_data = {
                "value": state_value,
                "type": state_type,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            self.short_term.set(state_key, state_data)
            
            # Execute state handler if exists
            if state_type in self.state_handlers:
                handler = self.state_handlers[state_type]
                handler(state_value, context or {})
                self.stats["handlers_executed"] += 1
            
            return True
            
        except Exception:
            return False
    
    def get_state(self, state_type: str, default: str = None) -> str:
        """Get a state value"""
        # Try current states first
        if state_type in self.current_states:
            return self.current_states[state_type]
        
        # Try short-term memory
        state_key = f"state_{state_type}"
        state_data = self.short_term.get(state_key)
        if state_data:
            self.current_states[state_type] = state_data["value"]
            return state_data["value"]
        
        # Try long-term memory
        state_data = self.long_term.get(state_key)
        if state_data:
            self.current_states[state_type] = state_data["value"]
            # Move back to short-term for faster access
            self.short_term.set(state_key, state_data)
            return state_data["value"]
        
        return default
    
    def update_state(self, state_type: str, state_value: str, context: Dict[str, Any] = None) -> bool:
        """Update an existing state"""
        if state_type in self.current_states:
            return self.set_state(state_type, state_value, context)
        return False
    
    def delete_state(self, state_type: str) -> bool:
        """Delete a state"""
        try:
            if state_type in self.current_states:
                del self.current_states[state_type]
            
            state_key = f"state_{state_type}"
            self.short_term.delete(state_key)
            self.long_term.delete(state_key)
            
            return True
            
        except Exception:
            return False
    
    def exists_state(self, state_type: str) -> bool:
        """Check if a state exists"""
        return self.get_state(state_type) is not None
    
    def add_validator(self, state_type: str, validator: Callable):
        """Add a validator for a state type"""
        self.state_validators[state_type] = validator
    
    def add_handler(self, state_type: str, handler: Callable):
        """Add a handler for a state type"""
        self.state_handlers[state_type] = handler
    
    def transition_state(self, state_type: str, new_state: str, context: Dict[str, Any] = None) -> bool:
        """Transition to a new state with validation"""
        current_state = self.get_state(state_type)
        
        # Validate transition
        if state_type in self.state_validators:
            validator = self.state_validators[state_type]
            transition_context = {
                "from_state": current_state,
                "to_state": new_state,
                **(context or {})
            }
            if not validator(new_state, transition_context):
                return False
        
        return self.set_state(state_type, new_state, context)
    
    def get_state_history(self, state_type: str = None) -> List[Dict[str, Any]]:
        """Get state transition history"""
        if state_type:
            # Filter by state type
            filtered_history = []
            for transition in self.state_history:
                # Look for corresponding state in context
                for st, sv in self.current_states.items():
                    if transition.to_state == sv:
                        filtered_history.append({
                            "from_state": transition.from_state,
                            "to_state": transition.to_state,
                            "timestamp": transition.timestamp.isoformat(),
                            "context": transition.context
                        })
                        break
            return filtered_history
        
        return [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "timestamp": t.timestamp.isoformat(),
                "context": t.context
            }
            for t in self.state_history
        ]
    
    def persist_state(self, state_type: str) -> bool:
        """Persist a state to long-term memory"""
        try:
            state_key = f"state_{state_type}"
            state_data = self.short_term.get(state_key)
            if state_data:
                self.long_term.set(state_key, state_data, category="persistent_state")
                return True
            return False
            
        except Exception:
            return False
    
    def persist_all_states(self) -> int:
        """Persist all current states to long-term memory"""
        persisted_count = 0
        for state_type in self.current_states.keys():
            if self.persist_state(state_type):
                persisted_count += 1
        return persisted_count
    
    def restore_state(self, state_type: str) -> bool:
        """Restore a state from long-term memory"""
        try:
            state_key = f"state_{state_type}"
            state_data = self.long_term.get(state_key)
            if state_data:
                self.current_states[state_type] = state_data["value"]
                self.short_term.set(state_key, state_data)
                return True
            return False
            
        except Exception:
            return False
    
    def restore_all_states(self) -> int:
        """Restore all states from long-term memory"""
        restored_count = 0
        persistent_states = self.long_term.get_by_category("persistent_state")
        
        for state_key, state_data in persistent_states.items():
            if state_key.startswith("state_"):
                state_type = state_key[6:]  # Remove "state_" prefix
                self.current_states[state_type] = state_data["value"]
                self.short_term.set(state_key, state_data)
                restored_count += 1
        
        return restored_count
    
    def clear_states(self, state_type: str = None):
        """Clear states"""
        if state_type:
            self.delete_state(state_type)
        else:
            self.current_states.clear()
            self.short_term.clear()
    
    def get_all_states(self) -> Dict[str, str]:
        """Get all current states"""
        return self.current_states.copy()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of all states"""
        return {
            "current_states": self.get_all_states(),
            "total_transitions": len(self.state_history),
            "short_term_size": len(self.short_term),
            "long_term_size": len(self.long_term),
            "stats": self.stats.copy(),
            "created_at": self.created_at.isoformat()
        }
    
    def validate_all_states(self) -> Dict[str, bool]:
        """Validate all current states"""
        results = {}
        
        for state_type, state_value in self.current_states.items():
            if state_type in self.state_validators:
                validator = self.state_validators[state_type]
                state_data = self.short_term.get(f"state_{state_type}")
                context = state_data.get("context", {}) if state_data else {}
                results[state_type] = validator(state_value, context)
                self.stats["validations_performed"] += 1
            else:
                results[state_type] = True  # No validator means always valid
        
        return results
    
    def __str__(self):
        return f"StateManager(states={len(self.current_states)}, transitions={len(self.state_history)})"
    
    def __repr__(self):
        return self.__str__()
