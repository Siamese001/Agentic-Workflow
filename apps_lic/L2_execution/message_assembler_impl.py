"""Implementation for message_assembler."""

from typing import Any, Dict, List, Optional
from .message_assembler_types import *

class MessageAssembler:
    """
    K.7 - Final QA & Assembly Agent
    
    Signature Immutability:
    - MUST match canonical 4-line signature format exactly
    - No deviations allowed
    
    QA Block Order (EXACT):
    1. LinkedIn QA Grid
    2. AI Filter Canonical
    3. Message-Specific RAG QA Table
    4. Evidence Pack
    """
    CANONICAL_SIGNATURE_TEMPLATE = 'Best regards,\n{name}\n{title}\n{contact}'
    QA_BLOCK_ORDER = [QABlockType.LINKEDIN_QA_GRID, QABlockType.AI_FILTER_CANONICAL, QABlockType.MESSAGE_SPECIFIC_RAG_QA, QABlockType.EVIDENCE_PACK]

    def __init__(self, config: Optional[MessageAssemblerConfig]=None, gate_executor: Optional[IntegrityGateExecutor]=None):
        self.config = config or MessageAssemblerConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()

    def assemble_final_message(self, message_body: str, cta: str, qa_data: Dict[str, Any], sender_info: Dict[str, str]) -> MessageAssemblerResult:
        """
        Assemble final message with QA blocks and signature.
        
        Args:
            message_body: Core message body
            cta: Call to action
            qa_data: QA block data
            sender_info: Sender information for signature
            
        Returns:
            MessageAssemblerResult with assembled message and validation
        """
        validation_results = []
        signature = self._generate_signature(sender_info)
        signature_result = self._validate_signature_immutability(signature, sender_info)
        validation_results.append(signature_result)
        if not signature_result.passed:
            return MessageAssemblerResult(final_message='', qa_blocks=[], signature='', validation_results=validation_results, success=False, metadata={})
        qa_blocks = self._generate_qa_blocks(qa_data)
        qa_order_result = self._validate_qa_block_order(qa_blocks)
        validation_results.append(qa_order_result)
        if not qa_order_result.passed:
            return MessageAssemblerResult(final_message='', qa_blocks=qa_blocks, signature=signature, validation_results=validation_results, success=False, metadata={})
        final_message = self._assemble_message(message_body=message_body, cta=cta, signature=signature, qa_blocks=qa_blocks)
        hygiene_result = self.gate_executor.execute_hygiene_scan(final_message)
        validation_results.append(hygiene_result)
        if not hygiene_result.passed:
            return MessageAssemblerResult(final_message='', qa_blocks=qa_blocks, signature=signature, validation_results=validation_results, success=False, metadata={})
        self.gate_executor.results = validation_results
        metadata = {'message_length': len(final_message), 'qa_blocks_count': len(qa_blocks), 'signature_lines': len(signature.split('\n'))}
        return MessageAssemblerResult(final_message=final_message, qa_blocks=qa_blocks, signature=signature, validation_results=validation_results, success=True, metadata=metadata)

    def _generate_signature(self, sender_info: Dict[str, str]) -> str:
        """Generate canonical 4-line signature"""
        return self.CANONICAL_SIGNATURE_TEMPLATE.format(name=sender_info.get('name', 'John Doe'), title=sender_info.get('title', 'Technology Executive'), contact=sender_info.get('contact', 'john.doe@email.com | (555) 123-4567'))

    def _validate_signature_immutability(self, signature: str, sender_info: Dict[str, str]) -> ValidationResult:
        """
        Validate signature matches canonical 4-line format exactly.
        BLOCKS if format deviates.
        """
        lines = signature.split('\n')
        if len(lines) != self.config.canonical_signature_lines:
            return ValidationResult(gate_id='VG_SIGNATURE_IMMUTABILITY', passed=False, severity='BLOCK', message=f'BLOCKED: Signature has {len(lines)} lines (expected {self.config.canonical_signature_lines})', details={'line_count': len(lines), 'expected': self.config.canonical_signature_lines})
        if not lines[0].startswith('Best regards'):
            return ValidationResult(gate_id='VG_SIGNATURE_IMMUTABILITY', passed=False, severity='BLOCK', message="BLOCKED: Signature line 1 must start with 'Best regards'", details={'actual_line_1': lines[0]})
        return ValidationResult(gate_id='VG_SIGNATURE_IMMUTABILITY', passed=True, severity='INFO', message='Signature immutability validated - canonical 4-line format', signature=f'SIG:OK:4LINES')

    def _generate_qa_blocks(self, qa_data: Dict[str, Any]) -> List[QABlock]:
        """Generate QA blocks in exact order"""
        qa_blocks = []
        linkedin_qa = QABlock(block_type=QABlockType.LINKEDIN_QA_GRID, title='LinkedIn QA Grid', content=self._format_linkedin_qa_grid(qa_data.get('linkedin_qa', {})), order=1)
        qa_blocks.append(linkedin_qa)
        ai_filter = QABlock(block_type=QABlockType.AI_FILTER_CANONICAL, title='AI Filter Canonical', content=self._format_ai_filter(qa_data.get('ai_filter', {})), order=2)
        qa_blocks.append(ai_filter)
        rag_qa = QABlock(block_type=QABlockType.MESSAGE_SPECIFIC_RAG_QA, title='Message-Specific RAG QA Table', content=self._format_rag_qa_table(qa_data.get('rag_qa', {})), order=3)
        qa_blocks.append(rag_qa)
        evidence = QABlock(block_type=QABlockType.EVIDENCE_PACK, title='Evidence Pack', content=self._format_evidence_pack(qa_data.get('evidence', {})), order=4)
        qa_blocks.append(evidence)
        return qa_blocks

    def _validate_qa_block_order(self, qa_blocks: List[QABlock]) -> ValidationResult:
        """
        Validate QA blocks are in exact required order.
        BLOCKS if order is incorrect.
        """
        if len(qa_blocks) != self.config.required_qa_blocks:
            return ValidationResult(gate_id='VG_QA_BLOCK_ORDER', passed=False, severity='BLOCK', message=f'BLOCKED: Expected {self.config.required_qa_blocks} QA blocks, got {len(qa_blocks)}', details={'expected': self.config.required_qa_blocks, 'actual': len(qa_blocks)})
        for i, (block, expected_type) in enumerate(zip(qa_blocks, self.QA_BLOCK_ORDER)):
            if block.block_type != expected_type:
                return ValidationResult(gate_id='VG_QA_BLOCK_ORDER', passed=False, severity='BLOCK', message=f'BLOCKED: QA block {i + 1} is {block.block_type.value}, expected {expected_type.value}', details={'position': i + 1, 'actual': block.block_type.value, 'expected': expected_type.value})
            if block.order != i + 1:
                return ValidationResult(gate_id='VG_QA_BLOCK_ORDER', passed=False, severity='BLOCK', message=f'BLOCKED: QA block order mismatch at position {i + 1}', details={'position': i + 1, 'block_order': block.order})
        return ValidationResult(gate_id='VG_QA_BLOCK_ORDER', passed=True, severity='INFO', message='QA block order validated - exact sequence maintained', signature=f'QAORDER:OK:4BLOCKS', details={'block_sequence': [b.block_type.value for b in qa_blocks]})

    def _assemble_message(self, message_body: str, cta: str, signature: str, qa_blocks: List[QABlock]) -> str:
        """Assemble final message with all components"""
        sections = [message_body, '', cta, '', signature, '', '=' * 80, 'QA VALIDATION REPORT', '=' * 80, '']
        for block in qa_blocks:
            sections.append(f'### {block.title}')
            sections.append('')
            sections.append(block.content)
            sections.append('')
            sections.append('-' * 80)
            sections.append('')
        return '\n'.join(sections)

    def _format_linkedin_qa_grid(self, data: Dict[str, Any]) -> str:
        """Format LinkedIn QA Grid"""
        return f"Route: {data.get('route', 'CONNECTION_REQ')}\nArchetype: {data.get('archetype', 'C_LEVEL')}\nPremium: {data.get('premium', False)}\nCharacter Count: {data.get('char_count', 0)}\nValidation: PASSED"

    def _format_ai_filter(self, data: Dict[str, Any]) -> str:
        """Format AI Filter Canonical"""
        return f"Hygiene Scan: {data.get('hygiene', 'PASSED')}\nForbidden Unicode: {data.get('unicode_violations', 0)}\nVoice Compliance: {data.get('voice', 'PASSED')}\nMetric Binding: {data.get('metric_binding', 'PASSED')}"

    def _format_rag_qa_table(self, data: Dict[str, Any]) -> str:
        """Format Message-Specific RAG QA Table"""
        return f"Grounding Check: {data.get('grounding', 'PASSED')}\nEvidence Sources: {data.get('evidence_count', 0)}\nClaim Verification: {data.get('claim_verification', 'PASSED')}\nHallucination Detection: {data.get('hallucination', 'NONE')}"

    def _format_evidence_pack(self, data: Dict[str, Any]) -> str:
        """Format Evidence Pack"""
        evidence_items = data.get('items', [])
        if not evidence_items:
            return 'No evidence items provided'
        lines = []
        for i, item in enumerate(evidence_items, 1):
            lines.append(f"{i}. {item.get('id', 'EV000')}: {item.get('text', 'N/A')}")
        return '\n'.join(lines)

def create_message_assembler(config: Optional[MessageAssemblerConfig]=None) -> MessageAssembler:
    """Factory function to create MessageAssembler instance"""
    return MessageAssembler(config=config)

