#!/usr/bin/env python3
"""
Canon Validator V2 - The Sovereign Runner
Fully refactored entry point using agentic_core.
"""
import argparse
import asyncio
import sys

# Verify Layout
try:
    pass
except ImportError:
    print("CRITICAL: 'agentic_core' or 'apps_shared' not found in path.")
    sys.exit(1)

from agentic_core.core.orchestrator import SwarmScheduler

# Check for Watchdog
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canon Validator V2")
    parser.add_argument("--daemon", action="store_true", help="Run in L5 Autonomous Mode")
    parser.add_argument("--target", type=str, help="Target specific file")
    args = parser.parse_args()

    if args.daemon:
        if not WATCHDOG_AVAILABLE:
            print("❌ Watchdog required for daemon mode: pip install watchdog")
            sys.exit(1)
            
        print("🚀 THE WATCHMAN: L5 Autonomous Mode Active")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Bridge Watchdog -> Orchestrator
        class BridgeHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.is_directory or not event.src_path.endswith('.py'): return
                print(f"\n[WATCHMAN] Change detected: {event.src_path}")
                # Fire and forget mission
                asyncio.run_coroutine_threadsafe(
                    SwarmScheduler().run_mission(target_scope=event.src_path), 
                    loop
                )

        observer = Observer()
        observer.schedule(BridgeHandler(), path='.', recursive=True)
        observer.start()
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
            
    else:
        # Standard Run
        asyncio.run(SwarmScheduler().run_mission(target_scope=args.target))
