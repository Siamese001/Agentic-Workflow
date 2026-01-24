"""
Base Resume Agent - Foundation for all RG Sovereign V2.5 Engines
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

# Import mixins - fall back to stubs if not available
try:
    from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
    from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
    MIXINS_AVAILABLE = True
except ImportError:
    class MCPHardenedMixin:
        """Stub MCPHardenedMixin for standalone usage."""
        def __init__(self, *args, **kwargs):
            pass
    
    class HealerMixin:
        """Stub HealerMixin for standalone usage."""
        def __init__(self, *args, **kwargs):
            pass
        
        def heal_repository(self, dry_run: bool = True, execute: bool = False, 
                           depth: int = 0, max_depth: int = 3, 
                           _call_path: Optional[set] = None) -> Dict[str, int]:
            return {'violations': 0, 'fixed': 0, 'errors': 0, 'skipped': 0}
    
    MIXINS_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):
    """
    Abstract base class for all Resume Generation engines.
    
    Provides:
    - MCP hardening capabilities
    - Self-healing capabilities
    - Standard logging interface
    - Pydantic model I/O enforcement
    - Knowledge base integration
    """
    
    def __init__(self, config: Optional[BaseModel] = None, **kwargs):
        """Initialize the engine with configuration."""
        super().__init__(**kwargs)
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        
        # Import knowledge base
        try:
            from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT
            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:
            self.knowledge = None
            self.logger.warning("Knowledge base not available")
    
    @abstractmethod
    def execute(self, input_data: BaseModel) -> BaseModel:
        """
        Main execution method - must be implemented by subclasses.
        
        Args:
            input_data: Pydantic model containing input
            
        Returns:
            Pydantic model containing output
        """
        pass
    
    def validate_input(self, input_data: BaseModel) -> bool:
        """Validate input data before execution."""
        if not isinstance(input_data, BaseModel):
            raise TypeError(f"Input must be a Pydantic BaseModel, got {type(input_data)}")
        return True
    
    def get_prompt(self, prompt_id: str) -> str:
        """Get prompt from knowledge base."""
        if self.knowledge:
            from apps_rg.domain.knowledge_base import get_prompt
            return get_prompt(prompt_id)
        return ""
    
    def get_node_config(self, node_id: str) -> Any:
        """Get K-node configuration from knowledge base."""
        if self.knowledge:
            from apps_rg.domain.knowledge_base import get_node_config
            return get_node_config(node_id)
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Return engine status for observability."""
        return {
            'engine': self.__class__.__name__,
            'initialized': self._initialized,
            'mixins_available': MIXINS_AVAILABLE,
            'knowledge_available': self.knowledge is not None
        }
