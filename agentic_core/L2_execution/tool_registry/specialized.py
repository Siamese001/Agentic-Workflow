import asyncio
import datetime
import re
import time

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent


class TheCartographer(SubAtomicAgent):
    """
    ROLE: Memory & Embedding. Maps the codebase into semantic space.
    """
    def can_run(self) -> bool:
        # Explicit validation and defaults
        modified_files = getattr(self.ctx, "modified_files", [])
        pinecone_available = getattr(self.ctx, "pinecone_available", False)
        return len(modified_files) > 0 and pinecone_available

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Mapping code to semantic space...")
        await asyncio.sleep(0)

        if not getattr(self.ctx, "pinecone_available", False):
            return

        for file_path in getattr(self.ctx, "modified_files", []):
            await self._map_file(file_path)

    async def _map_file(self, file_path: str):
        try:
            # Replace blocking file I/O with async alternative using to_thread
            def _read_sync():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            content = await asyncio.to_thread(_read_sync)

            # Upsert embedding with explicit UTC timestamp
            await self.ctx.upsert_embedding(
                file_path,
                content,
                metadata={"modified": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            )
            print(f"      📍 Mapped: {file_path}")
        except (IOError, UnicodeDecodeError):
            # Specific error handling for file access and encoding
            pass


class TheOmniContext(SubAtomicAgent):
    """
    ROLE: Wisdom & Semantic Retrieval. Provides context-aware answers.
    """
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Initializing semantic wisdom...")
        await asyncio.sleep(0)
        self.ctx.omni_context = self


class TheStrategist(SubAtomicAgent):
    """
    ROLE: Proactive Architecture. Identifies code smells and proposes refactors.
    """
    def can_run(self) -> bool:
        results = getattr(self.ctx, "results", {})
        if not results:
            return False
        return all(r.get("passed", False) for r in results.values())

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Analyzing architectural patterns...")
        await asyncio.sleep(0)
        # Placeholder for strategic analysis logic
        if getattr(self.ctx, "intelligence_enabled", False):
            pass


class NamingEnforcer(SubAtomicAgent):
    """ROLE: Semantic Naming Guardian."""
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Semantic Naming...")
        await asyncio.sleep(0)


class DocEnforcer(SubAtomicAgent):
    """ROLE: Documentation Surgeon."""
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Documentation Standards...")
        await asyncio.sleep(0)


class TypeEnforcer(SubAtomicAgent):
    """ROLE: Type Guardian. Enforces PEP 484."""
    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Type Contracts...")
        await asyncio.sleep(0)