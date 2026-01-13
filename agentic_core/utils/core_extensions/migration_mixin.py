import logging
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime

class MigrationError(Exception):
    """Raised when a schema migration fails or is invalid."""
    pass

class MigrationMixin:
    """
    Phase 2 Observability Infrastructure: Migration Support (Report 4.5).
    
    Provides version awareness and schema migration hooks for agents.
    Features:
    - Version tracking (_schema_version)
    - Automatic migration discovery
    - Backward compatibility warnings
    - Migration history tracking
    """

    # Default schema version for new agents
    _schema_version: str = "1.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mm_logger = logging.getLogger(self.__class__.__name__)
        self._migration_history: List[Dict[str, str]] = []

    def get_current_version(self) -> str:
        """Returns the current schema version of the agent."""
        return self._schema_version

    async def migrate_data(self, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """
        Orchestrates the migration of data from an older version to current.
        
        Args:
            data: The raw data dictionary to migrate.
            from_version: The version string the data currently follows.
            
        Returns:
            Dict: The migrated data matching the current _schema_version.
        """
        target_version = self._schema_version
        
        if from_version == target_version:
            return data

        self._mm_logger.info(f"Starting migration: {from_version} -> {target_version}")
        
        current_v = from_version
        # Logic to find and execute step-by-step migration methods
        # Expected naming: migrate_v1_0_to_next
        while current_v != target_version:
            # Simple version string normalization for method lookup (1.0 -> 1_0)
            v_norm = current_v.replace('.', '_')
            migration_method_name = f"migrate_v{v_norm}_to_next"
            
            migration_func = getattr(self, migration_method_name, None)
            
            if not migration_func:
                error_msg = f"No migration path found from {current_v}. Missing {migration_method_name}."
                self._mm_logger.error(error_msg)
                raise MigrationError(error_msg)

            try:
                data = await migration_func(data)
                old_v = current_v
                # Concrete agents must update the 'version' key in their logic or 
                # we assume the migration function handled the logic.
                # Here we assume the migration function returns data for the NEXT version.
                current_v = data.get("_new_version_id", target_version) 
                
                self._migration_history.append({
                    "from": old_v,
                    "to": current_v,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                self._mm_logger.error(f"Migration failed at step {current_v}: {e}")
                raise MigrationError(f"Step {current_v} failed: {e}")

        self._mm_logger.info(f"Migration successful. Final version: {current_v}")
        return data
