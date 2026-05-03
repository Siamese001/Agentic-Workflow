"""W5 tests: apps_rg Fort Knox proof producer.

Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
Phase: W5.P1-P2 - APPS-REQ-RG-* claim definitions and proof producer
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestRGClaimDefinitions:
    """Verify APPS-REQ-RG-* claim set is defined correctly."""

    def test_claim_set_has_8_claims(self) -> None:
        """APPS-REQ-RG-001 through -008 are defined."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import _RG_CLAIMS
        assert len(_RG_CLAIMS) == 8

    def test_claim_ids_are_sequential(self) -> None:
        """Claim IDs follow APPS-REQ-RG-NNN pattern."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import _RG_CLAIMS
        expected_ids = [f"APPS-REQ-RG-{i:03d}" for i in range(1, 9)]
        actual_ids = [c["claim_id"] for c in _RG_CLAIMS]
        assert actual_ids == expected_ids

    def test_every_claim_has_required_fields(self) -> None:
        """Every claim dict has claim_id, title, required_artifact, required_fields."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import _RG_CLAIMS
        for claim in _RG_CLAIMS:
            assert "claim_id" in claim
            assert "title" in claim
            assert "required_artifact" in claim
            assert "required_fields" in claim
            assert isinstance(claim["required_fields"], list)
            assert len(claim["required_fields"]) > 0

    def test_route_contract_claim_has_v15_fields(self) -> None:
        """APPS-REQ-RG-001 checks V15 RouteContract binding fields."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import _RG_CLAIMS
        claim_001 = next(c for c in _RG_CLAIMS if c["claim_id"] == "APPS-REQ-RG-001")
        required = claim_001["required_fields"]
        # Must include v15 canonical binding fields
        assert "route_digest" in required
        assert "hmac_sig" in required
        assert "policy_hash" in required
        assert "blueprint_hash" in required
        assert "replay_key" in required


class TestProofProducer:
    """Test proof producer behavior against missing/present artifacts."""

    def test_produce_proof_missing_artifact(self, tmp_path: Path) -> None:
        """produce_proof returns NOT_VERIFIED when artifact missing."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import produce_proof, _RG_CLAIMS

        claim = _RG_CLAIMS[0]
        # tmp_path is empty - no artifacts
        proof = produce_proof(claim, tmp_path)

        assert proof["assertion_result"] == "NOT_VERIFIED"
        assert "Missing artifact" in proof["reason"]
        assert proof["artifact_sha256"] is None

    def test_produce_proof_missing_fields(self, tmp_path: Path) -> None:
        """produce_proof returns NOT_VERIFIED when required fields missing."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import produce_proof, _RG_CLAIMS

        claim = _RG_CLAIMS[0]
        # Create artifact with empty content
        artifact = tmp_path / claim["required_artifact"]
        artifact.write_text(json.dumps({"unrelated_field": "foo"}))

        proof = produce_proof(claim, tmp_path)
        assert proof["assertion_result"] == "NOT_VERIFIED"
        assert "Missing fields" in proof["reason"]
        assert proof["artifact_sha256"] is not None  # artifact exists

    def test_produce_proof_all_fields_present(self, tmp_path: Path) -> None:
        """produce_proof returns PASS when all required fields present."""
        from tools.cert.apps_e2e.apps_rg_proof_producer import produce_proof, _RG_CLAIMS

        claim = _RG_CLAIMS[0]
        # Create artifact with all required fields
        complete_data = {field: f"value_{field}" for field in claim["required_fields"]}
        artifact = tmp_path / claim["required_artifact"]
        artifact.write_text(json.dumps(complete_data))

        proof = produce_proof(claim, tmp_path)
        assert proof["assertion_result"] == "PASS"
        assert proof["artifact_sha256"] is not None
        assert proof["artifact_path"] is not None


class TestEmitProofsNoRun:
    """Test behavior when no run directories exist."""

    def test_emit_proofs_missing_runs_root(self, tmp_path: Path, monkeypatch) -> None:
        """emit_proofs returns all NOT_VERIFIED when no runs exist."""
        from tools.cert.apps_e2e import apps_rg_proof_producer

        # Point RUNS_ROOT at empty dir
        empty_runs = tmp_path / "empty_runs"
        empty_runs.mkdir()
        monkeypatch.setattr(apps_rg_proof_producer, "RUNS_ROOT", empty_runs)

        out_dir = tmp_path / "out"
        proofs = apps_rg_proof_producer.emit_proofs(out_dir)

        assert len(proofs) == 8
        for proof in proofs:
            assert proof["assertion_result"] == "NOT_VERIFIED"
            assert "No run directories found" in proof["reason"]

    def test_emit_proofs_writes_individual_files(self, tmp_path: Path, monkeypatch) -> None:
        """emit_proofs writes one JSON file per claim + a combined bundle."""
        from tools.cert.apps_e2e import apps_rg_proof_producer

        empty_runs = tmp_path / "empty_runs"
        empty_runs.mkdir()
        monkeypatch.setattr(apps_rg_proof_producer, "RUNS_ROOT", empty_runs)

        out_dir = tmp_path / "out"
        apps_rg_proof_producer.emit_proofs(out_dir)

        # 8 individual proofs + 1 bundle
        files = list(out_dir.iterdir())
        json_files = [f for f in files if f.suffix == ".json"]
        assert len(json_files) == 9  # 8 claim files + 1 bundle

        bundle_path = out_dir / "apps_rg_proof_bundle.json"
        assert bundle_path.exists()
        bundle = json.loads(bundle_path.read_text())
        assert bundle["claim_count"] == 8
        assert bundle["pass_count"] == 0
        assert bundle["not_verified_count"] == 8
