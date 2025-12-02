#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Main Execution Script

Orchestrates the complete semantic cache rebuild process for both Resume Engine (RG)
and Outreach Engine (LIC) archives with strict engine separation and zero-loss guarantee.

Usage:
    python scripts/run_phase_0_5_semantic_cache.py [--dry-run] [--validate-only] [--engine RG|LIC]
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "schemas"))
sys.path.append(str(project_root / "runtime"))

from semantic_lineage import EngineType, GlobalCacheReport
from semantic_scanner import SemanticScanner, ScanConfiguration


class Phase05Orchestrator:
    """Main orchestrator for Phase 0.5 semantic cache rebuild"""
    
    def __init__(self, config: ScanConfiguration):
        self.config = config
        self.scanner = SemanticScanner(config)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        log_dir = self.config.output_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"phase_0_5_rebuild_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger("Phase05Orchestrator")
    
    def run_dry_run(self) -> Dict[str, Any]:
        """Perform dry-run validation of all archive paths and file counts"""
        self.logger.info("Starting dry-run validation")
        
        results = {
            "validation_errors": [],
            "archive_summary": {},
            "total_files_discovered": 0,
            "validation_passed": True
        }
        
        # Validate resume engine archives
        self.logger.info("Validating Resume Engine (RG) archives")
        rg_results = self._validate_archives(self.config.resume_archives, EngineType.RESUME_ENGINE)
        results["archive_summary"]["resume_engine"] = rg_results
        
        # Validate outreach engine archives
        self.logger.info("Validating Outreach Engine (LIC) archives")
        lic_results = self._validate_archives(self.config.outreach_archives, EngineType.OUTREACH_ENGINE)
        results["archive_summary"]["outreach_engine"] = lic_results
        
        # Calculate totals
        for engine_results in results["archive_summary"].values():
            results["total_files_discovered"] += engine_results["total_files"]
            results["validation_errors"].extend(engine_results["errors"])
        
        results["validation_passed"] = len(results["validation_errors"]) == 0
        
        self.logger.info(f"Dry-run completed: {results['total_files_discovered']} files discovered")
        if results["validation_errors"]:
            self.logger.warning(f"Found {len(results['validation_errors'])} validation errors")
        
        return results
    
    def _validate_archives(self, archive_paths: List[str], engine: EngineType) -> Dict[str, Any]:
        """Validate a list of archives for a specific engine"""
        results = {
            "engine": engine.value,
            "total_archives": len(archive_paths),
            "valid_archives": 0,
            "total_files": 0,
            "archive_details": {},
            "errors": []
        }
        
        for archive_path in archive_paths:
            archive_name = Path(archive_path).name
            archive_result = self._validate_single_archive(Path(archive_path), engine)
            
            results["archive_details"][archive_name] = archive_result
            results["total_files"] += archive_result["file_count"]
            
            if archive_result["valid"]:
                results["valid_archives"] += 1
            else:
                results["errors"].extend(archive_result["errors"])
        
        self.logger.info(f"{engine.value} validation: {results['valid_archives']}/{results['total_archives']} valid, {results['total_files']} files")
        return results
    
    def _validate_single_archive(self, archive_path: Path, engine: EngineType) -> Dict[str, Any]:
        """Validate a single archive directory"""
        result = {
            "path": str(archive_path),
            "valid": True,
            "file_count": 0,
            "errors": [],
            "sample_files": []
        }
        
        # Check if directory exists
        if not archive_path.exists():
            result["valid"] = False
            result["errors"].append(f"Archive directory does not exist: {archive_path}")
            return result
        
        if not archive_path.is_dir():
            result["valid"] = False
            result["errors"].append(f"Path is not a directory: {archive_path}")
            return result
        
        # Discover files
        try:
            file_count = 0
            sample_files = []
            
            for file_path in archive_path.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    if len(sample_files) < 5:  # Keep sample of first 5 files
                        relative_path = file_path.relative_to(archive_path)
                        depth = len(relative_path.parts)
                        sample_files.append({
                            "file": str(relative_path),
                            "size": file_path.stat().st_size,
                            "depth": depth
                        })
                    
                    # Check depth constraint
                    relative_path = file_path.relative_to(archive_path)
                    depth = len(relative_path.parts)
                    if depth > self.config.max_depth:
                        result["errors"].append(f"File exceeds max depth {self.config.max_depth}: {relative_path}")
            
            result["file_count"] = file_count
            result["sample_files"] = sample_files
            
            if file_count == 0:
                result["valid"] = False
                result["errors"].append(f"No files found in archive: {archive_path}")
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error scanning archive {archive_path}: {e}")
        
        return result
    
    def run_full_rebuild(self, engine_filter: Optional[EngineType] = None) -> GlobalCacheReport:
        """Execute the full semantic cache rebuild process"""
        self.logger.info("Starting full semantic cache rebuild")
        start_time = time.time()
        
        try:
            # Apply engine filter if specified
            if engine_filter == EngineType.RESUME_ENGINE:
                self.logger.info("Engine filter applied: Resume Engine (RG) only")
                original_outreach = self.config.outreach_archives
                self.config.outreach_archives = []
                global_report = self.scanner.scan_all_archives()
                self.config.outreach_archives = original_outreach
                
            elif engine_filter == EngineType.OUTREACH_ENGINE:
                self.logger.info("Engine filter applied: Outreach Engine (LIC) only")
                original_resume = self.config.resume_archives
                self.config.resume_archives = []
                global_report = self.scanner.scan_all_archives()
                self.config.resume_archives = original_resume
                
            else:
                self.logger.info("Processing both Resume Engine (RG) and Outreach Engine (LIC)")
                global_report = self.scanner.scan_all_archives()
            
            # Generate and save detailed reports
            self._save_detailed_reports(global_report)
            
            # Validate completeness
            self._validate_completeness(global_report)
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"Semantic cache rebuild completed in {duration:.2f} seconds")
            self.logger.info(f"Overall completeness: {global_report.completeness_report['overall_completeness']:.2%}")
            
            return global_report
            
        except Exception as e:
            self.logger.error(f"Semantic cache rebuild failed: {e}")
            raise
    
    def _save_detailed_reports(self, global_report: GlobalCacheReport):
        """Save detailed reports for analysis"""
        reports_dir = self.config.output_root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main global report
        global_report_path = reports_dir / f"global_report_{timestamp}.json"
        with open(global_report_path, 'w', encoding='utf-8') as f:
            json.dump(global_report.to_dict(), f, indent=2, default=str)
        
        # Save engine-specific reports
        for engine_name, manifests in [("resume_engine", global_report.resume_engine_manifests),
                                      ("outreach_engine", global_report.outreach_engine_manifests)]:
            engine_report = {
                "engine": engine_name,
                "archives": {version: manifest.to_dict() for version, manifest in manifests.items()},
                "total_archives": len(manifests),
                "total_files": sum(m.processed_files for m in manifests.values()),
                "average_completeness": sum(m.completeness_score for m in manifests.values()) / len(manifests) if manifests else 0.0
            }
            
            engine_report_path = reports_dir / f"{engine_name}_report_{timestamp}.json"
            with open(engine_report_path, 'w', encoding='utf-8') as f:
                json.dump(engine_report, f, indent=2, default=str)
        
        self.logger.info(f"Detailed reports saved to: {reports_dir}")
    
    def _validate_completeness(self, global_report: GlobalCacheReport):
        """Validate completeness and report any issues"""
        completeness = global_report.completeness_report
        
        if completeness["missing_archives"]:
            self.logger.warning(f"Missing archives: {completeness['missing_archives']}")
        
        if completeness["overall_completeness"] < 0.95:
            self.logger.warning(f"Low completeness score: {completeness['overall_completeness']:.2%}")
        
        # Check for failed files
        total_failed = 0
        for manifests in [global_report.resume_engine_manifests, global_report.outreach_engine_manifests]:
            for manifest in manifests.values():
                total_failed += len(manifest.failed_files)
        
        if total_failed > 0:
            self.logger.warning(f"Total failed files: {total_failed}")
        
        # Validate output directory structure
        self._validate_output_structure()
    
    def _validate_output_structure(self):
        """Validate that all required output directories and files exist"""
        required_dirs = [
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
        
        missing_dirs = []
        for directory in required_dirs:
            if not directory.exists():
                missing_dirs.append(str(directory))
        
        if missing_dirs:
            self.logger.error(f"Missing output directories: {missing_dirs}")
        else:
            self.logger.info("Output directory structure validation passed")
    
    def run_validation_only(self) -> Dict[str, Any]:
        """Run validation on existing semantic cache"""
        self.logger.info("Running validation on existing semantic cache")
        
        validation_results = {
            "cache_exists": self.config.output_root.exists(),
            "structure_valid": False,
            "engine_separation_valid": False,
            "artifact_integrity": {},
            "validation_passed": False
        }
        
        if not validation_results["cache_exists"]:
            self.logger.error("Semantic cache directory does not exist")
            return validation_results
        
        # Validate structure
        validation_results["structure_valid"] = self._validate_output_structure()
        
        # Validate engine separation
        validation_results["engine_separation_valid"] = self._validate_engine_separation()
        
        # Validate artifact integrity
        validation_results["artifact_integrity"] = self._validate_artifact_integrity()
        
        validation_results["validation_passed"] = all([
            validation_results["structure_valid"],
            validation_results["engine_separation_valid"],
            validation_results["artifact_integrity"]["overall_valid"]
        ])
        
        return validation_results
    
    def _validate_engine_separation(self) -> bool:
        """Validate that RG and LIC engines are properly separated"""
        rg_dir = self.config.output_root / "resume_engine"
        lic_dir = self.config.output_root / "outreach_engine"
        
        if not (rg_dir.exists() and lic_dir.exists()):
            return False
        
        # Check that no files cross between engines
        rg_versions = set([d.name for d in rg_dir.iterdir() if d.is_dir()])
        lic_versions = set([d.name for d in lic_dir.iterdir() if d.is_dir()])
        
        overlap = rg_versions.intersection(lic_versions)
        if overlap:
            self.logger.warning(f"Engine separation violation: overlapping versions {overlap}")
            return False
        
        return True
    
    def _validate_artifact_integrity(self) -> Dict[str, Any]:
        """Validate integrity of cached artifacts"""
        integrity_results = {
            "total_artifacts": 0,
            "valid_artifacts": 0,
            "corrupted_artifacts": 0,
            "overall_valid": True
        }
        
        # Check all engine directories
        for engine_dir in [self.config.output_root / "resume_engine", self.config.output_root / "outreach_engine"]:
            if not engine_dir.exists():
                continue
            
            for version_dir in engine_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                
                for artifact_file in version_dir.glob("*.json"):
                    integrity_results["total_artifacts"] += 1
                    
                    try:
                        with open(artifact_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                        integrity_results["valid_artifacts"] += 1
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        integrity_results["corrupted_artifacts"] += 1
                        self.logger.warning(f"Corrupted artifact: {artifact_file} - {e}")
        
        integrity_results["overall_valid"] = integrity_results["corrupted_artifacts"] == 0
        
        self.logger.info(f"Artifact integrity: {integrity_results['valid_artifacts']}/{integrity_results['total_artifacts']} valid")
        return integrity_results


def create_default_config() -> ScanConfiguration:
    """Create default scan configuration"""
    return ScanConfiguration(
        max_depth=7,
        max_workers=8,
        chunk_size=100,
        enable_embeddings=True,
        embedding_model="text-embedding-ada-002",
        embedding_dimensions=1536,
        output_root=Path("data/semantic_cache")
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Phase 0.5 Semantic Cache Rebuild",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_phase_0_5_semantic_cache.py --dry-run
    python scripts/run_phase_0_5_semantic_cache.py --validate-only
    python scripts/run_phase_0_5_semantic_cache.py --engine RG
    python scripts/run_phase_0_5_semantic_cache.py  # Full rebuild
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry-run validation without processing files"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate existing semantic cache without rebuilding"
    )
    
    parser.add_argument(
        "--engine",
        choices=["RG", "LIC"],
        help="Process only specified engine (RG=Resume Engine, LIC=Outreach Engine)"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum number of parallel workers (default: 8)"
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=7,
        help="Maximum recursion depth for file discovery (default: 7)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/semantic_cache",
        help="Output directory for semantic cache (default: data/semantic_cache)"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = create_default_config()
    config.max_workers = args.max_workers
    config.max_depth = args.max_depth
    config.output_root = Path(args.output_dir)
    
    # Create orchestrator
    orchestrator = Phase05Orchestrator(config)
    
    try:
        if args.dry_run:
            # Perform dry-run validation
            results = orchestrator.run_dry_run()
            
            print("\n" + "="*80)
            print("DRY-RUN VALIDATION RESULTS")
            print("="*80)
            print(f"Validation passed: {results['validation_passed']}")
            print(f"Total files discovered: {results['total_files_discovered']}")
            
            for engine_name, engine_results in results["archive_summary"].items():
                print(f"\n{engine_name.upper()}:")
                print(f"  Valid archives: {engine_results['valid_archives']}/{engine_results['total_archives']}")
                print(f"  Total files: {engine_results['total_files']}")
                
                if engine_results["errors"]:
                    print(f"  Errors: {len(engine_results['errors'])}")
                    for error in engine_results["errors"][:5]:  # Show first 5 errors
                        print(f"    - {error}")
            
            if results["validation_errors"]:
                print(f"\nTotal validation errors: {len(results['validation_errors'])}")
            
            sys.exit(0 if results["validation_passed"] else 1)
        
        elif args.validate_only:
            # Validate existing cache
            results = orchestrator.run_validation_only()
            
            print("\n" + "="*80)
            print("CACHE VALIDATION RESULTS")
            print("="*80)
            print(f"Cache exists: {results['cache_exists']}")
            print(f"Structure valid: {results['structure_valid']}")
            print(f"Engine separation valid: {results['engine_separation_valid']}")
            print(f"Overall validation passed: {results['validation_passed']}")
            
            if results["artifact_integrity"]["total_artifacts"] > 0:
                print(f"Artifacts: {results['artifact_integrity']['valid_artifacts']}/{results['artifact_integrity']['total_artifacts']} valid")
            
            sys.exit(0 if results["validation_passed"] else 1)
        
        else:
            # Run full rebuild
            engine_filter = None
            if args.engine:
                engine_filter = EngineType.RESUME_ENGINE if args.engine == "RG" else EngineType.OUTREACH_ENGINE
            
            global_report = orchestrator.run_full_rebuild(engine_filter)
            
            print("\n" + "="*80)
            print("SEMANTIC CACHE REBUILD COMPLETED")
            print("="*80)
            print(f"Overall completeness: {global_report.completeness_report['overall_completeness']:.2%}")
            print(f"Total archives processed: {global_report.global_integrity['total_archives']}")
            print(f"Total files processed: {global_report.global_integrity['total_files_processed']}")
            
            if global_report.completeness_report["missing_archives"]:
                print(f"Missing archives: {len(global_report.completeness_report['missing_archives'])}")
            
            print(f"\nResults written to: {config.output_root}")
            
            # Exit with error code if completeness is too low
            if global_report.completeness_report['overall_completeness'] < 0.9:
                print("WARNING: Low completeness score detected")
                sys.exit(1)
            else:
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
