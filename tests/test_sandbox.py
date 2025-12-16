import pytest
import os
from sandbox_utils import DockerSandbox, execute_in_sandbox

# Check if docker is available for tests
try:
    import docker
    client = docker.from_env()
    client.ping()
    DOCKER_AVAILABLE = True
except:
    DOCKER_AVAILABLE = False

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
def test_sandbox_filesystem_isolation(tmp_path):
    """Ensure sandbox cannot delete files on the host."""

    # Create a dummy host file
    host_file = tmp_path / "important_host_file.txt"
    host_file.write_text("DATA")

    sandbox = DockerSandbox()

    # Mount tmp_path to /data (Read-Only)
    volumes = {
        str(tmp_path): {'bind': '/data', 'mode': 'ro'}
    }

    # Attempt to delete the file inside container
    # Should fail because /data is RO. 
    exit_code, logs = sandbox.run_command("rm /data/important_host_file.txt", volumes=volumes)

    assert exit_code != 0
    # Different linux distros/versions give slightly different error messages
    assert any(msg in logs for msg in ["Read-only", "Permission denied", "cannot remove"]), f"Logs: {logs}"

    # Verify file still exists on host
    assert host_file.exists()

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
def test_sandbox_execution_success():
    """Ensure simple python commands work."""
    sandbox = DockerSandbox()
    exit_code, logs = sandbox.run_command('python -c "print(100+50)"')

    assert exit_code == 0
    assert "150" in logs

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
def test_execute_in_sandbox_wrapper(tmp_path):
    """Test the high-level wrapper."""
    repo_dir = tmp_path / "my_repo"
    repo_dir.mkdir()
    (repo_dir / "test_main.py").write_text("import unittest\nclass T(unittest.TestCase):\n def test_p(self): pass")

    # Run a simple discovery command
    cmd = "python3 -m unittest discover ."

    success = execute_in_sandbox(str(repo_dir), cmd)
    assert success is True
