"""
Test suite for CredentialScannerAgent

Risk 4: Hardcoded Credential Detection
Tests the scanner's ability to detect various types of credentials.
"""
import shutil
import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.CredentialScannerAgent import CredentialScannerAgent


class TestCredentialScannerAgent:
    """Test suite for credential detection."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def scanner(self):
        """Create a CredentialScannerAgent instance."""
        return CredentialScannerAgent()

    def test_scanner_initialization(self, scanner):
        """Test that scanner initializes correctly."""
        assert scanner is not None
        assert len(scanner.PATTERNS) > 0
        assert len(scanner.SCANNABLE_EXTENSIONS) > 0

    def test_detect_aws_access_key(self, scanner, temp_repo):
        """Test detection of AWS access keys."""
        test_file = temp_repo / "config.py"
        test_file.write_text(
            'AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"\n'
            'AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("aws" in m["type"].lower() for m in results["matches"])

    def test_detect_github_token(self, scanner, temp_repo):
        """Test detection of GitHub tokens."""
        test_file = temp_repo / "secrets.py"
        test_file.write_text(
            'GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("github" in m["type"].lower() for m in results["matches"])

    def test_detect_private_key(self, scanner, temp_repo):
        """Test detection of RSA private keys."""
        test_file = temp_repo / "key.pem"
        test_file.write_text(
            '-----BEGIN RSA PRIVATE KEY-----\n'
            'MIIEpAIBAAKCAQEA1234567890abcdef\n'
            '-----END RSA PRIVATE KEY-----\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("private_key" in m["type"] for m in results["matches"])
        assert any(m["severity"] == "high" for m in results["matches"])

    def test_detect_generic_api_key(self, scanner, temp_repo):
        """Test detection of generic API keys."""
        test_file = temp_repo / "app.py"
        test_file.write_text(
            'API_KEY = "sk_test_1234567890abcdefghijklmnop"\n'
            'api_secret = "my_super_secret_key_12345"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1

    def test_detect_database_connection_string(self, scanner, temp_repo):
        """Test detection of database connection strings."""
        test_file = temp_repo / "db.py"
        test_file.write_text(
            'DB_URL = "postgresql://user:password123@localhost/mydb"\n'
            'MONGO_URI = "mongodb://admin:secret@localhost:27017"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("db_connection" in m["type"] for m in results["matches"])

    def test_detect_stripe_key(self, scanner, temp_repo):
        """Test detection of Stripe secret keys."""
        test_file = temp_repo / "payment.py"
        test_file.write_text(
            'STRIPE_SECRET = "sk_live_1234567890abcdefghijklmnop"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("stripe" in m["type"].lower() for m in results["matches"])

    def test_ignore_false_positives(self, scanner, temp_repo):
        """Test that false positives are filtered out."""
        test_file = temp_repo / "example.py"
        test_file.write_text(
            '# Example: API_KEY = "your_api_key_here"\n'
            'API_KEY = "example_key_placeholder"\n'
            '// This is a test comment with password = "test"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        # Should have minimal or no matches due to false positive filtering
        assert results["total_matches"] == 0 or all(
            m["confidence"] < 0.8 for m in results["matches"]
        )

    def test_scan_multiple_files(self, scanner, temp_repo):
        """Test scanning multiple files."""
        (temp_repo / "file1.py").write_text('API_KEY = "sk_test_12345678901234567890"\n')
        (temp_repo / "file2.js").write_text('const token = "ghp_1234567890abcdefghijklmnopqrstuv";\n')
        (temp_repo / "file3.yaml").write_text('aws_secret: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n')

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_files_scanned"] >= 3
        assert results["total_matches"] >= 2

    def test_exclude_archived_files(self, scanner, temp_repo):
        """Test that archived directories are excluded."""
        archive_dir = temp_repo / "archives"
        archive_dir.mkdir()
        (archive_dir / "old.py").write_text('API_KEY = "sk_test_12345678901234567890"\n')

        results = scanner.scan_for_credentials(target_path=temp_repo)

        # Should not scan files in archives
        assert not any("archives" in m["file"] for m in results["matches"])

    def test_summary_statistics(self, scanner, temp_repo):
        """Test that summary statistics are generated correctly."""
        test_file = temp_repo / "mixed.py"
        test_file.write_text(
            '# High severity\n'
            'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n'
            '# Medium severity\n'
            'password = "my_password_123"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert "summary" in results
        assert "by_severity" in results["summary"]
        assert "by_type" in results["summary"]

    def test_recommendations_generated(self, scanner, temp_repo):
        """Test that security recommendations are generated."""
        test_file = temp_repo / "creds.py"
        test_file.write_text('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n')

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert "recommendations" in results
        assert len(results["recommendations"]) > 0

    def test_heal_repository_dry_run(self, scanner, temp_repo):
        """Test heal_repository in dry_run mode."""
        test_file = temp_repo / "secrets.py"
        test_file.write_text('API_KEY = "sk_test_12345678901234567890"\n')

        # Temporarily set file_cache to use temp_repo
        from agentic_core.utils.file_cache import FileCache
        scanner.file_cache = FileCache(project_root=temp_repo)

        # First run scan to populate matches
        scanner.scan_for_credentials(target_path=temp_repo)

        heal_results = scanner.heal_repository(dry_run=True)

        assert "violations" in heal_results
        assert heal_results["fixed"] == 0  # Never auto-fix credentials
        assert heal_results["skipped"] == heal_results["violations"]

    def test_high_confidence_detection(self, scanner, temp_repo):
        """Test that high-confidence patterns are detected."""
        test_file = temp_repo / "keys.py"
        test_file.write_text(
            '-----BEGIN RSA PRIVATE KEY-----\n'
            'MIIEpAIBAAKCAQEA1234567890abcdef\n'
            '-----END RSA PRIVATE KEY-----\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["summary"]["high_confidence_count"] >= 1

    def test_jwt_token_detection(self, scanner, temp_repo):
        """Test detection of JWT tokens."""
        test_file = temp_repo / "auth.py"
        test_file.write_text(
            'TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("jwt" in m["type"].lower() for m in results["matches"])

    def test_slack_token_detection(self, scanner, temp_repo):
        """Test detection of Slack tokens."""
        test_file = temp_repo / "slack.py"
        test_file.write_text(
            'SLACK_TOKEN = "xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("slack" in m["type"].lower() for m in results["matches"])

    def test_oauth_client_secret_detection(self, scanner, temp_repo):
        """Test detection of OAuth client secrets."""
        test_file = temp_repo / "oauth.py"
        test_file.write_text(
            'CLIENT_SECRET = "my_oauth_secret_1234567890"\n'
        )

        results = scanner.scan_for_credentials(target_path=temp_repo)

        assert results["total_matches"] >= 1
        assert any("oauth" in m["type"].lower() for m in results["matches"])


class TestCredentialScannerIntegration:
    """Integration tests for credential scanner."""

    def test_scanner_with_file_cache(self, tmp_path):
        """Test that scanner integrates correctly with FileCache."""
        from agentic_core.utils.file_cache import FileCache

        test_file = tmp_path / "test.py"
        test_file.write_text('API_KEY = "sk_test_12345678901234567890"\n')

        scanner = CredentialScannerAgent()
        scanner.file_cache = FileCache(project_root=tmp_path)

        results = scanner.scan_for_credentials(target_path=tmp_path)

        assert results["status"] == "success"
        assert results["total_files_scanned"] >= 1

    def test_scanner_performance(self, tmp_path):
        """Test scanner performance on multiple files."""
        import time

        # Create 10 test files
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text(
                f'# File {i}\n'
                f'API_KEY = "sk_test_1234567890{i}"\n'
            )

        scanner = CredentialScannerAgent()

        start_time = time.time()
        results = scanner.scan_for_credentials(target_path=tmp_path)
        duration = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds for 10 files)
        assert duration < 5.0
        assert results["total_files_scanned"] == 10
