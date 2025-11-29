#!/usr/bin/env python3
"""
Injection Detector
Section 8: Safety Layer - Injection attack detection and prevention
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class InjectionDetector:
    """Injection attack detection and prevention for agentic systems"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sensitivity_level = self.config.get("sensitivity_level", "medium")
        self.block_threshold = self.config.get("block_threshold", 0.8)
        self.warn_threshold = self.config.get("warn_threshold", 0.6)
        
        # Injection patterns
        self.injection_patterns = self._load_injection_patterns()
        self.suspicious_keywords = self._load_suspicious_keywords()
    
    def detect_injection(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect potential injection attacks in input text"""
        try:
            detection_result = {
                "is_safe": True,
                "risk_score": 0.0,
                "detections": [],
                "recommendations": []
            }
            
            # Check for SQL injection patterns
            sql_result = self._detect_sql_injection(input_text)
            if sql_result["detected"]:
                detection_result["detections"].append(sql_result)
                detection_result["risk_score"] += sql_result["confidence"]
            
            # Check for command injection patterns
            cmd_result = self._detect_command_injection(input_text)
            if cmd_result["detected"]:
                detection_result["detections"].append(cmd_result)
                detection_result["risk_score"] += cmd_result["confidence"]
            
            # Check for XSS injection patterns
            xss_result = self._detect_xss_injection(input_text)
            if xss_result["detected"]:
                detection_result["detections"].append(xss_result)
                detection_result["risk_score"] += xss_result["confidence"]
            
            # Check for prompt injection patterns
            prompt_result = self._detect_prompt_injection(input_text)
            if prompt_result["detected"]:
                detection_result["detections"].append(prompt_result)
                detection_result["risk_score"] += prompt_result["confidence"]
            
            # Check for suspicious keywords
            keyword_result = self._detect_suspicious_keywords(input_text)
            if keyword_result["detected"]:
                detection_result["detections"].append(keyword_result)
                detection_result["risk_score"] += keyword_result["confidence"]
            
            # Normalize risk score
            detection_result["risk_score"] = min(1.0, detection_result["risk_score"])
            
            # Determine safety based on thresholds
            if detection_result["risk_score"] >= self.block_threshold:
                detection_result["is_safe"] = False
                detection_result["action"] = "block"
            elif detection_result["risk_score"] >= self.warn_threshold:
                detection_result["action"] = "warn"
            else:
                detection_result["action"] = "allow"
            
            # Generate recommendations
            detection_result["recommendations"] = self._generate_recommendations(detection_result)
            
            logger.info(f"Injection detection: risk_score={detection_result['risk_score']:.2f}, action={detection_result['action']}")
            return detection_result
            
        except Exception as e:
            logger.error(f"Injection detection failed: {e}")
            return {"is_safe": False, "error": str(e), "risk_score": 1.0}
    
    def sanitize_input(self, input_text: str) -> Dict[str, Any]:
        """Sanitize input to remove potential injection vectors"""
        try:
            sanitized = input_text
            
            # Remove or escape dangerous characters
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            
            # Remove suspicious keywords
            for keyword in self.suspicious_keywords:
                sanitized = re.sub(rf'\b{re.escape(keyword)}\b', '', sanitized, flags=re.IGNORECASE)
            
            # Normalize whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            
            result = {
                "original": input_text,
                "sanitized": sanitized,
                "changes_made": len(input_text) - len(sanitized),
                "is_safe": self.detect_injection(sanitized)["is_safe"]
            }
            
            logger.debug(f"Input sanitized: {result['changes_made']} characters removed")
            return result
            
        except Exception as e:
            logger.error(f"Input sanitization failed: {e}")
            return {"original": input_text, "sanitized": "", "error": str(e)}
    
    def validate_query(self, query: str, allowed_operations: List[str]) -> Dict[str, Any]:
        """Validate database query against allowed operations"""
        try:
            validation_result = {
                "is_valid": True,
                "violations": [],
                "sanitized_query": query
            }
            
            # Check for allowed operations
            query_upper = query.upper()
            for op in ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER"]:
                if op in query_upper and op not in [allowed_op.upper() for allowed_op in allowed_operations]:
                    validation_result["is_valid"] = False
                    validation_result["violations"].append(f"Operation '{op}' not allowed")
            
            # Check for injection patterns
            injection_result = self.detect_injection(query)
            if not injection_result["is_safe"]:
                validation_result["is_valid"] = False
                validation_result["violations"].extend([d["type"] for d in injection_result["detections"]])
            
            logger.info(f"Query validation: {'valid' if validation_result['is_valid'] else 'invalid'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            return {"is_valid": False, "error": str(e)}
    
    def _detect_sql_injection(self, text: str) -> Dict[str, Any]:
        """Detect SQL injection patterns"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC)\b)",
            r"(\b(UNION|JOIN|WHERE|HAVING|GROUP BY|ORDER BY)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|\/\*|\*\/)",
            r"(\b(xp_|sp_)\w+)",
            r"(\b(INFORMATION_SCHEMA|SYS|MASTER|MSDB)\b)"
        ]
        
        detections = []
        confidence = 0.0
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    "type": "sql_injection",
                    "pattern": pattern,
                    "match": match.group(),
                    "position": match.span()
                })
                confidence += 0.2
        
        return {
            "detected": len(detections) > 0,
            "confidence": min(1.0, confidence),
            "detections": detections
        }
    
    def _detect_command_injection(self, text: str) -> Dict[str, Any]:
        """Detect command injection patterns"""
        cmd_patterns = [
            r"(\&\&|\|\||;|`|\$\(|\$\{\{)",
            r"(\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b)",
            r"(\b(curl|wget|nc|telnet|ssh|ftp)\b)",
            r"(\b(rm|mv|cp|chmod|chown|kill)\b)",
            r"(\b(python|perl|ruby|bash|sh|cmd|powershell)\b)",
            r"(\/etc\/passwd|\/etc\/shadow|\/proc\/|\/sys\/)"
        ]
        
        detections = []
        confidence = 0.0
        
        for pattern in cmd_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    "type": "command_injection",
                    "pattern": pattern,
                    "match": match.group(),
                    "position": match.span()
                })
                confidence += 0.25
        
        return {
            "detected": len(detections) > 0,
            "confidence": min(1.0, confidence),
            "detections": detections
        }
    
    def _detect_xss_injection(self, text: str) -> Dict[str, Any]:
        """Detect XSS injection patterns"""
        xss_patterns = [
            r"(<script[^>]*>.*?</script>)",
            r"(<iframe[^>]*>.*?</iframe>)",
            r"(javascript:)",
            r"(on\w+\s*=\s*['\"][^'\"]*['\"])",
            r"(<object[^>]*>.*?</object>)",
            r"(<embed[^>]*>.*?</embed>)",
            r"(<link[^>]*>)",
            r"(<meta[^>]*>)"
        ]
        
        detections = []
        confidence = 0.0
        
        for pattern in xss_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    "type": "xss_injection",
                    "pattern": pattern,
                    "match": match.group(),
                    "position": match.span()
                })
                confidence += 0.3
        
        return {
            "detected": len(detections) > 0,
            "confidence": min(1.0, confidence),
            "detections": detections
        }
    
    def _detect_prompt_injection(self, text: str) -> Dict[str, Any]:
        """Detect prompt injection patterns"""
        prompt_patterns = [
            r"(\b(ignore|forget|disregard|skip)\s+(previous|above|earlier)\s+(instructions|prompts|commands))",
            r"(\b(system|developer|admin)\s+(mode|override|privileges))",
            r"(\b(new\s+role|act\s+as|pretend\s+you\s+are)\b)",
            r"(\b(jailbreak|escape|override)\b)",
            r"(\b(instead|rather|alternatively)\s+(do|perform|execute))",
            r"(\b(change\s+the\s+(rules|instructions|behavior|personality))",
            r"(\b(you\s+are\s+now|from\s+now\s+on)\b)"
        ]
        
        detections = []
        confidence = 0.0
        
        for pattern in prompt_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    "type": "prompt_injection",
                    "pattern": pattern,
                    "match": match.group(),
                    "position": match.span()
                })
                confidence += 0.15
        
        return {
            "detected": len(detections) > 0,
            "confidence": min(1.0, confidence),
            "detections": detections
        }
    
    def _detect_suspicious_keywords(self, text: str) -> Dict[str, Any]:
        """Detect suspicious keywords"""
        found_keywords = []
        confidence = 0.0
        
        for keyword in self.suspicious_keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                found_keywords.append(keyword)
                confidence += 0.1
        
        return {
            "detected": len(found_keywords) > 0,
            "confidence": min(1.0, confidence),
            "keywords": found_keywords
        }
    
    def _generate_recommendations(self, detection_result: Dict[str, Any]) -> List[str]:
        """Generate safety recommendations based on detection results"""
        recommendations = []
        
        if detection_result["risk_score"] >= self.block_threshold:
            recommendations.append("Input blocked due to high injection risk")
            recommendations.append("Review and sanitize input before resubmission")
        elif detection_result["risk_score"] >= self.warn_threshold:
            recommendations.append("Input flagged for potential injection")
            recommendations.append("Consider using parameterized queries or input validation")
        
        # Specific recommendations based on detection types
        for detection in detection_result["detections"]:
            if "sql" in detection.get("type", "").lower():
                recommendations.append("Use parameterized queries to prevent SQL injection")
            elif "command" in detection.get("type", "").lower():
                recommendations.append("Avoid executing user input as system commands")
            elif "xss" in detection.get("type", "").lower():
                recommendations.append("Sanitize HTML output and use Content Security Policy")
            elif "prompt" in detection.get("type", "").lower():
                recommendations.append("Implement prompt validation and filtering")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _load_injection_patterns(self) -> Dict[str, List[str]]:
        """Load injection patterns by category"""
        return {
            "sql": [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC)\b)",
                r"(--|#|\/\*|\*\/)"
            ],
            "command": [
                r"(\&\&|\|\||;|`|\$\()",
                r"(\b(cat|ls|pwd|whoami)\b)"
            ],
            "xss": [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript:)"
            ],
            "prompt": [
                r"(\b(ignore|forget|disregard)\s+(previous|above))",
                r"(\b(system|developer|admin)\s+(mode|override))"
            ]
        }
    
    def _load_suspicious_keywords(self) -> List[str]:
        """Load list of suspicious keywords"""
        return [
            "password", "secret", "token", "key", "admin", "root",
            "privilege", "escalate", "bypass", "override", "debug",
            "execute", "eval", "system", "shell", "cmd", "powershell"
        ]
    
    def get_detector_info(self) -> Dict[str, Any]:
        """Get injection detector information"""
        return {
            "sensitivity_level": self.sensitivity_level,
            "block_threshold": self.block_threshold,
            "warn_threshold": self.warn_threshold,
            "supported_injection_types": ["sql", "command", "xss", "prompt"],
            "features": ["detection", "sanitization", "query_validation"]
        }

def create_injection_detector(config: Optional[Dict[str, Any]] = None) -> InjectionDetector:
    """Factory function to create injection detector instance"""
    return InjectionDetector(config)

# Re-export components
__all__ = [
    'InjectionDetector', 'create_injection_detector'
]





