#!/usr/bin/env python3
"""Debug ADG generation hang by adding progress markers"""

import traceback
from pathlib import Path

# Monkey-patch to add progress tracking
original_scan = None

def debug_scan(self, commit_sha=""):
    """Debug wrapper for ADGStaticScanner.scan"""
    print(f"[DEBUG] Starting scan with commit_sha: {commit_sha}")
    print(f"[DEBUG] Cache path: {self.cache_path}")

    try:
        # Load cache step
        print("[DEBUG] Step 1: Loading cache...")
        from agentic_core.adg.extraction.scan_cache import ScanCache
        cache = ScanCache.load(self.cache_path) if self.cache_path else ScanCache()
        print(f"[DEBUG] Cache loaded: {cache.size()} entries")

        # Initialize manifest
        print("[DEBUG] Step 2: Initializing manifest...")
        import sys
        manifest = self.ScanManifest(
            python_ast_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            scanner_version=self._SCANNER_VERSION,
            schema_version=self._SCHEMA_VERSION,
            scanner_self_test_passed=self.run_scanner_self_test(),
        )
        print("[DEBUG] Manifest initialized")

        # File iteration
        print("[DEBUG] Step 3: Starting file iteration...")
        all_edges = []
        modules_seen = []
        syntax_error_count = 0
        syntax_errors = []

        file_count = 0
        for filepath in self._iter_python_files(self.repo_root):
            file_count += 1
            if file_count % 100 == 0:
                print(f"[DEBUG] Processed {file_count} files...")

            rel = self._repo_relative(filepath, self.repo_root)
            modules_seen.append(rel)
            manifest.discovered_module_count += 1

            # Cache check
            fhash = self.file_hash(filepath)
            cached_edge_dicts, cache_hit = cache.get(rel, fhash)

            if cache_hit and cached_edge_dicts is not None:
                # Use cached edges
                file_edges = [
                    self.Edge(
                        from_name=d["from_name"],
                        relation_type=d["relation_type"],
                        to_name=d["to_name"],
                        edge_kind=d["edge_kind"],
                        source_file=d["source_file"],
                        line_no=d["line_no"],
                        symbol=d.get("symbol", ""),
                    )
                    for d in cached_edge_dicts
                ]
                had_error = False
            else:
                # Scan file
                if file_count % 500 == 0:
                    print(f"[DEBUG] Scanning file {file_count}: {rel}")

                file_edges, had_error = self._scan_file(filepath, self.repo_root, self.include_tests)
                if not had_error:
                    cache.put(rel, fhash, file_edges)

            if had_error:
                syntax_error_count += 1
                syntax_errors.append(rel)
            else:
                manifest.parsed_module_count += 1
            all_edges.extend(file_edges)

        print(f"[DEBUG] Step 4: Completed file iteration ({file_count} files)")

        # Save cache
        if self.cache_path:
            print("[DEBUG] Step 5: Saving cache...")
            cache.save(self.cache_path)
            print("[DEBUG] Cache saved")

        # Final processing
        print("[DEBUG] Step 6: Final processing...")
        cache_stats = cache.stats()
        manifest.cache_hits = cache_stats["hits"]
        manifest.cache_misses = cache_stats["misses"]
        manifest.cache_hit_rate = cache_stats["hit_rate"]

        if manifest.parsed_module_count == 0:
            print("[DEBUG] ERROR: Zero files parsed!")
            return None

        result = self.ScanResult(commit_sha=commit_sha, manifest=manifest)
        result.edges = sorted(set(all_edges))
        result.modules = sorted(modules_seen)
        result.syntax_errors = syntax_errors
        result.compute_digest()

        print("[DEBUG] Scan completed successfully!")
        return result

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"[DEBUG] ERROR during scan: {e}")
        traceback.print_exc()
        raise

def install_debug_wrapper():
    """Install debug wrapper for ADGStaticScanner.scan"""
    import agentic_core.adg.extraction.static_scanner as scanner_module

    # Store original method
    global original_scan
    original_scan = scanner_module.ADGStaticScanner.scan

    # Install debug wrapper
    scanner_module.ADGStaticScanner.scan = debug_scan

    # Also expose needed methods
    scanner_module.ADGStaticScanner.ScanManifest = scanner_module.ScanManifest
    scanner_module.ADGStaticScanner._SCANNER_VERSION = scanner_module._SCANNER_VERSION
    scanner_module.ADGStaticScanner._SCHEMA_VERSION = scanner_module._SCHEMA_VERSION
    scanner_module.ADGStaticScanner.run_scanner_self_test = scanner_module.run_scanner_self_test
    scanner_module.ADGStaticScanner._iter_python_files = scanner_module._iter_python_files
    scanner_module.ADGStaticScanner._repo_relative = scanner_module._repo_relative
    scanner_module.ADGStaticScanner.file_hash = scanner_module.file_hash
    scanner_module.ADGStaticScanner._scan_file = scanner_module._scan_file
    scanner_module.ADGStaticScanner.ScanResult = scanner_module.ScanResult
    scanner_module.ADGStaticScanner.Edge = scanner_module.Edge

if __name__ == "__main__":
    print("=== ADG Hang Debug ===")

    # Install debug wrapper
    install_debug_wrapper()

    # Import and run ADG generation
    print("Installing debug wrapper...")
    from tools.generate_full_adg import generate_full_adg

    print("Starting ADG generation with debug...")
    artifacts_dir = Path("artifacts/adg")
    from datetime import datetime, timedelta, timezone

    # Generate timestamp
    est = timezone(timedelta(hours=-4))
    now_est = datetime.now(est)
    ts = now_est.strftime("%m%d%Y_%H%M")

    try:
        generate_full_adg(artifacts_dir, ts, archive_old=False)
        print("✅ ADG generation completed!")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ ADG generation failed: {e}")
        traceback.print_exc()
