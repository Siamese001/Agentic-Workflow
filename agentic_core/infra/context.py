"""
Universal Context - The Nervous System
Single source of truth for state, memory, and LLM access across all agents.

Consolidates:
- omni_context.py (semantic context buffer)
- validation_context.py (validation state tracking)
- context_passport.py (thermal configuration)
- llm_client_flash.py (Gemini client)
- hardened_gemini_executor.py (resilient execution)

This is the "Brain" and "Nervous System" of the entire agentic architecture.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ThermalProfile(str, Enum):
    """Thermal configurations for different reasoning modes."""
    CREATIVITY_MAX = "creativity_max"
    CREATIVITY_HIGH = "creativity_high"
    BALANCED = "balanced"
    STRUCTURED = "structured"
    PRECISION = "precision"


@dataclass
class MemoryConfig:
    """Configuration for memory management."""
    memory_dir: Path = field(default_factory=lambda: Path(".canon_memory"))
    canon_memory_file: str = "canon_memory.json"
    context_file: str = "current_context.json"
    max_history_size: int = 100
    enable_pinecone: bool = False
    pinecone_index: str = "omni-context"


@dataclass
class GeminiConfig:
    """Configuration for Gemini client."""
    model: str = "gemini-2.5-flash"
    temperature: float = 0.2
    thinking_budget: int = 24576
    max_retries: int = 5
    base_delay: float = 2.0
    backoff_factor: float = 2.0
    timeout: int = 300


class UniversalContext:
    """
    Universal Context - The Nervous System
    
    Single source of truth for:
    - Agent state and signals
    - Memory management (canon_memory.json)
    - LLM client (Gemini 2.5 Flash)
    - Thermal configuration
    - AtomicBlackboard integration
    - File tracking and hashing
    
    This replaces all fragmented context implementations.
    """
    
    _instance: Optional['UniversalContext'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern - only one Universal Context exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        memory_config: Optional[MemoryConfig] = None,
        gemini_config: Optional[GeminiConfig] = None
    ):
        """
        Initialize Universal Context (singleton).
        
        Args:
            memory_config: Memory configuration
            gemini_config: Gemini configuration
        """
        if self._initialized:
            return
        
        self.memory_config = memory_config or MemoryConfig()
        self.gemini_config = gemini_config or GeminiConfig()
        
        self._client: Optional[Any] = None
        self._pinecone_client: Optional[Any] = None
        self._blackboard: Optional[Any] = None
        
        self.signals: Set[str] = set()
        self.modified_files: Set[Path] = set()
        self.file_hashes: Dict[str, str] = {}
        
        self.cycle_id: int = 0
        self.start_time: datetime = datetime.utcnow()
        self.status: str = "INITIALIZED"
        
        self.context_buffer: str = ""
        self.file_index: Dict[str, Any] = {}
        self.file_contents: Dict[str, str] = {}
        
        self.healing_attempts: Dict[str, int] = {}
        self.healing_budget_used: int = 0
        self.max_healing_per_file: int = 8
        self.global_healing_budget: int = 50
        
        self.chat_sessions: Dict[str, Any] = {}
        self.conversation_history: Dict[str, List[Any]] = {}
        
        self.thermal_profile: ThermalProfile = ThermalProfile.PRECISION
        
        self._ensure_memory_dir()
        self._load_memory()
        
        self._initialized = True
        logger.info("✅ Universal Context initialized (singleton)")
    
    @property
    def client(self):
        """
        Lazy-loaded Gemini client (singleton).
        
        Returns:
            Gemini client instance
        """
        if self._client is None:
            if not GENAI_AVAILABLE:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            
            self._client = genai.Client(api_key=api_key)
            logger.info(f"✅ Gemini client initialized: {self.gemini_config.model}")
        
        return self._client
    
    @property
    def blackboard(self):
        """
        Lazy-loaded AtomicBlackboard.
        
        Returns:
            AtomicBlackboard instance
        """
        if self._blackboard is None:
            try:
                from agentic_core.L4_state.atomic_blackboard import AtomicBlackboard
                self._blackboard = AtomicBlackboard()
                logger.info("✅ AtomicBlackboard integrated")
            except ImportError:
                logger.warning("⚠️  AtomicBlackboard not available")
        
        return self._blackboard
    
    def _ensure_memory_dir(self):
        """Ensure memory directory exists."""
        self.memory_config.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_memory(self):
        """Load memory from canon_memory.json."""
        memory_file = self.memory_config.memory_dir / self.memory_config.canon_memory_file
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                
                self.cycle_id = memory_data.get("last_cycle_id", 0) + 1
                self.file_hashes = memory_data.get("file_hashes", {})
                
                logger.info(f"📖 Loaded memory from {memory_file}")
            except Exception as e:
                logger.warning(f"Failed to load memory: {e}")
    
    def save_memory(self):
        """Save memory to canon_memory.json."""
        memory_file = self.memory_config.memory_dir / self.memory_config.canon_memory_file
        
        memory_data = {
            "last_cycle_id": self.cycle_id,
            "last_updated": datetime.utcnow().isoformat(),
            "file_hashes": self.file_hashes,
            "signals": list(self.signals),
            "modified_files": [str(p) for p in self.modified_files],
            "healing_budget_used": self.healing_budget_used,
            "status": self.status
        }
        
        try:
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            logger.debug(f"💾 Saved memory to {memory_file}")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    async def generate_with_thinking(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        thinking_budget: Optional[int] = None,
        tools: Optional[List] = None,
        file_path: Optional[str] = None
    ) -> str:
        """
        Generate content with Gemini 2.5 Flash thinking mode.
        
        Args:
            prompt: Prompt for generation
            temperature: Temperature override
            thinking_budget: Thinking budget override
            tools: Optional tools for function calling
            file_path: Optional file path for chat session tracking
            
        Returns:
            Generated text
        """
        config = types.GenerateContentConfig(
            temperature=temperature or self.gemini_config.temperature,
            thinking_config=types.ThinkingConfig(
                thinking_budget=thinking_budget or self.gemini_config.thinking_budget
            ),
            tools=tools or []
        )
        
        chat_key = f"chat_{file_path}" if file_path else "chat_default"
        
        if chat_key not in self.chat_sessions:
            self.chat_sessions[chat_key] = self.client.chats.create(
                model=self.gemini_config.model,
                config=config
            )
            logger.debug(f"Created chat session: {chat_key}")
        
        chat = self.chat_sessions[chat_key]
        
        try:
            response = await self._execute_with_retry(
                lambda: chat.send_message(prompt)
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return ""
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def _execute_with_retry(self, func):
        """Execute function with exponential backoff retry."""
        for attempt in range(self.gemini_config.max_retries):
            try:
                import asyncio
                return await asyncio.to_thread(func)
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < self.gemini_config.max_retries - 1:
                        wait = self.gemini_config.base_delay * (self.gemini_config.backoff_factor ** attempt)
                        logger.warning(f"Rate limit hit, waiting {wait}s...")
                        import asyncio
                        await asyncio.sleep(wait)
                    else:
                        raise
                else:
                    raise
    
    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.signals.add(signal)
        logger.debug(f"Signal added: {signal}")
    
    def clear_signals(self):
        """Clear all signals."""
        self.signals.clear()
    
    def add_modified_file(self, file_path: Path):
        """Track a modified file."""
        self.modified_files.add(file_path)
    
    def update_file_hash(self, file_path: str, file_hash: str):
        """Update file hash for change detection."""
        self.file_hashes[file_path] = file_hash
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Get stored file hash."""
        return self.file_hashes.get(file_path)
    
    def can_attempt_healing(self, file_path: str) -> bool:
        """Check if healing can be attempted on this file."""
        if self.healing_budget_used >= self.global_healing_budget:
            return False
        
        if self.healing_attempts.get(file_path, 0) >= self.max_healing_per_file:
            return False
        
        return True
    
    def record_healing_attempt(self, file_path: str, success: bool):
        """Record a healing attempt."""
        if file_path not in self.healing_attempts:
            self.healing_attempts[file_path] = 0
        
        self.healing_attempts[file_path] += 1
        self.healing_budget_used += 1
        
        if success:
            self.modified_files.add(Path(file_path))
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(
            f"Healing attempt {self.healing_attempts[file_path]} "
            f"for {file_path}: {status}"
        )
    
    def set_thermal_profile(self, profile: ThermalProfile):
        """Set thermal profile for LLM generation."""
        self.thermal_profile = profile
        
        profile_configs = {
            ThermalProfile.CREATIVITY_MAX: 0.9,
            ThermalProfile.CREATIVITY_HIGH: 0.8,
            ThermalProfile.BALANCED: 0.7,
            ThermalProfile.STRUCTURED: 0.3,
            ThermalProfile.PRECISION: 0.1
        }
        
        self.gemini_config.temperature = profile_configs[profile]
        logger.info(f"Thermal profile set: {profile.value} (temp={self.gemini_config.temperature})")
    
    def build_context_buffer(self, file_summaries: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build omniscient context buffer from file summaries.
        
        Args:
            file_summaries: File summaries from cartographer
            
        Returns:
            Build statistics
        """
        logger.info("🌐 Building context buffer...")
        
        self.context_buffer = ""
        self.file_index = {}
        self.file_contents = {}
        
        stats = {
            "files_processed": 0,
            "total_characters": 0,
            "skipped": 0
        }
        
        buffer_parts = []
        current_position = 0
        
        for file_key, data in file_summaries.items():
            try:
                file_path = data["absolute_path"]
                relative_path = data["path"]
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) > 5000:
                    content = content[:5000] + "\n...[truncated]..."
                
                header = f"\n{'='*60}\n"
                header += f"FILE: {relative_path}\n"
                header += f"SUMMARY: {data.get('summary', 'No summary')}\n"
                header += f"{'='*60}\n\n"
                
                start_pos = current_position
                buffer_parts.append(header)
                buffer_parts.append(content)
                buffer_parts.append("\n\n")
                
                current_position += len(header) + len(content) + 4
                
                self.file_index[file_key] = {
                    "start": start_pos,
                    "end": current_position - 1,
                    "path": relative_path,
                    "summary": data.get("summary")
                }
                
                self.file_contents[file_key] = content
                
                stats["files_processed"] += 1
                stats["total_characters"] += len(content)
            
            except Exception as e:
                logger.error(f"Failed to process {file_key}: {e}")
                stats["skipped"] += 1
        
        self.context_buffer = "".join(buffer_parts)
        stats["buffer_size"] = len(self.context_buffer)
        
        logger.info(f"✅ Context buffer built: {stats['files_processed']} files")
        
        return stats
    
    def query_context(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the context buffer.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of matching files with content
        """
        if not self.context_buffer:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for file_key, index_data in self.file_index.items():
            if query_lower in index_data["path"].lower():
                content = self.file_contents.get(file_key, "")
                matches.append({
                    "file": file_key,
                    "path": index_data["path"],
                    "summary": index_data["summary"],
                    "content": content[:1000] + "..." if len(content) > 1000 else content
                })
            
            if len(matches) >= max_results:
                break
        
        return matches
    
    def reset_for_new_cycle(self):
        """Reset context for a new validation cycle."""
        self.cycle_id += 1
        self.signals.clear()
        self.modified_files.clear()
        self.start_time = datetime.utcnow()
        self.status = "RUNNING"
        
        logger.info(f"🔄 Starting cycle {self.cycle_id}")
    
    def complete_cycle(self, status: str = "COMPLETED"):
        """Complete the current cycle."""
        self.status = status
        self.save_memory()
        
        logger.info(f"✅ Cycle {self.cycle_id} completed: {status}")


_global_context: Optional[UniversalContext] = None


def get_context() -> UniversalContext:
    """
    Get the global Universal Context instance (singleton).
    
    Returns:
        UniversalContext instance
    """
    global _global_context
    
    if _global_context is None:
        _global_context = UniversalContext()
    
    return _global_context


context = get_context()
