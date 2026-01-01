#!/usr/bin/env python3
"""
Autonomous RAG Daemon - L3 Self-Monitoring RAG System
Watches for territory changes and triggers reindexing with debouncing
"""

import asyncio
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# NAMING FIXED: TerritoryChangeHandler → TerritoryChangeHandler
class TerritoryChangeHandler(FileSystemEventHandler):
    """L0-L3: Watch for territory healing/ingestion changes with debouncing"""
    def __init__(self, daemon):
        self.daemon = daemon
        self.last_trigger = 0
        self.debounce_seconds = 10
        super().__init__()

    def on_modified(self, event):
                    
        if event.is_directory:
            return
        if event.src_path.endswith((".py", ".json", ".yaml", ".md", ".txt")):
            current_time = time.time()
            if current_time - self.last_trigger > self.debounce_seconds:
                self.last_trigger = current_time
                # Use call_soon_threadsafe because watchdog runs in its own thread
                self.daemon.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.daemon.trigger_reindex())
                )

# NAMING FIXED: AutonomousRAGDaemon → AutonomousRagDaemon
class AutonomousRagDaemon:
    """L3: Self-monitoring RAG system with autonomous health checks"""
    
    def __init__(self, orchestrator, retriever, Historian):
        self.orchestrator = orchestrator
        self.retriever = retriever
        self.Historian = Historian
        self.loop = asyncio.get_event_loop()
        self.running = True
        
        # Self-monitoring intervals
        self.health_check_interval = 3600  # 1 hour
        self.reindex_interval = 86400  # 24 hours
        
        # Watchdog setup
        self.observer = Observer()
        self.handler = TerritoryChangeHandler(self)
        
    async def start(self):
        """Start the autonomous daemon"""
        print("[DAEMON] Starting Autonomous RAG Daemon...")
        
        # Start file system watcher
        watch_path = Path("agentic_core")
        self.observer.schedule(self.handler, str(watch_path), recursive=True)
        self.observer.start()
        
        # Start background tasks
        asyncio.create_task(self.health_check())
        asyncio.create_task(self.periodic_reindex())
        
        print("[DAEMON] Autonomous RAG Daemon online")
    async def health_check(self):
        """L5: Sovereign validation – testing the Canon against reality"""
        while self.running:
            await asyncio.sleep(self.health_check_interval)
            
            try:
                # Randomize from a small pool of 'Golden Queries'
                test_queries = ["Purpose of the Canon?", "Explain L5 safety", "How does L1 expansion work?"]
                import random
                query = random.choice(test_queries)
                
                result = await self.orchestrator.sovereign_retrieve(query)
                faithfulness = result.get("faithfulness", 0.0)
                
                # Log health metrics
                self.Historian.log_event({
                    "event": "health_check",
                    "query": query,
                    "faithfulness": faithfulness,
                    "timestamp": time.time()
                })
                
                if faithfulness < 0.75:
                    print(f"[!] Health check warning: faithfulness {faithfulness:.2f}")
                    await self.trigger_reindex()
                    
            except Exception as e:
                print(f"[!] Health check failed: {e}")
    
    async def periodic_reindex(self):
        """Periodic full reindexing"""
        while self.running:
            await asyncio.sleep(self.reindex_interval)
            await self.trigger_reindex()
    
    async def trigger_reindex(self):
        """Trigger a full reindex of the canon"""
        print("[DAEMON] Triggering reindex...")
        try:
            await self.retriever.reindex_all()
            print("[DAEMON] Reindex complete")
        except Exception as e:
            print(f"[!] Reindex failed: {e}")
    
    async def stop(self):
        """Stop the daemon"""
        print("[DAEMON] Stopping Autonomous RAG Daemon...")
        self.running = False
        self.observer.stop()
        self.observer.join()
        print("[DAEMON] Daemon stopped")