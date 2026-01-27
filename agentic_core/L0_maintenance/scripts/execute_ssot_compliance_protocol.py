#!/usr/bin/env python3
"""
SSOT Compliance Execution Protocol - Hardened Implementation
Executes the complete multi-agent orchestration for structure blueprint alignment.
"""

import sys
import logging
import json
import os
import argparse
from pathlib import Path
from datetime import datetime

# Configure Sovereign Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [SOVEREIGN] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SSOT_Orchestrator")

def execute_phase0_validation():
    """PHASE 0: PRE-EXECUTION VALIDATION"""
    logger.info("=== PHASE 0: PRE-EXECUTION VALIDATION ===")
    
    # Step 0.1: Verify Unified SSOT Source
    try:
        # [RECONCILED] Import the Unified Master Constitution
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES
        if not SOVEREIGN_TERRITORIES:
            raise ValueError("SOVEREIGN_TERRITORIES is empty. Critical SSOT failure.")
        logger.info(f"SSOT Loaded: {len(SOVEREIGN_TERRITORIES)} territories defined")
    except ImportError as e:
        logger.critical(f"Failed to load structure blueprint: {e}")
        sys.exit(1)
    
    # Step 0.2: Initialize Agent Registry
    try:
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent  
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
        logger.info("All Sovereign Agents initialized successfully.")
        return {
            'reconciler': FilesystemSSOTReconcilerAgent,
            'location': LocationAgent,
            'hierarchy': HierarchyAgent,
            'arch_governor': ArchitectureGovernorAgent,
            'system_architect': SystemArchitectAgent,
            'territories': SOVEREIGN_TERRITORIES
        }
    except ImportError as e:
        logger.critical(f"Agent registry corruption detected: {e}")
        sys.exit(1)

def execute_phase1_discovery(agents, territory):
    """PHASE 1: TERRITORIAL DISCOVERY & DRIFT DETECTION"""
    logger.info(f"=== PHASE 1: TERRITORIAL DISCOVERY & DRIFT DETECTION - {territory} ===")
    
    # Step 1.1: Execute FilesystemSSOTReconcilerAgent
    reconciler = agents['reconciler'](project_root=Path.cwd())
    drift_report = reconciler.detect_root_drift()

    # CRITICAL: Null Pointer Protection (Test 5)
    if drift_report is None:
        logger.critical("Agent returned NoneType response - possible internal crash")
        sys.exit(1)

    logger.info("🔍 DRIFT DETECTION RESULTS:")
    logger.info(f"  Missing folders: {len(drift_report.get('missing_folders', []))}")
    logger.info(f"  Unauthorized folders: {len(drift_report.get('unauthorized_folders', []))}")
    logger.info(f"  Structure violations: {len(drift_report.get('violations', []))}")

    # CRITICAL ANALYSIS: Immediate halt on catastrophic drift to prevent cascading errors
    if len(drift_report.get('violations', [])) > 10:
        logger.critical("Excessive structural violations detected. Halting for manual review.")
        sys.exit(1)
    
    # Step 1.2: Validate Territory Compliance
    location_validator = agents['location'](project_root=Path.cwd())
    location_violations = location_validator.run()

    # CRITICAL: Null Pointer Protection for location report
    if location_violations is None:
        logger.critical("LocationAgent returned NoneType response")
        sys.exit(1)

    logger.info("📍 TERRITORIAL VALIDATION:")
    logger.info(f"  Location violations found: {len(location_violations)}")
    
    if len(location_violations) > 50:
        logger.critical("EXCESSIVE LOCATION VIOLATIONS. Immediate review required.")
        sys.exit(1)
    
    return drift_report, location_violations

def execute_phase2_alignment(agents, territory, drift_report):
    """PHASE 2: STRUCTURAL ALIGNMENT"""
    logger.info(f"=== PHASE 2: STRUCTURAL ALIGNMENT - {territory} ===")
    
    # Step 2.1: Execute HierarchyAgent for Structure Creation
    hierarchy_agent = agents['hierarchy']()
    structure_proposal = hierarchy_agent.analyze_and_propose(
        target_path=f"agentic_core/{territory}",
        blueprint_reference=agents['territories']['agentic_core']['subfolders'].get(territory, {})
    )

    # CRITICAL: Null Pointer Protection
    if structure_proposal is None:
        logger.warning("No structure proposal generated (possible agent failure).")
        return None

    logger.info("🏗️ STRUCTURE PROPOSAL:")
    logger.info(f"  Folders to create: {len(structure_proposal['create_folders'])}")
    logger.info(f"  Files to relocate: {len(structure_proposal['relocate_files'])}")
    
    # Step 2.2: Apply Structural Changes (with confirmation)
    if structure_proposal['has_changes']:
        # CRITICAL: CI/CD Environment Safety (Test 7)
        confirmation = None
        try:
            # CRITICAL: Force interactive confirmation unless overridden by strict ENV flag
            confirmation = input("⚠️ Apply structural changes? Type 'EXECUTE' to confirm: ")
        except EOFError:
            logger.critical("Running in non-interactive environment. Aborting structural changes for safety.")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.warning("User interrupted. Structural alignment aborted.")
            return None
            
        if confirmation == 'EXECUTE':
            alignment_result = hierarchy_agent.execute_structure_alignment(
                proposal=structure_proposal,
                auto_apply=True
            )
            if not alignment_result['success']:
                logger.error(f"Alignment failed: {alignment_result.get('error', 'Unknown error')}")
                sys.exit(1)
            logger.info(f"✅ Alignment completed successfully.")
            return alignment_result
        else:
            logger.warning("⏸️ Structural alignment skipped by user.")
    return None

def execute_phase3_validation(agents, territory):
    """PHASE 3: ARCHITECTURAL VALIDATION"""
    logger.info(f"=== PHASE 3: ARCHITECTURAL VALIDATION - {territory} ===")
    
    # Step 3.1: Execute ArchitectureGovernorAgent
    arch_governor = agents['arch_governor']()
    governance_report = arch_governor.comprehensive_territory_audit(
        target_territories=[territory],
        check_layer_boundaries=True,
        check_naming_conventions=True,
        check_orphaned_agents=True
    )

    # CRITICAL: Null Pointer Protection
    if governance_report is None:
        logger.critical("ArchitectureGovernorAgent returned NoneType response")
        sys.exit(1)

    logger.info("🛡️ ARCHITECTURE GOVERNANCE RESULTS:")
    
    # HARDENING: Safe dictionary access
    violations_count = (len(governance_report.get('layer_violations', [])) + 
                        len(governance_report.get('naming_violations', [])))
                        
    if violations_count > 0:
        logger.error(f"❌ FOUND {violations_count} ARCHITECTURE VIOLATIONS")
    else:
        logger.info("✅ No architecture violations found.")
    
    # Step 3.2: Execute SystemArchitectAgent
    system_architect = agents['system_architect']()
    architecture_report = system_architect.validate_core_architecture(
        target_path=f"agentic_core/{territory}"
    )

    # CRITICAL: Null Pointer Protection
    if architecture_report is None:
        logger.critical("SystemArchitectAgent returned NoneType response")
        sys.exit(1)

    logger.info("🏛️ CORE ARCHITECTURE VALIDATION:")
    
    # CRITICAL: Circular Dependency Deadlock Protection (Test 8)
    if not architecture_report['imports_valid']:
        circular_deps = architecture_report.get('circular_dependencies', [])
        if circular_deps:
            logger.critical(f"CIRCULAR DEPENDENCY DETECTED: {circular_deps}")
            logger.critical("This will cause runtime recursion errors. Immediate halt required.")
        else:
            logger.error("Invalid import structure detected in core modules.")
        # Critical fail for imports as this breaks runtime
        sys.exit(1)
    
    return governance_report, architecture_report

def execute_phase4_healing(agents, territory, governance_report):
    """PHASE 4: HEALING & CORRECTION"""
    logger.info(f"=== PHASE 4: HEALING & CORRECTION - {territory} ===")
    
    # Step 4.1: Auto-Heal Detected Violations
    arch_governor = agents['arch_governor']()
    healing_plan = arch_governor.generate_healing_plan(governance_report)

    # CRITICAL: Null Pointer Protection
    if healing_plan is None:
        logger.warning("Healing plan generation failed (returned None)")
        return None

    if healing_plan['requires_healing']:
        logger.info("🔧 HEALING PLAN GENERATED:")
        logger.info(f"  Naming fixes: {len(healing_plan['naming_fixes'])}")
        
        # CRITICAL: CI/CD Environment Safety
        try:
            # HARDENING: Proactive environment check before waiting for input
            if os.environ.get('CI') == 'true' or not sys.stdin.isatty():
                logger.critical("Refusing to execute interactive healing in headless environment.")
                sys.exit(1)
                
            healing_confirmation = input("Execute healing plan? (y/N): ")
        except EOFError:
            logger.critical("Running in non-interactive environment. Aborting healing for safety.")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.warning("User interrupted. Healing aborted.")
            return None
            
        if healing_confirmation.lower() == 'y':
            healing_result = arch_governor.execute_healing_plan(healing_plan)
            
            # CRITICAL: Healing Illusion Detection (Test 6)
            if not healing_result['success']:
                logger.error(f"Healing failed: {healing_result.get('error', 'Unknown error')}")
                sys.exit(1)
                
            logger.info(f"✅ Healing completed: {healing_result['success']}")
            
            # CRITICAL: Verify healing actually worked - don't trust success flag
            post_heal_audit = arch_governor.comprehensive_territory_audit([territory])
            if post_heal_audit is None:
                logger.critical("Post-healing audit failed (returned None)")
                sys.exit(1)
                
            # HARDENING: Fix KeyError - 'violations' key does not exist in standard report
            post_violation_count = (len(post_heal_audit.get('layer_violations', [])) + 
                                    len(post_heal_audit.get('naming_violations', [])))
            
            if post_violation_count > 0:
                logger.critical(f"Healing failed to resolve {post_violation_count} violations - Healing Illusion detected")
                sys.exit(1)
                
            logger.info("✅ Post-healing verification passed - All violations resolved")
            return healing_result
    return None

def execute_phase5_final_validation(agents, territory):
    """PHASE 5: FINAL VALIDATION & LOCKDOWN"""
    logger.info(f"=== PHASE 5: FINAL VALIDATION & LOCKDOWN - {territory} ===")
    
    # Step 5.1: Post-Compliance Validation
    final_reconciler = agents['reconciler']()
    final_drift_check = final_reconciler.execute_detailed_analysis(
        target_path=f"agentic_core/{territory}",
        auto_apply=False
    )

    final_location = agents['location'](root_path=Path("agentic_core"))
    final_location_check = final_location.validate_territory_compliance(territory=territory)

    logger.info("🎯 FINAL COMPLIANCE CHECK:")
    drift_resolved = len(final_drift_check.get('violations', [])) == 0
    
    if not drift_resolved:
        logger.critical("❌ FINAL VALIDATION FAILED: DRIFT STILL EXISTS")
        sys.exit(1)
        
    logger.info("✅ Territory secured and compliant.")
    
    # Step 5.2: Generate Compliance Certificate
    compliance_certificate = {
        'territory': territory,
        'timestamp': datetime.now().isoformat(),
        'ssot_version': 'structure_blueprint.py',
        'drift_free': drift_resolved,
        'architecturally_compliant': final_location_check['overall_compliant'],
        'agents_executed': [
            'FilesystemSSOTReconcilerAgent',
            'LocationAgent', 
            'HierarchyAgent',
            'ArchitectureGovernorAgent',
            'SystemArchitectAgent'
        ]
    }

    logger.info("📜 COMPLIANCE CERTIFICATE ISSUED:")
    print(json.dumps(compliance_certificate, indent=2))
    
    return compliance_certificate

def execute_territory_compliance(agents, territory):
    """Execute complete compliance protocol for a single territory"""
    logger.info(f"🚀 PROCESSING TERRITORY: {territory}")
    
    # Execute all phases
    drift_report, location_report = execute_phase1_discovery(agents, territory)
    alignment_result = execute_phase2_alignment(agents, territory, drift_report)
    governance_report, architecture_report = execute_phase3_validation(agents, territory)
    healing_result = execute_phase4_healing(agents, territory, governance_report)
    compliance_certificate = execute_phase5_final_validation(agents, territory)
    
    return compliance_certificate

def main(target_territory=None):
    """Main execution function"""
    logger.info("🏛️ SOVEREIGN SSOT COMPLIANCE EXECUTION PROTOCOL STARTED")
    
    # Phase 0: Validation
    agents = execute_phase0_validation()
    
    # HARDENING: Dynamic Territory Selection
    if target_territory:
        target_territories = [target_territory]
        logger.info(f"Targeting specific territory: {target_territory}")
    else:
        # [RECONCILED] Reference the unified registry
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES
        if not SOVEREIGN_TERRITORIES:
            logger.critical("No territories found in SOVEREIGN_TERRITORIES.")
            sys.exit(1)
        target_territories = [list(SOVEREIGN_TERRITORIES.keys())[0]]
        logger.warning(f"No territory specified. Defaulting to first in registry: {target_territories[0]}")
    
    # Execute compliance for each territory
    compliance_results = []
    for territory in target_territories:
        try:
            result = execute_territory_compliance(agents, territory)
            compliance_results.append(result)
            logger.info(f"✅ Territory {territory} compliance completed successfully")
        except Exception as e:
            logger.error(f"❌ Territory {territory} compliance failed: {e}")
            sys.exit(1)
    
    # Final summary
    logger.info("🎉 ALL TERRITORIES COMPLIANT - SSOT PROTOCOL COMPLETED")
    logger.info(f"Processed {len(compliance_results)} territories successfully")
    
    return compliance_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sovereign SSOT Compliance Orchestrator")
    parser.add_argument(
        "--territory", 
        type=str, 
        help="The specific folder/territory to run compliance on (e.g., prompt_governance)"
    )
    args = parser.parse_args()

    try:
        results = main(target_territory=args.territory)
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("⏸️ Protocol interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"💥 Protocol failed with critical error: {e}")
        sys.exit(1)
