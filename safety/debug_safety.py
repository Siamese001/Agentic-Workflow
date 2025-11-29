#!/usr/bin/env python3
"""
Debug the safety layer to identify false positives
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety.safety_layer import (
    check_outbound_content_safety,
    PIIDetector,
    HallucinationDetector,
    InjectionDetector
)

def debug_pii_detector():
    """Debug PII detector"""
    print("=== DEBUGGING PII DETECTOR ===")
    
    detector = PIIDetector()
    
    safe_content = "This is a safe message without personal information"
    print(f"Testing content: '{safe_content}'")
    
    violations = detector.detect_pii(safe_content)
    print(f"PII violations found: {len(violations)}")
    
    for i, violation in enumerate(violations):
        print(f"  {i+1}. Type: {violation.violation_type}")
        print(f"     Severity: {violation.severity}")
        print(f"     Content: '{violation.content}'")
        print(f"     Confidence: {violation.confidence}")
        print(f"     Metadata: {violation.metadata}")
        print()

def debug_hallucination_detector():
    """Debug hallucination detector"""
    print("=== DEBUGGING HALLUCINATION DETECTOR ===")
    
    detector = HallucinationDetector()
    
    safe_content = "This is a safe message without personal information"
    print(f"Testing content: '{safe_content}'")
    
    violations = detector.detect_hallucination(safe_content)
    print(f"Hallucination violations found: {len(violations)}")
    
    for i, violation in enumerate(violations):
        print(f"  {i+1}. Type: {violation.violation_type}")
        print(f"     Severity: {violation.severity}")
        print(f"     Content: '{violation.content}'")
        print(f"     Confidence: {violation.confidence}")
        print(f"     Metadata: {violation.metadata}")
        print()

def debug_injection_detector():
    """Debug injection detector"""
    print("=== DEBUGGING INJECTION DETECTOR ===")
    
    detector = InjectionDetector()
    
    safe_content = "This is a safe message without personal information"
    print(f"Testing content: '{safe_content}'")
    
    violations = detector.detect_injection(safe_content)
    print(f"Injection violations found: {len(violations)}")
    
    for i, violation in enumerate(violations):
        print(f"  {i+1}. Type: {violation.violation_type}")
        print(f"     Severity: {violation.severity}")
        print(f"     Content: '{violation.content}'")
        print(f"     Confidence: {violation.confidence}")
        print(f"     Metadata: {violation.metadata}")
        print()

def debug_safety_layer():
    """Debug the full safety layer"""
    print("=== DEBUGGING FULL SAFETY LAYER ===")
    
    safe_content = "This is a safe message without personal information"
    print(f"Testing content: '{safe_content}'")
    
    result = check_outbound_content_safety(safe_content)
    print(f"Overall result: is_safe={result.is_safe}")
    print(f"Confidence: {result.confidence}")
    print(f"Total violations: {len(result.violations)}")
    
    for i, violation in enumerate(result.violations):
        print(f"  {i+1}. Type: {violation.violation_type}")
        print(f"     Severity: {violation.severity}")
        print(f"     Content: '{violation.content}'")
        print(f"     Confidence: {violation.confidence}")
        print(f"     Metadata: {violation.metadata}")
        print()

def main():
    """Run all debug tests"""
    print("=== SAFETY LAYER DEBUG SUITE ===\n")
    
    debug_pii_detector()
    debug_hallucination_detector()
    debug_injection_detector()
    debug_safety_layer()

if __name__ == "__main__":
    main()
