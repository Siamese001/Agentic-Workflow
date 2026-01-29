"""
[SSOT] End-to-End Integration Test for apps_rg Modernization.
Verifies the complete data lifecycle:
K.0 (Thematic) -> Routing -> Two-Phase Gen -> Enforcement (Sign) -> Airlock -> State Commit.
"""

from apps_rg.core.sovereign_context import SovereignContext
from apps_rg.logic_nodes.resume_section_node import ResumeSectionNode
from apps_rg.logic_nodes.rg_flow_router import RGFlowRouter
from apps_rg.logic_nodes.thematic_analysis_node import ThematicAnalysisNode


class TestRGProductionFlow:
    """
    The 'System Seal' test. Proves all modernized components work in concert.
    """

    def test_end_to_end_resume_lifecycle(self):
        # 1. Initialize The Sovereign System
        ctx = SovereignContext()
        thematic_node = ThematicAnalysisNode()
        router = RGFlowRouter()
        section_node = ResumeSectionNode()  # Internal composition of TwoPhase & Enforcer

        # 2. Input Data (Simulating a Mission)
        job_description = "Senior AI Engineer. Must lead scaling initiatives."
        company_name = "FutureTech"
        profile = {"role": "Engineer", "data": "Raw profile data..."}

        # 3. Step 1: K.0 Thematic Analysis
        print("\n[1] Executing K.0 Thematic Analysis...")
        thematic_output = thematic_node(job_description, company_name)
        assert thematic_output.primary_theme is not None

        # 4. Step 2: Routing with Injected Context
        print("[2] Executing Flow Routing...")
        state = {
            "task_description": job_description,  # Required by router Gate 1
            "job_description": job_description,
            "company_name": company_name,
            "thematic_analysis": thematic_output,  # Injection
        }
        next_hop = router(state)
        # The router returns RGFlowOutput, not a simple string
        assert hasattr(next_hop, "flow_result"), (
            "Router should return RGFlowOutput with flow_result"
        )
        assert next_hop.flow_result.flow_type in [
            "generate_base_node",
            "strategic_tailor_node",
            "generate_scratch",
        ]

        # 5. Step 3: Two-Phase Generation & Enforcement
        print("[3] Executing Two-Phase Generation (Gen + Synthesis + Enforcement)...")
        # This step internally calls:
        # -> TwoPhaseNode.generate_bullets_phase_a
        # -> TwoPhaseNode.synthesize_overview_phase_b
        # -> WordCountEnforcer.enforce_with_regeneration
        # -> ValidationGate.sign_payload
        experience_result = section_node.generate_experience_section(profile, thematic_output)

        # 6. Verify Cryptographic Chain of Custody
        # CRITICAL: The signature from enforcement must be the same signature used for commit
        overview_content = experience_result["overview"]
        validation_signature = experience_result["validation_signature"]

        # Assertion: We must have a signature to commit - this proves the chain is unbroken
        assert validation_signature is not None, (
            "BROKEN LINK: Signature not propagated from Enforcer!"
        )
        assert isinstance(validation_signature, str), "BROKEN LINK: Signature is not a string!"
        assert len(validation_signature) > 0, "BROKEN LINK: Signature is empty!"

        # 7. Step 4: Transactional Commit
        print("[4] Executing Sovereign State Commit...")
        ctx.write_to_airlock("experience_section", overview_content)

        # Verify Airlock Isolation
        assert ctx.get("experience_section") is None

        # Commit with the ACTUAL signature from the enforcement chain (The Final Seal)
        # This proves the complete cryptographic chain: Enforcement -> Airlock -> State
        ctx.commit_airlock(validation_signature)

        # 8. Final Verification
        committed_data = ctx.get("experience_section")
        assert committed_data == overview_content
        print("[SUCCESS] End-to-End Lifecycle Verified.")
