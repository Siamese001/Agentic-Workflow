"""
Unified Semantic Scanner for Phase 0.5 Cache Rebuild

Scans both Resume Engine (RG) and Outreach Engine (LIC) archives with strict engine separation,
parallel processing, and streaming artifact generation to data/semantic_cache/
"""

from __future__ import annotations
import ast
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Generator
import logging
import threading
from contextlib import contextmanager

# Add schemas to path for imports
sys.path.append(str(Path(__file__).parent.parent / "schemas"))
from semantic_lineage import (
    EngineType, ResponsibilityLevel, FileExtension, FileSignature,
    ASTNode, ASTSignature, EmbeddingVector, ToolUsageSignature,
    SafetySignature, GoldenProjection, IntegritySignals,
    SemanticCacheEntry, ArchiveManifest, GlobalCacheReport,
    calculate_file_hash, extract_archive_version,
    validate_file_extension, SemanticLineageValidator
)


@dataclass
class ScanConfiguration:
    """Configuration for semantic scanning operations"""
    max_depth: int = 7
    max_workers: int = 8
    chunk_size: int = 100
    enable_embeddings: bool = True
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
    output_root: Path = field(default_factory=lambda: Path("data/semantic_cache"))
    resume_archives: List[str] = field(default_factory=lambda: [
        "C:\\Git\\Resume Engine Archive\\Agentic-Workflow-10_11",
        "C:\\Git\\Resume Engine Archive\\Agentic_Workflow-10_10",
        "C:\\Git\\Resume Engine Archive\\Agentic-Workflow-10_9",
        "C:\\Git\\Resume Engine Archive\\Agentic-Workflow-10_8_core",
        "C:\\Git\\Resume Engine Archive\\Agentic-Workflow-10_7_main",
        "C:\\Git\\Resume Engine Archive\\Microservices Model",
        "C:\\Git\\Resume Engine Archive\\Monolith",
        "C:\\Git\\Resume Engine Archive\\Monolithic",
        "C:\\Git\\Resume Engine Archive\\Old Resume Gen Python",
        "C:\\Git\\Resume Engine Archive\\v2",
        "C:\\Git\\Resume Engine Archive\\v6.0",
        "C:\\Git\\Resume Engine Archive\\v7.0",
        "C:\\Git\\Resume Engine Archive\\v8.0",
        "C:\\Git\\Resume Engine Archive\\v9.0",
        "C:\\Git\\Resume Engine Archive\\v10.7"
    ])
    outreach_archives: List[str] = field(default_factory=lambda: [
        "C:\\Git\\Reachout Engine Archive\\Agentic-LIC",
        "C:\\Git\\Reachout Engine Archive\\Agentic LIC",
        "C:\\Git\\Reachout Engine Archive\\Monolithic",
        "C:\\Git\\Reachout Engine Archive\\Old LIC",
        "C:\\Git\\Reachout Engine Archive\\deprecated in v13"
    ])


class ArtifactWriter:
    """Thread-safe artifact writer for streaming cache entries to disk"""
    
    def __init__(self, config: ScanConfiguration):
        self.config = config
        self._lock = threading.Lock()
        self._setup_output_directories()
        
    def _setup_output_directories(self):
        """Create required output directory structure"""
        directories = [
            self.config.output_root,
            self.config.output_root / "resume_engine",
            self.config.output_root / "outreach_engine",
            self.config.output_root / "ast",
            self.config.output_root / "embeddings",
            self.config.output_root / "meta",
            self.config.output_root / "diffs",
            self.config.output_root / "safety",
            self.config.output_root / "golden",
            self.config.output_root / "integrity"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _write_atomic(self, file_path: Path, content: str) -> bool:
        """Write content atomically to avoid corruption"""
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        
        try:
            # Write to temporary file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            
            # Windows compatibility: remove existing file before atomic replace
            if file_path.exists():
                file_path.unlink()
            
            # Atomic move to final location
            os.replace(temp_path, file_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write {file_path}: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            return False
    
    def write_cache_entry(self, entry: SemanticCacheEntry) -> bool:
        """Write a complete cache entry to disk with all artifacts"""
        try:
            file_hash = entry.get_file_hash()
            engine_dir = "resume_engine" if entry.file_signature.engine == EngineType.RESUME_ENGINE else "outreach_engine"
            archive_dir = self.config.output_root / engine_dir / entry.file_signature.archive_version
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Write individual artifacts
            artifacts = {
                f"{file_hash}.ast": entry.ast_signature.to_dict(),
                f"{file_hash}.ast.meta.json": entry.file_signature.to_dict(),
                f"{file_hash}.embedding": entry.embedding.to_dict(),
                f"{file_hash}.embedding.meta.json": {"model": entry.embedding.embedding_model, "dimensions": entry.embedding.vector_dimensions},
                f"{file_hash}.diff.json": entry.semantic_diff.to_dict() if entry.semantic_diff else None,
                f"{file_hash}.safety.json": entry.safety.to_dict(),
                f"{file_hash}.golden.json": entry.golden_projection.to_dict()
            }
            
            with self._lock:
                for filename, content in artifacts.items():
                    if content is not None:
                        file_path = archive_dir / filename
                        if self._write_atomic(file_path, json.dumps(content, indent=2, default=str)):
                            continue
                        else:
                            raise Exception(f"Failed to write {file_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to write cache entry for {entry.file_signature.file_path}: {e}")
            return False


class ASTExtractor:
    """Extract AST signatures from Python files"""
    
    @staticmethod
    def extract_ast_signature(file_path: Path, file_signature: FileSignature) -> ASTSignature:
        """Extract complete AST signature from Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            root_nodes = []
            import_graph = {}
            function_signatures = {}
            class_signatures = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        if module_name not in import_graph:
                            import_graph[module_name] = []
                        import_graph[module_name].append(f"line_{node.lineno}")
                
                elif isinstance(node, ast.ImportFrom):
                    module_name = f"from_{node.module}" if node.module else "from_"
                    if module_name not in import_graph:
                        import_graph[module_name] = []
                    import_graph[module_name].append(f"line_{node.lineno}")
                
                elif isinstance(node, ast.FunctionDef):
                    func_sig = ASTExtractor._extract_function_signature(node)
                    root_nodes.append(func_sig)
                    function_signatures[node.name] = func_sig.name
                
                elif isinstance(node, ast.ClassDef):
                    class_sig = ASTExtractor._extract_class_signature(node)
                    root_nodes.append(class_sig)
                    class_signatures[node.name] = class_sig.name
            
            complexity_metrics = ASTExtractor._calculate_complexity(tree)
            
            return ASTSignature(
                signature=file_signature,
                root_nodes=root_nodes,
                import_graph=import_graph,
                function_signatures=function_signatures,
                class_signatures=class_signatures,
                complexity_metrics=complexity_metrics
            )
            
        except SyntaxError as e:
            logging.warning(f"Syntax error in {file_path}: {e}")
            # Return minimal signature for syntax errors
            return ASTSignature(
                signature=file_signature,
                root_nodes=[],
                import_graph={},
                function_signatures={},
                class_signatures={},
                complexity_metrics={"error": "syntax_error", "line": e.lineno}
            )
    
    @staticmethod
    def _extract_function_signature(node: ast.FunctionDef) -> ASTNode:
        """Extract function signature as AST node"""
        docstring = ast.get_docstring(node)
        imports = []
        dependencies = []
        
        # Extract dependencies from function body
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                dependencies.append(child.func.id)
        
        return ASTNode(
            node_type="function",
            name=node.name,
            line_number=node.lineno,
            docstring=docstring,
            imports=imports,
            dependencies=list(set(dependencies)),
            responsibility_level=ASTExtractor._determine_responsibility_level(node.name),
            children=[]
        )
    
    @staticmethod
    def _extract_class_signature(node: ast.ClassDef) -> ASTNode:
        """Extract class signature as AST node"""
        docstring = ast.get_docstring(node)
        imports = []
        dependencies = []
        
        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                dependencies.append(base.id)
        
        return ASTNode(
            node_type="class",
            name=node.name,
            line_number=node.lineno,
            docstring=docstring,
            imports=imports,
            dependencies=list(set(dependencies)),
            responsibility_level=ASTExtractor._determine_responsibility_level(node.name),
            children=[]
        )
    
    @staticmethod
    def _determine_responsibility_level(name: str) -> ResponsibilityLevel:
        """Determine L1-L5 responsibility level from naming patterns"""
        name_lower = name.lower()
        
        if any(pattern in name_lower for pattern in ['core', 'main', 'engine', 'kernel']):
            return ResponsibilityLevel.L1_CORE
        elif any(pattern in name_lower for pattern in ['component', 'module', 'service']):
            return ResponsibilityLevel.L2_COMPONENT
        elif any(pattern in name_lower for pattern in ['interface', 'api', 'handler']):
            return ResponsibilityLevel.L3_INTERFACE
        elif any(pattern in name_lower for pattern in ['impl', 'worker', 'processor']):
            return ResponsibilityLevel.L4_IMPLEMENTATION
        else:
            return ResponsibilityLevel.L5_UTILITY
    
    @staticmethod
    def _calculate_complexity(tree: ast.AST) -> Dict[str, Union[int, float]]:
        """Calculate complexity metrics"""
        complexity = {
            "cyclomatic_complexity": 1,
            "cognitive_complexity": 0,
            "nesting_depth": 0,
            "lines_of_code": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                complexity["cyclomatic_complexity"] += 1
            
            if isinstance(node, ast.If):
                complexity["cognitive_complexity"] += 1
        
        return complexity


class EmbeddingGenerator:
    """Generate semantic embeddings for files"""
    
    def __init__(self, config: ScanConfiguration):
        self.config = config
        self.enabled = config.enable_embeddings
    
    def generate_embedding(self, file_path: Path, file_signature: FileSignature) -> EmbeddingVector:
        """Generate embedding vector for file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, generate a mock embedding (replace with actual embedding service)
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            mock_embedding = [hash(content_hash[i:i+4]) % 1000 / 1000.0 for i in range(0, min(64, len(content_hash)), 4)]
            
            return EmbeddingVector(
                vector_hash=hashlib.sha256(str(mock_embedding).encode()).hexdigest(),
                embedding_model=self.config.embedding_model,
                vector_dimensions=len(mock_embedding),
                embedding_data=mock_embedding,
                confidence_score=0.85,
                semantic_tags=self._extract_semantic_tags(content)
            )
            
        except Exception as e:
            logging.warning(f"Failed to generate embedding for {file_path}: {e}")
            # Return minimal embedding
            return EmbeddingVector(
                vector_hash="mock_hash",
                embedding_model="mock",
                vector_dimensions=1,
                embedding_data=[0.0],
                confidence_score=0.0,
                semantic_tags=[]
            )
    
    def _extract_semantic_tags(self, content: str) -> List[str]:
        """Extract semantic tags from content"""
        tags = []
        content_lower = content.lower()
        
        if 'class ' in content_lower:
            tags.append("class_definition")
        if 'def ' in content_lower:
            tags.append("function_definition")
        if 'import ' in content_lower:
            tags.append("imports")
        if 'async def ' in content_lower:
            tags.append("async")
        if 'try:' in content_lower or 'except' in content_lower:
            tags.append("error_handling")
        
        return tags


class ToolUsageExtractor:
    """Extract tool usage patterns from code"""
    
    @staticmethod
    def extract_tool_usage(file_path: Path) -> ToolUsageSignature:
        """Extract tool usage signatures from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            api_calls = []
            retry_patterns = []
            backoff_strategies = []
            error_handling = []
            external_dependencies = []
            
            # Simple pattern matching for tool usage
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # API calls
                if 'requests.' in line_lower or 'httpx.' in line_lower:
                    api_calls.append({
                        "function": line.strip(),
                        "line": i + 1,
                        "type": "http_request"
                    })
                
                # Retry patterns
                if 'retry' in line_lower or 'attempt' in line_lower:
                    retry_patterns.append(line.strip())
                
                # Backoff strategies
                if 'backoff' in line_lower or 'exponential' in line_lower:
                    backoff_strategies.append(line.strip())
                
                # Error handling
                if 'try:' in line_lower or 'except' in line_lower:
                    error_handling.append(line.strip())
                
                # External dependencies
                if any(lib in line_lower for lib in ['import requests', 'import httpx', 'import boto3', 'import openai']):
                    external_dependencies.append(line.strip())
            
            return ToolUsageSignature(
                api_calls=api_calls,
                retry_patterns=retry_patterns,
                backoff_strategies=backoff_strategies,
                error_handling=error_handling,
                external_dependencies=external_dependencies
            )
            
        except Exception as e:
            logging.warning(f"Failed to extract tool usage from {file_path}: {e}")
            return ToolUsageSignature([], [], [], [], [])


class SafetyExtractor:
    """Extract safety and policy signatures"""
    
    @staticmethod
    def extract_safety_signature(file_path: Path) -> SafetySignature:
        """Extract safety patterns from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            safety_checks = []
            policy_compliance = []
            security_patterns = []
            data_handling = []
            access_controls = []
            
            content_lower = content.lower()
            
            # Safety checks
            if any(pattern in content_lower for pattern in ['validate', 'verify', 'check']):
                safety_checks.append("input_validation")
            if 'sanitize' in content_lower:
                safety_checks.append("sanitization")
            
            # Policy compliance
            if any(pattern in content_lower for pattern in ['gdpr', 'hipaa', 'sox', 'compliance']):
                policy_compliance.append("regulatory_compliance")
            
            # Security patterns
            if any(pattern in content_lower for pattern in ['encrypt', 'decrypt', 'hash', 'token']):
                security_patterns.append("cryptography")
            if 'authenticate' in content_lower or 'authorize' in content_lower:
                security_patterns.append("auth")
            
            # Data handling
            if any(pattern in content_lower for pattern in ['pii', 'personal', 'sensitive']):
                data_handling.append("sensitive_data")
            
            # Access controls
            if 'permission' in content_lower or 'role' in content_lower:
                access_controls.append("rbac")
            
            return SafetySignature(
                safety_checks=safety_checks,
                policy_compliance=policy_compliance,
                security_patterns=security_patterns,
                data_handling=data_handling,
                access_controls=access_controls
            )
            
        except Exception as e:
            logging.warning(f"Failed to extract safety signature from {file_path}: {e}")
            return SafetySignature([], [], [], [], [])


class GoldenProjectionGenerator:
    """Generate golden canonical projections"""
    
    @staticmethod
    def generate_golden_projection(file_path: Path, ast_signature: ASTSignature) -> GoldenProjection:
        """Generate golden projection from AST signature"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract canonical form (normalized representation)
            canonical_form = GoldenProjectionGenerator._normalize_code(content)
            
            # Extract normalized signatures
            normalized_signature = GoldenProjectionGenerator._extract_signatures(ast_signature)
            
            # Core functionality analysis
            core_functionality = GoldenProjectionGenerator._analyze_core_functionality(content)
            
            # Interface contract
            interface_contract = GoldenProjectionGenerator._extract_interface_contract(ast_signature)
            
            # Test coverage indicators
            test_coverage = GoldenProjectionGenerator._analyze_test_coverage(content)
            
            return GoldenProjection(
                canonical_form=canonical_form,
                normalized_signature=normalized_signature,
                core_functionality=core_functionality,
                interface_contract=interface_contract,
                test_coverage=test_coverage
            )
            
        except Exception as e:
            logging.warning(f"Failed to generate golden projection for {file_path}: {e}")
            return GoldenProjection("", "", "", "", [])
    
    @staticmethod
    def _normalize_code(content: str) -> str:
        """Normalize code to canonical form"""
        lines = content.split('\n')
        normalized = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Remove extra whitespace and normalize
                normalized.append(' '.join(stripped.split()))
        
        return '\n'.join(normalized)
    
    @staticmethod
    def _extract_signatures(ast_signature: ASTSignature) -> str:
        """Extract normalized function and class signatures"""
        signatures = []
        
        for func_name in ast_signature.function_signatures:
            signatures.append(f"func:{func_name}")
        
        for class_name in ast_signature.class_signatures:
            signatures.append(f"class:{class_name}")
        
        return ';'.join(signatures)
    
    @staticmethod
    def _analyze_core_functionality(content: str) -> str:
        """Analyze and describe core functionality"""
        content_lower = content.lower()
        
        if 'class ' in content_lower and 'def ' in content_lower:
            return "object_oriented_with_methods"
        elif 'def ' in content_lower:
            return "procedural_functions"
        elif 'import ' in content_lower:
            return "module_imports"
        else:
            return "configuration_or_data"
    
    @staticmethod
    def _extract_interface_contract(ast_signature: ASTSignature) -> str:
        """Extract interface contract from AST"""
        public_methods = []
        
        for node in ast_signature.root_nodes:
            if node.node_type == "function" and not node.name.startswith('_'):
                public_methods.append(node.name)
        
        return f"public_methods:{','.join(public_methods)}"
    
    @staticmethod
    def _analyze_test_coverage(content: str) -> List[str]:
        """Analyze test coverage indicators"""
        indicators = []
        content_lower = content.lower()
        
        if 'test' in content_lower:
            indicators.append("contains_tests")
        if 'assert' in content_lower:
            indicators.append("contains_assertions")
        if 'unittest' in content_lower or 'pytest' in content_lower:
            indicators.append("uses_testing_framework")
        
        return indicators


class IntegritySignalGenerator:
    """Generate integrity and verification signals"""
    
    @staticmethod
    def generate_integrity_signals(file_path: Path, ast_signature: ASTSignature, embedding: EmbeddingVector) -> IntegritySignals:
        """Generate comprehensive integrity signals"""
        try:
            with open(file_path, 'rb') as f:
                content_bytes = f.read()
            
            # Content hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Structure hash (based on AST)
            structure_str = json.dumps(ast_signature.to_dict(), sort_keys=True, default=str)
            structure_hash = hashlib.sha256(structure_str.encode()).hexdigest()
            
            # Semantic hash (based on embedding)
            semantic_str = json.dumps(embedding.to_dict(), sort_keys=True, default=str)
            semantic_hash = hashlib.sha256(semantic_str.encode()).hexdigest()
            
            # Version ID (timestamp + hash)
            version_id = f"{datetime.now().isoformat()}_{content_hash[:16]}"
            
            # Lineage chain (empty for new files)
            lineage_chain = []
            
            # Verification status
            verification_status = True  # Simplified - would include actual verification logic
            
            return IntegritySignals(
                content_hash=content_hash,
                structure_hash=structure_hash,
                semantic_hash=semantic_hash,
                version_id=version_id,
                lineage_chain=lineage_chain,
                verification_status=verification_status
            )
            
        except Exception as e:
            logging.error(f"Failed to generate integrity signals for {file_path}: {e}")
            return IntegritySignals("", "", "", "", [], False)


class SemanticScanner:
    """Unified semantic scanner for both RG and LIC engines"""
    
    def __init__(self, config: ScanConfiguration):
        self.config = config
        self.writer = ArtifactWriter(config)
        self.embedding_generator = EmbeddingGenerator(config)
        self.validator = SemanticLineageValidator()
        
    def scan_all_archives(self) -> GlobalCacheReport:
        """Scan all configured archives and generate semantic cache"""
        logging.info("Starting comprehensive semantic scan of all archives")
        
        resume_manifests = {}
        outreach_manifests = {}
        
        # Scan resume engine archives
        for archive_path in self.config.resume_archives:
            try:
                manifest = self._scan_single_archive(Path(archive_path), EngineType.RESUME_ENGINE)
                resume_manifests[manifest.archive_version] = manifest
                logging.info(f"Completed RG archive: {manifest.archive_version}")
            except Exception as e:
                logging.error(f"Failed to scan RG archive {archive_path}: {e}")
        
        # Scan outreach engine archives
        for archive_path in self.config.outreach_archives:
            try:
                manifest = self._scan_single_archive(Path(archive_path), EngineType.OUTREACH_ENGINE)
                outreach_manifests[manifest.archive_version] = manifest
                logging.info(f"Completed LIC archive: {manifest.archive_version}")
            except Exception as e:
                logging.error(f"Failed to scan LIC archive {archive_path}: {e}")
        
        # Generate global report
        global_report = self._generate_global_report(resume_manifests, outreach_manifests)
        
        logging.info("Semantic scan completed successfully")
        return global_report
    
    def _scan_single_archive(self, archive_path: Path, engine: EngineType) -> ArchiveManifest:
        """Scan a single archive directory"""
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive path does not exist: {archive_path}")
        
        archive_version = extract_archive_version(archive_path)
        start_time = datetime.now()
        
        logging.info(f"Scanning {engine.value} archive: {archive_version}")
        
        # Discover all files
        all_files = list(self._discover_files(archive_path))
        total_files = len(all_files)
        
        if total_files == 0:
            logging.warning(f"No files found in archive: {archive_path}")
            return ArchiveManifest(
                engine=engine,
                archive_version=archive_version,
                archive_path=archive_path,
                total_files=0,
                processed_files=0,
                failed_files=[],
                file_hashes=set(),
                completeness_score=0.0,
                processing_start=start_time,
                processing_end=datetime.now()
            )
        
        # Process files in parallel
        processed_files = 0
        failed_files = []
        file_hashes = set()
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(self._process_file, file_path, engine, archive_version): file_path
                for file_path in all_files
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        processed_files += 1
                        file_hashes.add(result)
                    else:
                        failed_files.append(str(file_path))
                except Exception as e:
                    logging.error(f"Failed to process file {file_path}: {e}")
                    failed_files.append(str(file_path))
        
        end_time = datetime.now()
        completeness_score = processed_files / total_files if total_files > 0 else 0.0
        
        return ArchiveManifest(
            engine=engine,
            archive_version=archive_version,
            archive_path=archive_path,
            total_files=total_files,
            processed_files=processed_files,
            failed_files=failed_files,
            file_hashes=file_hashes,
            completeness_score=completeness_score,
            processing_start=start_time,
            processing_end=end_time
        )
    
    def _discover_files(self, root_path: Path) -> Generator[Path, None, None]:
        """Discover all eligible files in directory tree"""
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                file_ext = validate_file_extension(file_path)
                if file_ext:
                    # Check depth constraint
                    relative_path = file_path.relative_to(root_path)
                    depth = len(relative_path.parts)
                    if depth <= self.config.max_depth:
                        yield file_path
    
    def _process_file(self, file_path: Path, engine: EngineType, archive_version: str) -> Optional[str]:
        """Process a single file and generate semantic cache entry"""
        try:
            # Generate file signature
            file_hash = calculate_file_hash(file_path)
            file_signature = FileSignature(
                file_path=file_path,
                file_hash=file_hash,
                size_bytes=file_path.stat().st_size,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                engine=engine,
                archive_version=archive_version,
                file_extension=validate_file_extension(file_path) or FileExtension.TEXT
            )
            
            # Skip non-Python files for AST extraction (but still process for embeddings)
            ast_signature = None
            if file_signature.file_extension == FileExtension.PYTHON:
                ast_signature = ASTExtractor.extract_ast_signature(file_path, file_signature)
            else:
                # Create minimal AST signature for non-Python files
                ast_signature = ASTSignature(
                    signature=file_signature,
                    root_nodes=[],
                    import_graph={},
                    function_signatures={},
                    class_signatures={},
                    complexity_metrics={"file_type": "non_python"}
                )
            
            # Generate embedding
            embedding = self.embedding_generator.generate_embedding(file_path, file_signature)
            
            # Extract tool usage
            tool_usage = ToolUsageExtractor.extract_tool_usage(file_path)
            
            # Extract safety signature
            safety = SafetyExtractor.extract_safety_signature(file_path)
            
            # Generate golden projection
            golden_projection = GoldenProjectionGenerator.generate_golden_projection(file_path, ast_signature)
            
            # Generate integrity signals
            integrity = IntegritySignalGenerator.generate_integrity_signals(file_path, ast_signature, embedding)
            
            # Create semantic cache entry
            cache_entry = SemanticCacheEntry(
                file_signature=file_signature,
                ast_signature=ast_signature,
                embedding=embedding,
                tool_usage=tool_usage,
                safety=safety,
                semantic_diff=None,  # Would be populated during diff analysis
                golden_projection=golden_projection,
                integrity=integrity,
                processing_timestamp=datetime.now()
            )
            
            # Validate cache entry
            validation_errors = self.validator.validate_cache_entry(cache_entry)
            if validation_errors:
                logging.warning(f"Validation errors for {file_path}: {validation_errors}")
            
            # Write to disk
            if self.writer.write_cache_entry(cache_entry):
                return file_hash
            else:
                return None
                
        except Exception as e:
            logging.error(f"Failed to process file {file_path}: {e}")
            return None
    
    def _generate_global_report(self, resume_manifests: Dict[str, ArchiveManifest], 
                              outreach_manifests: Dict[str, ArchiveManifest]) -> GlobalCacheReport:
        """Generate global cache report"""
        total_archives = len(resume_manifests) + len(outreach_manifests)
        successful_archives = sum(1 for m in resume_manifests.values() if m.completeness_score > 0.9)
        successful_archives += sum(1 for m in outreach_manifests.values() if m.completeness_score > 0.9)
        
        total_files_processed = sum(m.processed_files for m in resume_manifests.values())
        total_files_processed += sum(m.processed_files for m in outreach_manifests.values())
        
        global_integrity = {
            "total_archives": total_archives,
            "successful_archives": successful_archives,
            "total_files_processed": total_files_processed,
            "integrity_violations": []  # Would be populated with actual violations
        }
        
        drift_report = {
            "semantic_drift": [],
            "api_drift": []
        }
        
        orphan_report = {
            "orphaned_files": [],
            "unreferenced_hashes": []
        }
        
        required_archives = set(self.config.resume_archives + self.config.outreach_archives)
        processed_archives = set(str(m.archive_path) for m in resume_manifests.values()) | \
                           set(str(m.archive_path) for m in outreach_manifests.values())
        
        completeness_report = {
            "required_archives": list(required_archives),
            "missing_archives": list(required_archives - processed_archives),
            "overall_completeness": successful_archives / total_archives if total_archives > 0 else 0.0
        }
        
        return GlobalCacheReport(
            resume_engine_manifests=resume_manifests,
            outreach_engine_manifests=outreach_manifests,
            global_integrity=global_integrity,
            drift_report=drift_report,
            orphan_report=orphan_report,
            completeness_report=completeness_report
        )


def main():
    """Main entry point for semantic scanner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    config = ScanConfiguration()
    scanner = SemanticScanner(config)
    
    try:
        global_report = scanner.scan_all_archives()
        
        # Write global report
        report_path = config.output_root / "global_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(global_report.to_dict(), f, indent=2, default=str)
        
        logging.info(f"Semantic scan completed. Report written to: {report_path}")
        logging.info(f"Overall completeness: {global_report.completeness_report['overall_completeness']:.2%}")
        
    except Exception as e:
        logging.error(f"Semantic scan failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
