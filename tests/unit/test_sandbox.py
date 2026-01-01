import pytest
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from sandbox_utils import DockerSandbox, execute_in_sandbox
try:
    import docker
from typing import Any
    client: Any = docker.from_env()
    client.ping()
    DOCKER_AVAILABLE: Any = True
except Exception:
    pass
docker_available: Any = False

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason='Docker not available')
def test_sandbox_filesystem_isolation(tmp_path: Any) -> Any:
    """Ensure sandbox cannot delete files on the host."""
    host_file: Any = tmp_path / 'important_host_file.txt'
    host_file.write_text('DATA')
    sandbox: Any = DockerSandbox()
    volumes: Any = {str(tmp_path): {'bind': '/data', 'mode': 'ro'}}
    exit_code, logs = sandbox.run_command('rm /data/important_host_file.txt', volumes=volumes)
    assert exit_code != 0
    assert any((msg in logs for msg in ['Read-only', 'Permission denied', 'cannot remove'])), f'Logs: {logs}'
    assert host_file.exists()

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason='Docker not available')
def test_sandbox_execution_success() -> Any:
    """Ensure simple python commands work."""
    sandbox: Any = DockerSandbox()
    exit_code, logs = sandbox.run_command('python -c "print(100+50)"')
    assert exit_code == 0
    assert '150' in logs

@pytest.mark.skipif(not DOCKER_AVAILABLE, reason='Docker not available')
def test_execute_in_sandbox_wrapper(tmp_path: Any) -> Any:
    """Test the high-level wrapper."""
    repo_dir: Any = tmp_path / 'my_repo'
    repo_dir.mkdir()
    (repo_dir / 'test_main.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_p(self): pass')
    cmd: Any = 'python3 -m unittest discover .'
    success: Any = execute_in_sandbox(str(repo_dir), cmd)
    assert success is True
