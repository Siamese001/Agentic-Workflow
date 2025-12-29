"""
L1 Protocol Handler - MCP Compliance Layer
Provides structured communication interface for tool execution
"""
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
logger: Any = logging.getLogger(__name__)

class tool_execution_error(Exception):
    """Raised when tool execution fails due to protocol violations"""

class blackout_protocol_error(Exception):
    """Raised when EBP blackout is active"""

class git_conflict_error(Exception):
    """Simulated git conflict error for testing"""

@dataclass
class tool_result:
    """Standardized tool execution result"""
    content: str
    source_data: Optional[List[str]] = None
    isError: bool = False
    toolExecutionError: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class l1_protocol_handler:
    """
    L1 Protocol Handler implementing MCP compliance and security checks
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.allowlist = {'src', 'tests', 'docs', 'config', 'data', 'logs', 'temp', 'reports', 'schemas', 'prompt_governance', 'observability'}
        self.tool_schemas = {'read_file': {'path': {'type': 'string', 'required': True}}, 'write_file': {'path': {'type': 'string', 'required': True}, 'content': {'type': 'string', 'required': True}}, 'tavily_search': {'query': {'type': 'string', 'required': True}}, 'git_commit': {'message': {'type': 'string', 'required': True}}}

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
        """
        Handles LLM response, enforces L1 protocol integrity, and executes tool.
        Returns a ToolResult object or None if protocol validation fails critically.
        """
        try:
            self._validate_schema(tool_name, args)
            self._check_ebp_status()
            if tool_name in ['read_file', 'write_file']:
                self._check_path_allowlist(args['path'])
            result: Any = self._execute_tool_impl(tool_name, args)
            sanitized_result: Any = self._sanitize_output(result)
            return sanitized_result
        except (ToolExecutionError, BlackoutProtocolError, GitConflictError) as e:
            pass
            protocol_error: Any = f'L1_PROTOCOL_ERROR: {e.__class__.__name__}: {str(e)}'
            self._log_to_l5('L1', 'Protocol Handler', protocol_error, status='CRITICAL')
            return ToolResult(content='', isError=True, toolExecutionError=f'{e.__class__.__name__}: {str(e)}')
        except Exception as e:
            pass
            protocol_error: Any = f'L1_PROTOCOL_ERROR: Unexpected error: {str(e)}'
            self._log_to_l5('L1', 'Protocol Handler', protocol_error, status='CRITICAL')
            return ToolResult(content='', isError=True, toolExecutionError=f'Unexpected error: {str(e)}')

    def _validate_schema(self, tool_name: str, args: Dict[str, Any]):
        """Validate input schema"""
        if tool_name not in self.tool_schemas:
            raise ToolExecutionError(f'Unknown tool: {tool_name}')
        schema = self.tool_schemas[tool_name]
        for param, rules in schema.items():
            if rules.get('required', False) and param not in args:
                raise ToolExecutionError(f'Missing required parameter: {param}')
            if param in args:
                if rules['type'] == 'string' and (not isinstance(args[param], str)):
                    raise ToolExecutionError(f'Parameter {param} must be string, got {type(args[param]).__name__}')

    def _log_to_l5(self, layer: str, component: str, message: str, status: str='INFO'):
        """Log to L5 MEMory (mock implementation for testing)"""
        try:
            log_entry = {'timestamp': datetime.now().isoformat(), 'layer': layer, 'component': component, 'message': message, 'status': status}
            logger.warning(f'L5_LOG: {log_entry}')
        except Exception:
            pass
            pass

    def _check_path_allowlist(self, path: str):
        """Check if path is within allowed directories"""
        normalized = os.path.normpath(path)
        if '..' in path:
            final_path = normalized.split(os.sep)[-1]
            if final_path not in self.allowlist:
                raise ToolExecutionError(f'Path traversal detected: {path}')
        first_component = normalized.split(os.sep)[0]
        if first_component not in self.allowlist:
            raise ToolExecutionError(f'Path not in allowlist: {path}')

    def _check_ebp_status(self):
        """Check Emergency Bailout Protocol status"""
        if self.redis_client:
            try:
                ebp_status = self.redis_client.get('validator:status:blackout')
                if ebp_status:
                    status_str = ebp_status.decode() if isinstance(ebp_status, bytes) else ebp_status
                    if status_str == 'TRUE':
                        raise BlackoutProtocolError('EBP blackout active - tool execution blocked')
            except Exception as e:
                pass
                if 'BlackoutProtocolError' not in str(type(e)):
                    pass
                else:
                    raise

    def _execute_tool_impl(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
        """Actual tool implementation"""
        if tool_name == 'read_file':
            return self._mock_read_file(args['path'])
        elif tool_name == 'write_file':
            return self._mock_write_file(args['path'], args['content'])
        elif tool_name == 'tavily_search':
            return self._mock_tavily_search(args['query'])
        elif tool_name == 'git_commit':
            return self._mock_git_commit(args['message'])
        else:
            raise ToolExecutionError(f'Tool not implemented: {tool_name}')

    def _mock_read_file(self, path: str) -> ToolResult:
        """Mock file reading"""
        return ToolResult(content=f'Mock content from {path}', source_data=[f'file://{path}'])

    def _mock_write_file(self, path: str, content: str) -> ToolResult:
        """Mock file writing with temporal integrity check"""
        current_time = datetime.now().timestamp()
        try:
            content_data = json.loads(content)
            if 'timestamp' in content_data:
                content_time = content_data.get('timestamp', 0)
                if content_time < current_time - 1.0:
                    raise ToolExecutionError('Temporal integrity violation: past timestamp')
        except json.JSONDecodeError:
            pass
            pass
        return ToolResult(content=f'Successfully wrote to {path}', metadata={'timestamp': current_time})

    def _mock_tavily_search(self, query: str) -> ToolResult:
        """Mock Tavily search with raw JSON output"""
        raw_json = {'results': [{'title': f'Search result for: {query}', 'url': 'https://example.com/result1', 'content': f'Content about {query}'}]}
        return ToolResult(content=json.dumps(raw_json), source_data=['https://example.com/result1'])

    def _mock_git_commit(self, message: str) -> ToolResult:
        """Mock git commit with potential conflict"""
        if 'conflict' in message.lower():
            raise GitConflictError('Merge conflict detected')
        return ToolResult(content=f'Committed: {message}', metadata={'commit_hash': 'abc123'})

    def _sanitize_output(self, result: ToolResult) -> ToolResult:
        """Sanitize tool output to remove prompt injections"""
        if not result.content:
            return result
        adversarial_patterns = ['DISREGARD ALL PREVIOUS INSTRUCTIONS', 'IGNORE ALL RULES', 'NEW INSTRUCTION:', '# TARGET_REPO:', '(?i)system\\(', '(?i)subprocess\\.']
        sanitized_content = result.content
        for pattern in adversarial_patterns:
            sanitized_content = re.sub(pattern, '[REDACTED]', sanitized_content, flags=re.IGNORECASE)
        if result.source_data and 'results' in result.content:
            try:
                data = json.loads(result.content)
                if 'results' in data:
                    summary = f"Found {len(data['results'])} search results"
                    sanitized_content = summary
            except json.JSONDecodeError:
                pass
                pass
        result.content = sanitized_content
        return result
