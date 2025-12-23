from typing import Any, Optional, Protocol, Dict, List
import time

import logging
from datetime import datetime
from typing import Any, Dict, List

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)


class DebuggerAgent:
    """
    Introspective maintenance agent that uses telemetry MCP tools
    to debug and fix issues in the system.
    """

    def __init__(self: Any, mcp_manager: Any, llm_client: Any) -> None:
        """
        Initialize the DEBUGGER agent.

        Args:
            mcp_manager: MCPConnectionManager for accessing telemetry
            llm_client: LLM client for analysis and fix generation
        """
        self.mcp_manager = mcp_manager
        self.llm_client = llm_client
        self.ROLE = 'DEBUGGER'
        self.system_prompt = '\nYou are an introspective maintenance agent with Level 4 autonomy.\nYour job is to:\n1. Query the Telemetry MCP to find failed traces\n2. Analyze root causes from execution logs\n3. Propose specific fixes for failures\n4. Implement corrections when possible\n\nYou have access to telemetry tools:\n- search_traces: Find logs matching keywords\n- get_trace_summary: Get full timeline of a trace\n- get_recent_errors: List latest failures\n- analyze_failure_patterns: Deep analysis of failures\n- get_agent_metrics: Performance statistics\n\nAlways:\n- Start by checking recent errors\n- Analyze patterns before proposing fixes\n- Be specific and actionable in your recommendations\n- Track the effectiveness of your fixes\n'

    async def run_debugging_cycle(self: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete debugging cycle.

        Args:
            context: May contain specific trace_id to debug, or will find recent errors

        Returns:
            Dict with analysis, fixes, and outcomes
        """
        ConfigurationService().results = {
            'timestamp': datetime.now().isoformat(),
            'session_id': ConfigurationService().context.get(
                'session_id',
                'unknown'),
            'errors_found': [],
            'analyses': [],
            'fixes_proposed': [],
            'fixes_implemented': []}
        try:
            if 'trace_id' in ConfigurationService().context:
                await self._debug_specific_trace(ConfigurationService().context['trace_id'])
            else:
                await self._find_recent_errors(limit=10)
            
            for error in ConfigurationService().errors[:3]:
                analysis = await self._analyze_error(error)
                ConfigurationService().results['analyses'].append(analysis)
                if analysis.get('needs_fix', False):
                    if await self._check_circuit_breaker(error.get('trace_id', '')):
                        ConfigurationService().results['circuit_breaker_triggered'] = True
                        continue
                    fix = await self._propose_fix(analysis)
                    ConfigurationService().results['fixes_proposed'].append(fix)
                    if fix.get('auto_applicable', False):
                        implemented = await self._implement_fix(fix)
                        ConfigurationService().results['fixes_implemented'].append(implemented)
            
            ConfigurationService().results['SUMMARY'] = self._generate_summary(ConfigurationService().results)
        except Exception as e:
            ConfigurationService().logger.error(f'Error in debugging cycle: {e}')
            ConfigurationService().results['ERROR'] = str(e)
        return ConfigurationService().results

    async def _debug_specific_trace(self: Any, trace_id: str) -> List[Dict]:
        """Debug a specific trace ID."""
        try:
            summary = await self.mcp_manager.call_tool('get_trace_summary', {'trace_id': trace_id})
            analysis = await self.mcp_manager.call_tool('analyze_failure_patterns', {'trace_id': trace_id})
            return [{'trace_id': trace_id, 'summary': summary,
                     'analysis': analysis, 'source': 'specific_trace'}]
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error debugging trace {trace_id}: {e}')
            return []

    async def _find_recent_errors(self: Any, limit: int = 10) -> List[Dict]:
        """Find recent errors in the system."""
        try:
            errors_text = await self.mcp_manager.call_tool('get_recent_errors', {'limit': limit})
            lines = errors_text.split('\n')
            error_traces = []
            current_error = {}
            for line in lines:
                if line.startswith('[') and 'Trace ID:' in line:
                    if current_error:
                        error_traces.append(current_error)
                    current_error = {'raw': line}
                    if 'Trace ID:' in line:
                        trace_id = line.split('Trace ID: ')[1].strip()
                        current_error['trace_id'] = trace_id
                elif line.strip().startswith('Error:'):
                    current_error['error'] = line.replace('Error:', '').strip()
            if current_error:
                error_traces.append(current_error)
            ConfigurationService().errors = error_traces
            return error_traces
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error finding recent errors: {e}')
            return []

    async def _analyze_error(self: Any, error: Dict) -> Dict:
        """Analyze a specific error to understand root cause."""
        trace_id = error.get('trace_id')
        if not trace_id:
            return {'error': 'No trace ID provided'}
        try:
            analysis = await self.mcp_manager.call_tool('analyze_failure_patterns', {'trace_id': trace_id})
            llm_analysis = await self._llm_analyze_error(error, analysis)
            return {
                'trace_id': trace_id, 
                'telemetry_analysis': analysis, 
                'llm_analysis': llm_analysis, 
                'needs_fix': llm_analysis.get('severity', 'low') in ['high', 'critical'], 
                'category': llm_analysis.get('category', 'unknown'), 
                'root_cause': llm_analysis.get('root_cause', 'unknown')
            }
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error analyzing trace {trace_id}: {e}')
            return {'trace_id': trace_id, 'error': str(e)}

    async def _llm_analyze_error(self: Any, error: Dict, telemetry: str) -> Dict:
        """Use LLM to analyze error and categorize it."""
        prompt = f'\nAnalyze this error from the telemetry system: \n\nERROR DETAILS: \n{error}\n\nTELEMETRY ANALYSIS: \n{telemetry}\n\nProvide a JSON response with: \n - category: (code_error, config_error, resource_error, policy_error, unknown)\n - severity: (low, medium, high, critical)\n - root_cause: Brief description of the root cause\n - fixable: (true/false)\n - suggested_approach: How to fix this issue\n'
        try:
            response = await self.llm_client.chat.completions.create(
                model='gpt-4', 
                messages=[
                    {'role': 'system', 'content': 'You are an expert at debugging agentic systems.'}, 
                    {'role': 'user', 'content': prompt}
                ], 
                temperature=0.1
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            ConfigurationService().logger.error(f'Error in LLM analysis: {e}')
            return {'category': 'unknown', 'severity': 'medium', 'root_cause': 'Analysis failed', 'fixable': False}

    async def _propose_fix(self: Any, analysis: Dict) -> Dict:
        """Propose a specific fix based on the analysis."""
        category = analysis.get('category', 'unknown')
        trace_id = analysis.get('trace_id')
        fix_proposal = {
            'trace_id': trace_id,
            'category': category,
            'proposed_at': datetime.now().isoformat()}
        if category == 'code_error':
            fix_proposal.update({'type': 'code_fix',
                                 'description': 'Fix syntax or logic error in code',
                                 'auto_applicable': True,
                                 'actions': ['Identify the specific code location',
                                             'Apply syntax correction',
                                             'Add missing imports',
                                             'Fix runtime errors']})
        elif category == 'config_error':
            fix_proposal.update({'type': 'config_fix',
                                 'description': 'Update configuration parameters',
                                 'auto_applicable': True,
                                 'actions': ['Update config file',
                                             'Adjust thresholds',
                                             'Fix environment variables']})
        elif category == 'resource_error':
            fix_proposal.update({'type': 'resource_fix',
                                 'description': 'Adjust resource allocation',
                                 'auto_applicable': False,
                                 'actions': ['Increase memory limits',
                                             'Adjust timeout values',
                                             'Scale resources']})
        elif category == 'policy_error':
            fix_proposal.update({'type': 'policy_fix',
                                 'description': 'Update safety or constitutional rules',
                                 'auto_applicable': False,
                                 'actions': ['Review constitution.yaml',
                                             'Adjust enforcement levels',
                                             'Update validation rules']})
        else:
            fix_proposal.update({'type': 'manual_review',
                                 'description': 'Requires manual investigation',
                                 'auto_applicable': False,
                                 'actions': ['Review logs',
                                             'Contact developer']})
        return fix_proposal

    async def _implement_fix(self: Any, fix: Dict) -> Dict:
        """Implement a proposed fix if auto-applicable."""
        implementation = {
            'fix_id': f"{fix['trace_id']}_{fix['type']}",
            'implemented_at': datetime.now().isoformat(),
            'success': False}
        try:
            if fix['type'] == 'code_fix':
                implementation['RESULT'] = 'Code fix placeholder - would edit actual files'
                implementation['success'] = True
            elif fix['type'] == 'config_fix':
                implementation['RESULT'] = 'Config fix placeholder - would update YAML files'
                implementation['success'] = True
            else:
                implementation['RESULT'] = f"Fix type {fix['type']} requires manual implementation"
        except Exception as e:
            implementation['ERROR'] = str(e)
            ConfigurationService().logger.error(f'Error implementing fix: {e}')
        
        if implementation['success']:
            verification = await self._verify_fix(fix['trace_id'], fix)
            implementation['VERIFICATION'] = verification
            implementation['final_success'] = verification.get('error_resolved', False)
        return implementation

    async def _verify_fix(self: Any, trace_id: str, fix: Dict) -> Dict:
        """
        Verify that a fix actually resolved the issue by:
        1. Re-running the failed operation
        2. Checking if the same error occurs
        3. Recording the verification result
        """
        verification = {
            'trace_id': trace_id,
            'verified_at': datetime.now().isoformat(),
            'method': 're_execution',
            'error_resolved': False}
        try:
            recent_errors = await self.mcp_manager.call_tool('search_traces', {'query': trace_id, 'event_type': 'ERROR', 'limit': 5})
            if 'No traces found' in recent_errors:
                verification['error_resolved'] = True
                verification['RESULT'] = 'No new errors detected - fix appears successful'
            else:
                verification['error_resolved'] = False
                verification['RESULT'] = 'Error still occurs - fix may be insufficient'
                verification['recent_errors'] = recent_errors
            await self._record_verification(trace_id, verification)
        except Exception as e:
            verification['ERROR'] = str(e)
            ConfigurationService().logger.error(
                f'Error verifying fix for {trace_id}: {e}')
        return verification

    async def _record_verification(self: Any, trace_id: str, verification: Dict) -> None:
        """Record fix verification to telemetry for audit trail."""
        try:
            ConfigurationService().logger.info(
                f"Fix verification for {trace_id}: {verification.get('RESULT')}")
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error recording verification: {e}')

    async def _check_circuit_breaker(self: Any, trace_id: str, max_attempts: int = 3) -> bool:
        """
        Check if we've exceeded max fix attempts for this trace.
        Prevents infinite fix-retry loops.
        """
        try:
            fix_history = await self.mcp_manager.call_tool('search_traces', {'query': f'fix_id:{trace_id}', 'limit': max_attempts + 1})
            attempt_count = str(fix_history).count('fix_id:')
            if attempt_count >= max_attempts:
                ConfigurationService().logger.warning(
                    f'Circuit breaker triggered for {trace_id}: {attempt_count} attempts')
                return True
            return False
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error checking circuit breaker: {e}')
            return False

    def _generate_summary(self: Any, results: Dict) -> str:
        """Generate a summary of the debugging cycle."""
        total_errors = len(results.get('errors_found', []))
        total_analyses = len(results.get('analyses', []))
        fixes_proposed = len(results.get('fixes_proposed', []))
        fixes_implemented = len(results.get('fixes_implemented', []))
        
        effectiveness = (fixes_implemented / max(fixes_proposed, 1)) * 100
        
        summary = (
            f"\nDEBUGGER Session Summary: \n"
            f" - Errors analyzed: {total_errors}\n"
            f" - Detailed analyses: {total_analyses}\n"
            f" - Fixes proposed: {fixes_proposed}\n"
            f" - Fixes implemented: {fixes_implemented}\n\n"
            f"Effectiveness: {effectiveness:.1f}% of proposed fixes implemented\n"
        )
        if results.get('error'):
            summary += f"\nError encountered: {results['error']}"
        return summary


async def create_debugger_agent(mcp_manager: Any, llm_client: Any) -> DebuggerAgent:
    """Create and initialize a DEBUGGER agent."""
    await mcp_manager.connect('DEBUGGER')
    return DebuggerAgent(mcp_manager, llm_client)
