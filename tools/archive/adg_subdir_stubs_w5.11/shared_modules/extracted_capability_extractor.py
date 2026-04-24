"""
Extracted capability module: extracted_capability_extractor
Source: tools/adg/capability_extractor.py
Extracted: 2026-03-27T06:52:44.268287
"""


class CapabilityExtractor:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.adg_dir = self.repo_root / "tools" / "adg"
        self.estimator = ContextWindowEstimator()

        # Ensure target directories exist
        self.shared_modules_dir = self.adg_dir / "shared_modules"
        self.shared_modules_dir.mkdir(parents=True, exist_ok=True)

        # Extraction log
        self.extraction_log = []

        # Capability patterns to look for
        self.capability_patterns = {
            "file_operations": ["open", "read", "write", "file_exists", "mkdir", "rmdir"],
            "string_processing": ["split", "join", "replace", "strip", "lower", "upper"],
            "json_processing": ["json_load", "json_dump", "parse_json", "serialize_json"],
            "git_operations": ["git_add", "git_commit", "git_push", "git_status"],
            "path_operations": ["path_join", "path_exists", "get_extension", "get_basename"],
            "validation": ["validate", "check", "verify", "ensure"],
            "error_handling": ["handle_error", "catch_exception", "log_error", "raise_error"],
        }

    def load_manifest(self, manifest_path: str) -> List[Dict[str, Any]]:
        """Load the repo hygiene manifest."""
        with open(manifest_path) as f:
            data = json.load(f)
        return data["files"]

    def get_legitimate_python_files(self, manifest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract legitimate Python files for analysis."""
        python_files = [
            item
            for item in manifest
            if (
                item["classification"] == "legitimate"
                and item["path"].endswith(".py")
                and (Path(item["path"]).exists())
            )
        ]
        logging.info(f"Found {len(python_files)} legitimate Python files to analyze")
        return python_files

    def analyze_file_capabilities(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for reusable capabilities."""
        try:
            # Convert to absolute path and check if it's within repo
            abs_path = file_path.resolve()
            try:
                rel_path = abs_path.relative_to(self.repo_root)
            except ValueError:
                logging.warning(f"File {file_path} is outside repository root")
                return None

            with open(abs_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            capabilities = {
                "file_path": str(rel_path),
                "functions": [],
                "classes": [],
                "imports": [],
                "capability_patterns": defaultdict(list),
                "reusable_score": 0,
                "size_lines": len(content.splitlines()),
                "size_bytes": len(content),
            }

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_private": node.name.startswith("_"),
                        "calls": self._extract_function_calls(node),
                    }
                    capabilities["functions"].append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node),
                        "is_private": node.name.startswith("_"),
                    }
                    capabilities["classes"].append(class_info)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            capabilities["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            capabilities["imports"].append(f"{module}.{alias.name}")

            # Score reusability
            capabilities["reusable_score"] = self._calculate_reusability_score(capabilities)

            return capabilities

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logging.warning(f"Failed to analyze {file_path}: {e}")
            return None

    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls from a function definition."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls

    def _calculate_reusability_score(self, capabilities: Dict[str, Any]) -> int:
        """Calculate a reusability score for the file."""
        score = 0

        # Points for public functions
        public_funcs = [f for f in capabilities["functions"] if not f["is_private"]]
        score += len(public_funcs) * 2

        # Points for public classes
        public_classes = [c for c in capabilities["classes"] if not c["is_private"]]
        score += len(public_classes) * 3

        # Points for utility patterns
        for func in capabilities["functions"]:
            for pattern, keywords in self.capability_patterns.items():
                if any(keyword in func["name"].lower() for keyword in keywords):
                    score += 1
                    capabilities["capability_patterns"][pattern].append(func["name"])

        # Deduct points for very large files (harder to reuse)
        if capabilities["size_lines"] > 500:
            score -= 2
        elif capabilities["size_lines"] > 200:
            score -= 1

        return max(0, score)

    def identify_extraction_candidates(self, file_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify the best candidates for capability extraction."""
        # Sort by reusability score
        candidates = sorted(file_analyses, key=lambda x: x["reusable_score"], reverse=True)

        # Filter for candidates with reasonable scores
        high_score_candidates = [c for c in candidates if c["reusable_score"] >= 3]

        logging.info(f"Identified {len(high_score_candidates)} high-score extraction candidates")
        return high_score_candidates[:20]  # Top 20 as per plan

    def extract_capability(self, candidate: Dict[str, Any]) -> bool:
        """Extract a capability and promote it to shared modules."""
        try:
            source_path = self.repo_root / candidate["file_path"]

            # Determine target module name based on primary capability
            primary_capability = self._determine_primary_capability(candidate)
            target_module = self.shared_modules_dir / f"{primary_capability}.py"

            # Extract reusable code
            extracted_code = self._extract_reusable_code(source_path, candidate)

            if not extracted_code:
                logging.warning(f"No reusable code found in {candidate['file_path']}")
                return False

            # Write to shared module
            with open(target_module, "w", encoding="utf-8") as f:
                f.write(f'"""\nExtracted capability module: {primary_capability}\n')
                f.write(f"Source: {candidate['file_path']}\n")
                f.write(f"Extracted: {datetime.now().isoformat()}\n")
                f.write('"""\n\n')
                f.write(extracted_code)

            # Log the extraction
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_file": candidate["file_path"],
                "target_module": str(target_module.relative_to(self.repo_root)),
                "capability": primary_capability,
                "reusable_score": candidate["reusable_score"],
                "functions_extracted": len(
                    [f for f in candidate.get("functions", []) if not f.get("is_private", True)]
                ),
                "classes_extracted": len(
                    [c for c in candidate.get("classes", []) if not c.get("is_private", True)]
                ),
                "status": "extracted",
            }
            self.extraction_log.append(log_entry)

            logging.info(f"Extracted {primary_capability} from {candidate['file_path']}")
            return True

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logging.error(f"Failed to extract capability from {candidate['file_path']}: {e}")
            return False

    def _determine_primary_capability(self, candidate: Dict[str, Any]) -> str:
        """Determine the primary capability type for a candidate."""
        capability_patterns = candidate.get("capability_patterns", {})
        pattern_counts = {pattern: len(funcs) for pattern, funcs in capability_patterns.items()}

        if pattern_counts:
            return max(pattern_counts, key=pattern_counts.get)

        # Fallback to generic naming
        return f"extracted_{Path(candidate['file_path']).stem}"

    def _extract_reusable_code(self, source_path: Path, candidate: Dict[str, Any]) -> str:
        """Extract reusable code from a source file."""
        try:
            with open(source_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            extracted_lines = []

            # Extract public functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_"):
                        # Get the lines for this node
                        start_line = node.lineno - 1
                        end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line + 10
                        lines = content.splitlines()

                        # Extract with proper indentation handling
                        node_lines = lines[start_line:end_line]
                        extracted_lines.extend(node_lines)
                        extracted_lines.append("")  # Add blank line between items

            return "\n".join(extracted_lines)

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logging.error(f"Failed to extract code from {source_path}: {e}")
            return ""

    def save_extraction_log(self, log_path: str = "tools/evidence/capability_extraction_log.json"):
        """Save the extraction operation log."""
        log_file = self.repo_root / log_path

        log_data = {
            "generated_time": datetime.now().isoformat(),
            "shared_modules_directory": str(self.shared_modules_dir.relative_to(self.repo_root)),
            "total_extractions": len(self.extraction_log),
            "extractions": self.extraction_log,
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Extraction log saved to {log_file}")
        return log_file


def main():
    """Main execution function."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    extractor = CapabilityExtractor(repo_root)

    # Load manifest and get legitimate Python files
    manifest_path = os.path.join(repo_root, "tools", "evidence", "repo_hygiene_manifest.json")
    manifest = extractor.load_manifest(manifest_path)
    python_files = extractor.get_legitimate_python_files(manifest)

    if not python_files:
        logging.info("No legitimate Python files found to analyze")
        return

    # Analyze files for capabilities
    logging.info("Analyzing files for reusable capabilities...")
    file_analyses = []
    for file_info in python_files:
        file_path = extractor.repo_root / file_info["path"]
        analysis = extractor.analyze_file_capabilities(file_path)
        if analysis:
            file_analyses.append(analysis)

    # Identify extraction candidates
    candidates = extractor.identify_extraction_candidates(file_analyses)

    if not candidates:
        logging.info("No suitable extraction candidates found")
        return

    print("\n=== HITL GATE: Capability Extraction Review ===")
    print(f"Found {len(candidates)} extraction candidates:")
    for i, candidate in enumerate(candidates[:10], 1):  # Show top 10
        print(f"  {i}. {candidate['file_path']} (score: {candidate['reusable_score']})")

    if len(candidates) > 10:
        print(f"  ... and {len(candidates) - 10} more")

    print(f"\nProceeding with extraction of top {len(candidates)} candidates...")

    # Extract capabilities
    successful_extractions = 0
    for candidate in candidates:
        print(f"\n=== HITL GATE: Extract from {candidate['file_path']} ===")
        print(f"Reusability Score: {candidate['reusable_score']}")
        print(f"Functions: {len([f for f in candidate['functions'] if not f['is_private']])}")
        print(f"Classes: {len([c for c in candidate['classes'] if not c['is_private']])}")

        # In real implementation, this would wait for user confirmation
        print("Extracting capability...")

        if extractor.extract_capability(candidate):
            successful_extractions += 1

    # Save extraction log
    log_path = extractor.save_extraction_log()

    # Print summary
    print("\n=== Capability Extraction Complete ===")
    print(f"Files analyzed: {len(file_analyses)}")
    print(f"Candidates identified: {len(candidates)}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Extraction log: {log_path}")

    return successful_extractions

    def load_manifest(self, manifest_path: str) -> List[Dict[str, Any]]:
        """Load the repo hygiene manifest."""
        with open(manifest_path) as f:
            data = json.load(f)
        return data["files"]

    def get_legitimate_python_files(self, manifest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract legitimate Python files for analysis."""
        python_files = [
            item
            for item in manifest
            if (
                item["classification"] == "legitimate"
                and item["path"].endswith(".py")
                and (Path(item["path"]).exists())
            )
        ]
        logging.info(f"Found {len(python_files)} legitimate Python files to analyze")
        return python_files

    def analyze_file_capabilities(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for reusable capabilities."""
        try:
            # Convert to absolute path and check if it's within repo
            abs_path = file_path.resolve()
            try:
                rel_path = abs_path.relative_to(self.repo_root)
            except ValueError:
                logging.warning(f"File {file_path} is outside repository root")
                return None

            with open(abs_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            capabilities = {
                "file_path": str(rel_path),
                "functions": [],
                "classes": [],
                "imports": [],
                "capability_patterns": defaultdict(list),
                "reusable_score": 0,
                "size_lines": len(content.splitlines()),
                "size_bytes": len(content),
            }

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_private": node.name.startswith("_"),
                        "calls": self._extract_function_calls(node),
                    }
                    capabilities["functions"].append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node),
                        "is_private": node.name.startswith("_"),
                    }
                    capabilities["classes"].append(class_info)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            capabilities["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            capabilities["imports"].append(f"{module}.{alias.name}")

            # Score reusability
            capabilities["reusable_score"] = self._calculate_reusability_score(capabilities)

            return capabilities

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logging.warning(f"Failed to analyze {file_path}: {e}")
            return None

    def identify_extraction_candidates(self, file_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify the best candidates for capability extraction."""
        # Sort by reusability score
        candidates = sorted(file_analyses, key=lambda x: x["reusable_score"], reverse=True)

        # Filter for candidates with reasonable scores
        high_score_candidates = [c for c in candidates if c["reusable_score"] >= 3]

        logging.info(f"Identified {len(high_score_candidates)} high-score extraction candidates")
        return high_score_candidates[:20]  # Top 20 as per plan

    def extract_capability(self, candidate: Dict[str, Any]) -> bool:
        """Extract a capability and promote it to shared modules."""
        try:
            source_path = self.repo_root / candidate["file_path"]

            # Determine target module name based on primary capability
            primary_capability = self._determine_primary_capability(candidate)
            target_module = self.shared_modules_dir / f"{primary_capability}.py"

            # Extract reusable code
            extracted_code = self._extract_reusable_code(source_path, candidate)

            if not extracted_code:
                logging.warning(f"No reusable code found in {candidate['file_path']}")
                return False

            # Write to shared module
            with open(target_module, "w", encoding="utf-8") as f:
                f.write(f'"""\nExtracted capability module: {primary_capability}\n')
                f.write(f"Source: {candidate['file_path']}\n")
                f.write(f"Extracted: {datetime.now().isoformat()}\n")
                f.write('"""\n\n')
                f.write(extracted_code)

            # Log the extraction
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_file": candidate["file_path"],
                "target_module": str(target_module.relative_to(self.repo_root)),
                "capability": primary_capability,
                "reusable_score": candidate["reusable_score"],
                "functions_extracted": len(
                    [f for f in candidate.get("functions", []) if not f.get("is_private", True)]
                ),
                "classes_extracted": len(
                    [c for c in candidate.get("classes", []) if not c.get("is_private", True)]
                ),
                "status": "extracted",
            }
            self.extraction_log.append(log_entry)

            logging.info(f"Extracted {primary_capability} from {candidate['file_path']}")
            return True

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logging.error(f"Failed to extract capability from {candidate['file_path']}: {e}")
            return False

    def save_extraction_log(self, log_path: str = "tools/evidence/capability_extraction_log.json"):
        """Save the extraction operation log."""
        log_file = self.repo_root / log_path

        log_data = {
            "generated_time": datetime.now().isoformat(),
            "shared_modules_directory": str(self.shared_modules_dir.relative_to(self.repo_root)),
            "total_extractions": len(self.extraction_log),
            "extractions": self.extraction_log,
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Extraction log saved to {log_file}")
        return log_file
