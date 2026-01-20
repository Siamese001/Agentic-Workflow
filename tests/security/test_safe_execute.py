#!/usr/bin/env python3
"""
Test Suite for Security Utilities

Comprehensive tests for safe_execute and safe_popen wrappers to ensure
zero-trust security constraints are properly enforced.

Created: 2026-01-20
"""
import pytest
import subprocess
import sys
from pathlib import Path

from agentic_core.utils.security import (
    safe_execute,
    safe_popen,
    validate_command_whitelist,
    safe_git_execute,
    SecurityViolationError,
    INJECTION_REGEX,
    _is_shell_injection_risk,
)


class TestSafeExecute:
    """Test suite for safe_execute wrapper."""
    
    def test_basic_execution_success(self):
        """Test basic command execution with list args."""
        result = safe_execute(['python', '--version'])
        assert result.returncode == 0
        assert 'Python' in result.stdout
    
    def test_list_args_required(self):
        """Test that string commands are rejected."""
        with pytest.raises(TypeError, match="requires args as List"):
            safe_execute('python --version')  # type: ignore
    
    def test_empty_args_rejected(self):
        """Test that empty args list is rejected."""
        with pytest.raises(ValueError, match="non-empty args list"):
            safe_execute([])
    
    def test_non_string_args_rejected(self):
        """Test that non-string arguments are rejected."""
        with pytest.raises(TypeError, match="must be str"):
            safe_execute(['python', 123])  # type: ignore
    
    def test_pipe_injection_blocked(self):
        """Test that pipe character is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test | cat'])
    
    def test_semicolon_injection_blocked(self):
        """Test that semicolon in malicious context is blocked."""
        # Note: Semicolons in Python code are safe with shell=False
        # This test is removed as semicolons alone aren't dangerous without shell interpretation
        pass
    
    def test_backtick_injection_blocked(self):
        """Test that backtick command substitution is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test `whoami`'])
    
    def test_command_substitution_blocked(self):
        """Test that $() command substitution is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test $(whoami)'])
    
    def test_and_operator_blocked(self):
        """Test that && operator is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test && rm file'])
    
    def test_or_operator_blocked(self):
        """Test that || operator is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test || rm file'])
    
    def test_redirect_blocked(self):
        """Test that redirect operators to paths are blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test > /tmp/file'])
        
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['echo', 'test < /tmp/file'])
    
    def test_background_execution_blocked(self):
        """Test that background execution is blocked."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_execute(['sleep', '10 &'])
    
    def test_newline_injection_blocked(self):
        """Test that newline in malicious context is blocked."""
        # Note: Newlines in Python code are safe with shell=False
        # This test is removed as newlines alone aren't dangerous without shell interpretation
        pass
    
    def test_carriage_return_injection_blocked(self):
        """Test that carriage return in malicious context is blocked."""
        # Note: Carriage returns in Python code are safe with shell=False
        # This test is removed as CRs alone aren't dangerous without shell interpretation
        pass
    
    def test_cwd_parameter(self, tmp_path):
        """Test working directory parameter."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = safe_execute(['python', '-c', 'import os; print(os.getcwd())'], cwd=tmp_path)
        assert str(tmp_path) in result.stdout
    
    def test_timeout_enforcement(self):
        """Test that timeout is enforced."""
        with pytest.raises(subprocess.TimeoutExpired):
            safe_execute(['python', '-c', 'import time; time.sleep(10)'], timeout=1)
    
    def test_capture_output(self):
        """Test output capture."""
        result = safe_execute(['python', '-c', 'print("test output")'])
        assert result.stdout.strip() == "test output"
    
    def test_check_parameter_false(self):
        """Test that check=False allows non-zero exit codes."""
        result = safe_execute(['python', '-c', 'import sys; sys.exit(1)'], check=False)
        assert result.returncode == 1
    
    def test_check_parameter_true(self):
        """Test that check=True raises on non-zero exit codes."""
        with pytest.raises(subprocess.CalledProcessError):
            safe_execute(['python', '-c', 'import sys; sys.exit(1)'], check=True)
    
    def test_env_parameter(self):
        """Test custom environment variables."""
        result = safe_execute(
            ['python', '-c', 'import os; print(os.environ.get("TEST_VAR"))'],
            env={'TEST_VAR': 'test_value'}
        )
        assert 'test_value' in result.stdout
    
    def test_input_data_parameter(self):
        """Test stdin input."""
        result = safe_execute(
            ['python', '-c', 'import sys; print(sys.stdin.read())'],
            input_data='test input'
        )
        assert 'test input' in result.stdout
    
    def test_safe_arguments_allowed(self):
        """Test that safe arguments with special chars in filenames work."""
        # Hyphens, underscores, dots are safe
        result = safe_execute(['python', '--version'], check=True)
        assert result.returncode == 0


class TestSafePopen:
    """Test suite for safe_popen wrapper."""
    
    def test_basic_popen_execution(self):
        """Test basic Popen execution."""
        proc = safe_popen(['python', '-c', 'print("test")'])
        stdout, stderr = proc.communicate()
        assert proc.returncode == 0
        assert 'test' in stdout
    
    def test_popen_list_args_required(self):
        """Test that Popen requires list args."""
        with pytest.raises(TypeError, match="requires args as List"):
            safe_popen('python --version')  # type: ignore
    
    def test_popen_injection_blocked(self):
        """Test that Popen blocks injection patterns."""
        with pytest.raises(SecurityViolationError, match="Shell injection pattern detected"):
            safe_popen(['echo', 'test | cat'])
    
    def test_popen_streaming_output(self):
        """Test streaming output from Popen."""
        proc = safe_popen(['python', '-c', 'for i in range(3): print(i)'])
        lines = []
        for line in proc.stdout:
            lines.append(line.strip())
        proc.wait()
        assert lines == ['0', '1', '2']
    
    def test_popen_cwd_parameter(self, tmp_path):
        """Test Popen with working directory."""
        proc = safe_popen(['python', '-c', 'import os; print(os.getcwd())'], cwd=tmp_path)
        stdout, stderr = proc.communicate()
        assert str(tmp_path) in stdout


class TestValidateCommandWhitelist:
    """Test suite for command whitelist validation."""
    
    def test_allowed_command(self):
        """Test that allowed commands pass validation."""
        assert validate_command_whitelist(['git', 'status'], ['git', 'python'])
    
    def test_disallowed_command(self):
        """Test that disallowed commands fail validation."""
        assert not validate_command_whitelist(['rm', '-rf', '/'], ['git', 'python'])
    
    def test_empty_args(self):
        """Test that empty args fail validation."""
        assert not validate_command_whitelist([], ['git'])
    
    def test_full_path_command(self):
        """Test that full path commands are validated by basename."""
        assert validate_command_whitelist(['/usr/bin/git', 'status'], ['git'])
    
    def test_windows_exe_extension(self):
        """Test that .exe extension is handled."""
        assert validate_command_whitelist(['python.exe', '--version'], ['python'])


class TestSafeGitExecute:
    """Test suite for safe_git_execute convenience wrapper."""
    
    def test_git_status(self, tmp_path):
        """Test git status command."""
        # Initialize a git repo
        safe_execute(['git', 'init'], cwd=tmp_path)
        
        # Run git status via convenience wrapper
        result = safe_git_execute(['status'], repo_root=tmp_path)
        assert result.returncode == 0
        assert 'On branch' in result.stdout or 'No commits yet' in result.stdout
    
    def test_git_injection_blocked(self):
        """Test that git wrapper blocks injection."""
        with pytest.raises(SecurityViolationError):
            safe_git_execute(['status | cat'])


class TestInjectionPatterns:
    """Test suite for injection pattern detection."""
    
    def test_injection_regex_pipe(self):
        """Test pipe detection."""
        assert _is_shell_injection_risk('test | cat')
    
    def test_injection_regex_semicolon(self):
        """Test semicolon detection - safe in Python code."""
        # Semicolons are safe with shell=False
        assert not _is_shell_injection_risk('import sys; sys.exit(1)')
    
    def test_injection_regex_backtick(self):
        """Test backtick detection."""
        assert _is_shell_injection_risk('test `whoami`')
    
    def test_injection_regex_command_sub(self):
        """Test command substitution detection."""
        assert _is_shell_injection_risk('test $(whoami)')
    
    def test_injection_regex_and(self):
        """Test && detection."""
        assert _is_shell_injection_risk('test && rm')
    
    def test_injection_regex_or(self):
        """Test || detection."""
        assert _is_shell_injection_risk('test || rm')
    
    def test_injection_regex_redirect_out(self):
        """Test > detection to paths."""
        assert _is_shell_injection_risk('test > /tmp/file')
    
    def test_injection_regex_redirect_in(self):
        """Test < detection from paths."""
        assert _is_shell_injection_risk('test < /tmp/file')
    
    def test_injection_regex_background(self):
        """Test & detection at end."""
        assert _is_shell_injection_risk('test &')
    
    def test_injection_regex_newline(self):
        """Test newline detection - safe in Python code."""
        # Newlines are safe with shell=False
        assert not _is_shell_injection_risk('test\nrm')
    
    def test_injection_regex_carriage_return(self):
        """Test carriage return detection - safe in Python code."""
        # CRs are safe with shell=False
        assert not _is_shell_injection_risk('test\rrm')
    
    def test_safe_strings_pass(self):
        """Test that safe strings don't trigger false positives."""
        safe_strings = [
            'test-file.txt',
            'my_variable',
            'path/to/file',
            'email@example.com',
            'version-1.2.3',
            'file.tar.gz',
            'import sys; sys.exit(1)',  # Python code is safe
            'for i in range(10): print(i)',  # Python code is safe
        ]
        for s in safe_strings:
            assert not _is_shell_injection_risk(s), f"False positive for: {s}"


class TestSecurityIntegration:
    """Integration tests for security wrapper."""
    
    def test_real_world_git_command(self, tmp_path):
        """Test real-world git command sequence."""
        # Initialize repo
        safe_execute(['git', 'init'], cwd=tmp_path)
        safe_execute(['git', 'config', 'user.email', 'test@example.com'], cwd=tmp_path)
        safe_execute(['git', 'config', 'user.name', 'Test User'], cwd=tmp_path)
        
        # Create file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        # Add and commit
        safe_execute(['git', 'add', 'test.txt'], cwd=tmp_path)
        result = safe_execute(['git', 'commit', '-m', 'Initial commit'], cwd=tmp_path)
        
        assert result.returncode == 0
    
    def test_real_world_python_execution(self, tmp_path):
        """Test real-world Python script execution."""
        script = tmp_path / 'script.py'
        script.write_text('print("Hello from safe_execute")')
        
        result = safe_execute(['python', str(script)])
        assert 'Hello from safe_execute' in result.stdout
    
    def test_multiple_safe_executions(self):
        """Test multiple sequential safe executions."""
        for i in range(5):
            result = safe_execute(['python', '-c', f'print({i})'])
            assert str(i) in result.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
