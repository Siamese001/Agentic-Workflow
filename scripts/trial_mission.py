#!/usr/bin/env python3
"""
TRIAL MISSION: Operation Subatomic Cleanroom

This script runs the Hardened Swarm in trial mode, focusing specifically on:
- Project Root (stray files)
- scripts/ directory (generic names, monoliths)

Mission Phases:
1. Void Purification - Clean root directory
2. Depth & Taxonomy Alignment - Structure scripts properly
3. Atomicity Surgery - Split large scripts
4. Semantic Literacy - Add documentation
5. Import Repair - Fix all references
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path to import canon_validator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canon_validator_agentic import SwarmScheduler, ValidationContext

class TrialValidationContext(ValidationContext):
    """Filtered ValidationContext for trial mission focusing on root and scripts/."""
    
    def __init__(self):
        super().__init__()
        # Initialize modified_files tracking if not present
        if not hasattr(self, 'modified_files'):
            self.modified_files = set()
        
        # Filter python_files to only include root and scripts/ directory
        filtered_files = []
        for file_path in self.python_files:
            # Normalize path
            norm_path = file_path.replace('\\', '/')
            
            # Include if in root or scripts/ directory
            if (norm_path.count('/') == 0 or  # Root file
                norm_path.startswith('scripts/') or  # In scripts/
                norm_path.startswith('./scripts/')):  # Scripts with ./
                filtered_files.append(file_path)
        
        self.python_files = filtered_files
        print(f"\n🎯 TRIAL MODE: Targeting {len(self.python_files)} files")
        print(f"   📍 Root files: {sum(1 for f in self.python_files if f.count('/') == 0)}")
        print(f"   📂 Scripts: {sum(1 for f in self.python_files if 'scripts' in f)}")

class TrialSwarmScheduler(SwarmScheduler):
    """SwarmScheduler configured for trial mission."""
    
    def __init__(self):
        # Use TrialValidationContext instead of regular ValidationContext
        self.ctx = TrialValidationContext()
        
        # Same phase configuration as main scheduler
        self.phases = {
            # 1. INTEGRITY (Sequential, Safe)
            "integrity_seq": [
                Historian(self.ctx),        # Skip unchanged
                VoidEnforcer(self.ctx),      # Root hygiene
                SystemArchitect(self.ctx),   # Core check
                DepthEnforcer(self.ctx),     # Nesting 3-5
                AtomicityEnforcer(self.ctx), # Split >200 lines
                TaxonomyEnforcer(self.ctx),  # Refine names & patch imports
                DocEnforcer(self.ctx)        # Semantic Literacy (Docstrings)
            ],
            # 2. CURATION (Organization)
            "curator_seq": [
                TheCurator(self.ctx) # Moves scripts to Depth 3
            ],
            # 3. PARALLEL SWARM (Reduced for trial)
            "parallel_swarm": [
                SafetyInspector(self.ctx),   # Security & Secrets
                TypeMechanic(self.ctx),      # Type Checking
                StructuralEngineer(self.ctx), # Architecture
                DocumentationAgent(self.ctx) # Documentation Generation
            ],
            # 4. VERIFICATION (Regression)
            "verification_seq": [
                TestPilot(self.ctx)          # Run tests after mutations
            ]
        }
    
    async def run_trial_mission(self):
        """Run the trial mission with enhanced logging."""
        print("\n" + "="*60)
        print("🚀 INITIATING TRIAL MISSION: Operation Subatomic Cleanroom")
        print("="*60)
        print(f"⏰ Started: {datetime.now().isoformat()}")
        print(f"🎯 Target: Project Root + scripts/ directory")
        print("="*60)
        
        # Create trial log
        trial_log_path = "observability/audit/trial_mission_log.md"
        os.makedirs(os.path.dirname(trial_log_path), exist_ok=True)
        
        with open(trial_log_path, 'w', encoding='utf-8') as f:
            f.write(f"# Trial Mission Log: Operation Subatomic Cleanroom\n\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write(f"Target: Project Root + scripts/ directory\n\n")
            f.write("## Mission Phases\n\n")
        
        # Phase 1: Integrity
        print("\n📋 PHASE 1: INTEGRITY SEQUENCE")
        print("-" * 40)
        for i, agent in enumerate(self.phases["integrity_seq"], 1):
            print(f"\n[{i}/7] {agent.__class__.__name__}")
            await agent.execute()
        
        # Phase 2: Curation
        print("\n📋 PHASE 2: CURATION SEQUENCE")
        print("-" * 40)
        for i, agent in enumerate(self.phases["curator_seq"], 1):
            print(f"\n[{i}/1] {agent.__class__.__name__}")
            await agent.execute()
        
        # Phase 3: Parallel Swarm
        print("\n📋 PHASE 3: PARALLEL SWARM")
        print("-" * 40)
        print("⚡ Unleashing Parallel Swarm...")
        parallel_tasks = [agent.execute() for agent in self.phases["parallel_swarm"]]
        if parallel_tasks:
            await asyncio.gather(*parallel_tasks)
        
        # Phase 4: Verification
        print("\n📋 PHASE 4: VERIFICATION")
        print("-" * 40)
        for i, agent in enumerate(self.phases["verification_seq"], 1):
            print(f"\n[{i}/1] {agent.__class__.__name__}")
            await agent.execute()
        
        # Mission complete
        print("\n" + "="*60)
        print("🏁 TRIAL MISSION COMPLETE")
        print("="*60)
        print(f"⏰ Completed: {datetime.now().isoformat()}")
        
        # Update trial log
        with open(trial_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\nCompleted: {datetime.now().isoformat()}\n")
            f.write(f"\n## Summary\n")
            f.write(f"- Files processed: {len(self.ctx.python_files)}\n")
            f.write(f"- Signals: {self.ctx.signals}\n")
            f.write(f"- Results: {len(self.ctx.results)} validations\n")

# Import required agents
from canon_validator_agentic import (
    Historian, VoidEnforcer, SystemArchitect, DepthEnforcer,
    AtomicityEnforcer, TaxonomyEnforcer, DocEnforcer,
    TheCurator, SafetyInspector, TypeMechanic,
    StructuralEngineer, DocumentationAgent, TestPilot
)

async def main():
    """Main entry point for trial mission."""
    scheduler = TrialSwarmScheduler()
    await scheduler.run_trial_mission()

if __name__ == "__main__":
    print("🎯 TRIAL MISSION CONFIRMED")
    print("   Target: Project Root + scripts/")
    print("   Mode: Subatomic Cleanroom")
    print()
    print("⚠️  WARNING: This will modify files!")
    print("   Press Ctrl+C to abort...")
    
    try:
        input("   Press Enter to continue...")
    except KeyboardInterrupt:
        print("\n❌ Mission aborted by user")
        sys.exit(0)
    
    # Run the mission
    asyncio.run(main())
