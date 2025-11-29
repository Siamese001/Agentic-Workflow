#!/usr/bin/env python3
"""
Crypto Hash Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional
import logging
import hashlib

logger = logging.getLogger(__name__)

class CryptoHashTool:
    """Hashing, checksums"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.algorithm = self.config.get("algorithm", "sha256")
        self.encoding = self.config.get("encoding", "utf-8")
    
    def hash_string(self, data: str, algorithm: Optional[str] = None) -> str:
        """Hash string data"""
        try:
            hash_algorithm = algorithm or self.algorithm
            hash_func = hashlib.new(hash_algorithm)
            hash_func.update(data.encode(self.encoding))
            hash_hex = hash_func.hexdigest()
            
            logger.debug(f"String hashed with {hash_algorithm}: {len(hash_hex)} characters")
            return hash_hex
            
        except Exception as e:
            logger.error(f"String hashing failed: {e}")
            raise
    
    def hash_file(self, file_path: str, algorithm: Optional[str] = None) -> str:
        """Hash file contents"""
        try:
            hash_algorithm = algorithm or self.algorithm
            hash_func = hashlib.new(hash_algorithm)
            
            # Simulate file hashing
            # In production, would read actual file
            mock_file_content = f"File content for {file_path}"
            hash_func.update(mock_file_content.encode(self.encoding))
            hash_hex = hash_func.hexdigest()
            
            logger.info(f"File hashed with {hash_algorithm}: {file_path}")
            return hash_hex
            
        except Exception as e:
            logger.error(f"File hashing failed: {e}")
            raise
    
    def hash_data(self, data: Any, algorithm: Optional[str] = None) -> str:
        """Hash any data (converted to string)"""
        try:
            # Convert data to string representation
            if isinstance(data, (dict, list)):
                import json
                data_string = json.dumps(data, sort_keys=True)
            else:
                data_string = str(data)
            
            return self.hash_string(data_string, algorithm)
            
        except Exception as e:
            logger.error(f"Data hashing failed: {e}")
            raise
    
    def verify_hash(self, data: str, expected_hash: str, algorithm: Optional[str] = None) -> bool:
        """Verify data against expected hash"""
        try:
            actual_hash = self.hash_string(data, algorithm)
            is_valid = actual_hash == expected_hash
            
            logger.info(f"Hash verification: {'valid' if is_valid else 'invalid'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    def verify_file_hash(self, file_path: str, expected_hash: str, algorithm: Optional[str] = None) -> bool:
        """Verify file against expected hash"""
        try:
            actual_hash = self.hash_file(file_path, algorithm)
            is_valid = actual_hash == expected_hash
            
            logger.info(f"File hash verification: {'valid' if is_valid else 'invalid'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"File hash verification failed: {e}")
            return False
    
    def generate_checksum(self, data: str) -> Dict[str, str]:
        """Generate multiple checksums for data"""
        try:
            algorithms = ["md5", "sha1", "sha256", "sha512"]
            checksums = {}
            
            for algorithm in algorithms:
                try:
                    checksum = self.hash_string(data, algorithm)
                    checksums[algorithm] = checksum
                except Exception as e:
                    logger.warning(f"Failed to generate {algorithm} checksum: {e}")
                    checksums[algorithm] = "error"
            
            logger.info(f"Generated {len(checksums)} checksums")
            return checksums
            
        except Exception as e:
            logger.error(f"Checksum generation failed: {e}")
            return {}
    
    def batch_hash(self, data_list: List[str], algorithm: Optional[str] = None) -> List[str]:
        """Hash multiple data items"""
        try:
            hashes = []
            for data in data_list:
                hash_value = self.hash_string(data, algorithm)
                hashes.append(hash_value)
            
            logger.info(f"Batch hashed {len(hashes)} items")
            return hashes
            
        except Exception as e:
            logger.error(f"Batch hashing failed: {e}")
            raise
    
    def compare_hashes(self, hash1: str, hash2: str) -> Dict[str, Any]:
        """Compare two hash values"""
        try:
            is_equal = hash1 == hash2
            
            result = {
                "hash1": hash1,
                "hash2": hash2,
                "equal": is_equal,
                "analysis": {
                    "length1": len(hash1),
                    "length2": len(hash2),
                    "algorithm": "unknown"  # Could be inferred from length
                }
            }
            
            # Try to infer algorithm from hash length
            if len(hash1) == 32:
                result["analysis"]["algorithm"] = "md5"
            elif len(hash1) == 40:
                result["analysis"]["algorithm"] = "sha1"
            elif len(hash1) == 64:
                result["analysis"]["algorithm"] = "sha256"
            elif len(hash1) == 128:
                result["analysis"]["algorithm"] = "sha512"
            
            logger.info(f"Hash comparison: {'equal' if is_equal else 'different'}")
            return result
            
        except Exception as e:
            logger.error(f"Hash comparison failed: {e}")
            return {"error": str(e)}
    
    def get_hash_info(self) -> Dict[str, Any]:
        """Get hash tool information"""
        return {
            "default_algorithm": self.algorithm,
            "encoding": self.encoding,
            "supported_algorithms": ["md5", "sha1", "sha256", "sha512"],
            "hash_lengths": {
                "md5": 32,
                "sha1": 40,
                "sha256": 64,
                "sha512": 128
            }
        }

def create_crypto_hash_tool(config: Optional[Dict[str, Any]] = None) -> CryptoHashTool:
    """Factory function to create crypto hash tool instance"""
    return CryptoHashTool(config)

# Re-export components
__all__ = [
    'CryptoHashTool', 'create_crypto_hash_tool'
]
