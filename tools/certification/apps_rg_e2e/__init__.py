"""Certification harness for apps_rg end-to-end proof.

Honest fail-closed proof bundle emitter. Refuses to certify spine routing
that does not exist in the current runtime. See emit_proof_bundle.py for
the contract and tests/runtime/test_apps_rg_e2e_proof.py for the verifier.
"""
