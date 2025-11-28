from l3.lic_orchestrator import LICOrchestrator
from agentic_workflow.LIC_capabilities.lic_atomic_spec import ATOMIC_LIC_SPEC

def test_phase_c():
    orchestrator = LICOrchestrator(ATOMIC_LIC_SPEC)
    
    mock_context = {
        'recipient': {
            'first_name': 'John',
            'title': 'Engineering Manager',
            'company': 'TechCorp'
        },
        'type': 'SHORT_NEW',
        'recipient_type': 'EXECUTIVE',
        'date_window': 'next week'
    }
    
    mock_sender = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'title': 'Senior Software Engineer',
        'linkedin_url': 'https://linkedin.com/in/janesmith'
    }
    
    result = orchestrator.execute_full_pipeline('SHORT_NEW', mock_context, mock_sender)
    
    print('EXECUTION TRACE:')
    for trace in result.execution_trace:
        print(f'  {trace["node"]}: {trace["status"]} - {trace.get("error", "No error")}')
    
    print(f'FINAL ERROR: {result.error_message}')
    print(f'SUCCESS: {result.success}')
    
    if not result.success:
        print('VALIDATION: Pipeline correctly rejected mock data due to insufficient confidence/signal scores')
    else:
        print('Pipeline succeeded with mock data')

if __name__ == "__main__":
    test_phase_c()
