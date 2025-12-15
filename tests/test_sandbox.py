import pytest
import os
from sandbox_utils import DockerSandbox

# Skip if docker is not running
@pytest.mark.skipif(os.system("docker ps >nul 2>&1") != 0, reason="Docker not available")
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
    exit_code, logs = sandbox.run_command("rm /data/important_host_file.txt", volumes=volumes)
    
    # Should fail due to Read-Only file system
    assert exit_code != 0
    assert "Read-only file system" in logs or "cannot remove" in logs
    
    # Verify file still exists on host
    assert host_file.exists()

def test_sandbox_execution_success():
    """Ensure simple python commands work."""
    sandbox = DockerSandbox()
    exit_code, logs = sandbox.run_command('python -c "print(1+1)"')
    
    assert exit_code == 0
    assert "2" in logs.strip()

@pytest.mark.skipif(os.system("docker ps >nul 2>&1") != 0, reason="Docker not available")
def test_sandbox_python_syntax_check(tmp_path):
    """Test that sandbox can detect Python syntax errors."""
    
    # Create a Python file with syntax error
    bad_file = tmp_path / "bad_syntax.py"
    bad_file.write_text("def my_func()\n    print('missing colon')")
    
    sandbox = DockerSandbox()
    
    # Mount tmp_path to /data (Read-Only)
    volumes = {
        str(tmp_path): {'bind': '/data', 'mode': 'ro'}
    }
    
    # Try to compile the file
    exit_code, logs = sandbox.run_command("python -m py_compile /data/bad_syntax.py", volumes=volumes)
    
    # Should fail due to syntax error
    assert exit_code != 0
    assert "SyntaxError" in logs

@pytest.mark.skipif(os.system("docker ps >nul 2>&1") != 0, reason="Docker not available")
def test_sandbox_environment_variables():
    """Test that environment variables work in sandbox."""
    
    sandbox = DockerSandbox()
    
    # Set environment variables
    env = {"TEST_VAR": "test_value", "ANOTHER_VAR": "123"}
    
    exit_code, logs = sandbox.run_command("echo $TEST_VAR $ANOTHER_VAR", environment=env)
    
    assert exit_code == 0
    assert "test_value 123" in logs.strip()

@pytest.mark.skipif(os.system("docker ps >nul 2>&1") != 0, reason="Docker not available")
def test_sandbox_working_directory():
    """Test that working directory is set correctly."""
    
    sandbox = DockerSandbox()
    
    exit_code, logs = sandbox.run_command("pwd")
    
    assert exit_code == 0
    assert "/app" in logs.strip()

@pytest.mark.skipif(os.system("docker ps >nul 2>&1") != 0, reason="Docker not available")
def test_sandbox_cleanup():
    """Test that containers are properly cleaned up."""
    
    import docker
    
    # Get initial container count
    client = docker.from_env()
    initial_count = len(client.containers.list(all=True))
    
    # Run a command
    sandbox = DockerSandbox()
    sandbox.run_command("echo 'test'")
    
    # Check that container was cleaned up
    final_count = len(client.containers.list(all=True))
    assert final_count == initial_count

def test_execute_in_sandbox_function():
    """Test the high-level execute_in_sandbox function."""
    from sandbox_utils import execute_in_sandbox
    
    # This should work if Docker is available
    if os.system("docker ps >nul 2>&1") == 0:
        result = execute_in_sandbox(".", "python -c 'print(\"hello\")'")
        assert result is True
    else:
        # Should handle Docker not being available gracefully
        result = execute_in_sandbox(".", "echo 'test'")
        assert result is False
