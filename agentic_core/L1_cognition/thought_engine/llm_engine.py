from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
"""
LLM Engine Abstraction - Provider Diversification Layer

RESPONSIBILITIES:
- Abstract interface for multiple LLM providers
- Enable consistency checks across providers
- Support fallback and redundancy
- Prevent single-Provider dependency

Placed in L1_cognition per SSOT semantic registry:
  "Cognitive layer for LLM interaction abstraction"
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any

Logger = logging.getLogger(__name__)


class LLMEngine(ABC):
    """
    Abstract base class for LLM providers.
    
    Enables:
    - Provider diversification
    - Consistency checks across models
    - Graceful fallback on Provider failure
    """
    
    @abstractmethod
    async def mutate(
        self, 
        prompt: str, 
        code: str, 
        file_path: str,
        context: str = "",
        fission_active: bool = False
    ) -> str:
        """
        Generate code mutation using LLM.
        
        Args:
            prompt: System/Task prompt
            code: Original code to mutate
            file_path: Path to file being mutated
            context: Additional context (e.g., from vector memory)
            fission_active: Whether this is a fission operation
            
        Returns:
            Mutated code string
        """
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this LLM Provider."""
        pass


class GeminiEngine(LLMEngine):
    """
    [HARDENING 11] Gemini-based LLM engine implementation.
    
    Wraps existing SubAtomicEngine logic for Gemini 2.5 Flash.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize Gemini engine.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self._engine = None
        
        # Lazy load SubAtomicEngine to avoid circular imports
        try:
            # GRAVITY FIXED (Upward Leak): from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngineImpl
            _mod = importlib.import_module('agentic_core.L5_safety.guardrails.subatomic_engine')
            SubAtomicEngineImpl = getattr(_mod, 'SubAtomicEngineImpl')
            self._engine = SubAtomicEngineImpl(project_root)
            Logger.info("[GeminiEngine] Initialized successfully")
        except Exception as e:
            Logger.error(f"[GeminiEngine] Initialization failed: {e}")
    
    async def mutate(
        self, 
        prompt: str, 
        code: str, 
        file_path: str,
        context: str = "",
        fission_active: bool = False
    ) -> str:
        """
        Generate code mutation using Gemini.
        
        Args:
            prompt: System/Task prompt
            code: Original code to mutate
            file_path: Path to file being mutated
            context: Additional context
            fission_active: Whether this is a fission operation
            
        Returns:
            Mutated code string
        """
        if not self._engine:
            raise RuntimeError("GeminiEngine not initialized")
        
        # Use SubAtomicEngine's resilient_mutation
        return await self._engine.resilient_mutation(
            code=code,
            Task=prompt,
            file_path=file_path,
            system_prompt=None,
            fission_active=fission_active
        )
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding using Gemini.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self._engine:
            raise RuntimeError("GeminiEngine not initialized")
        
        # Use SubAtomicEngine's embedding capability via Pinecone agent
        if hasattr(self._engine, 'pinecone') and self._engine.pinecone:
            return await self._engine.pinecone.get_embedding(text)
        
        # Fallback: return zero vector
        return [0.0] * 768
    
    def get_provider_name(self) -> str:
        """Return Provider name."""
        return "gemini-2.5-flash"


class MultiProviderEngine:
    """
    [HARDENING 11] Multi-Provider LLM engine with consistency checks.
    
    Supports:
    - Primary/secondary Provider configuration
    - Consistency verification across providers
    - Automatic fallback on failure
    """
    
    def __init__(
        self, 
        project_root: Path,
        primary: str = "gemini",
        secondary: Optional[str] = None,
        consistency_threshold: float = 0.95
    ):
        """
        Initialize multi-Provider engine.
        
        Args:
            project_root: Project root directory
            primary: Primary Provider name
            secondary: Optional secondary Provider for consistency checks
            consistency_threshold: Minimum similarity for consistency check (0.0-1.0)
        """
        self.project_root = project_root
        self.consistency_threshold = consistency_threshold
        self.consistency_mode = bool(secondary)
        
        # Initialize primary engine
        self.primary = self._load_engine(primary)
        Logger.info(f"[MultiProviderEngine] Primary: {primary}")
        
        # Initialize secondary engine if specified
        self.secondary = None
        if secondary:
            try:
                self.secondary = self._load_engine(secondary)
                Logger.info(f"[MultiProviderEngine] Secondary: {secondary} (consistency mode enabled)")
            except Exception as e:
                Logger.warning(f"[MultiProviderEngine] Secondary engine failed to load: {e}")
                self.consistency_mode = False
    
    def _load_engine(self, Provider: str) -> LLMEngine:
        """
        Load LLM engine by Provider name.
        
        Args:
            Provider: Provider name (e.g., 'gemini', 'grok')
            
        Returns:
            LLMEngine instance
        """
        if Provider.lower() == "gemini":
            return GeminiEngine(self.project_root)
        else:
            raise ValueError(f"Unsupported LLM Provider: {Provider}")
    
    async def mutate(
        self, 
        prompt: str, 
        code: str, 
        file_path: str,
        context: str = "",
        fission_active: bool = False
    ) -> str:
        """
        [HARDENING 11] Generate code mutation with optional consistency check.
        
        Args:
            prompt: System/Task prompt
            code: Original code to mutate
            file_path: Path to file being mutated
            context: Additional context
            fission_active: Whether this is a fission operation
            
        Returns:
            Mutated code string
            
        Raises:
            ValueError: If consistency check fails
        """
        # Get primary output
        primary_output = await self.primary.mutate(
            prompt=prompt,
            code=code,
            file_path=file_path,
            context=context,
            fission_active=fission_active
        )
        
        # If consistency mode enabled, verify with secondary Provider
        if self.consistency_mode and self.secondary:
            try:
                secondary_output = await self.secondary.mutate(
                    prompt=prompt,
                    code=code,
                    file_path=file_path,
                    context=context,
                    fission_active=fission_active
                )
                
                # Check consistency
                if not self._outputs_equivalent(primary_output, secondary_output):
                    Logger.error(
                        f"[CONSISTENCY] Outputs diverge for {Path(file_path).name}\n"
                        f"  Primary: {self.primary.get_provider_name()}\n"
                        f"  Secondary: {self.secondary.get_provider_name()}"
                    )
                    raise ValueError(
                        "LLM consistency check failed - outputs diverge between providers"
                    )
                
                Logger.info(f"[CONSISTENCY] Verified for {Path(file_path).name}")
                
            except Exception as e:
                if "consistency check failed" in str(e).lower():
                    raise
                Logger.warning(f"[CONSISTENCY] Secondary Provider failed: {e}")
        
        return primary_output
    
    def _outputs_equivalent(self, output_a: str, output_b: str) -> bool:
        """
        [HARDENING 11] Check if two LLM outputs are equivalent.
        
        Uses line-by-line comparison with whitespace normalization.
        
        Args:
            output_a: First output
            output_b: Second output
            
        Returns:
            True if outputs are sufficiently similar
        """
        # Normalize: strip whitespace, remove empty lines
        lines_a = [line.strip() for line in output_a.splitlines() if line.strip()]
        lines_b = [line.strip() for line in output_b.splitlines() if line.strip()]
        
        # Must have same number of non-empty lines
        if len(lines_a) != len(lines_b):
            Logger.warning(
                f"[CONSISTENCY] Line count mismatch: {len(lines_a)} vs {len(lines_b)}"
            )
            return False
        
        # Count matching lines
        matches = sum(1 for la, lb in zip(lines_a, lines_b) if la == lb)
        similarity = matches / len(lines_a) if lines_a else 1.0
        
        Logger.debug(f"[CONSISTENCY] Similarity: {similarity:.2%}")
        
        return similarity >= self.consistency_threshold
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding using primary Provider.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return await self.primary.embed(text)
    
    def get_provider_name(self) -> str:
        """Return primary Provider name."""
        return self.primary.get_provider_name()
