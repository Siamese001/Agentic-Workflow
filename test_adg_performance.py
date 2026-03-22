#!/usr/bin/env python3
"""Comprehensive ADG performance testing suite."""
import json
import sqlite3
import statistics
import subprocess
import time
from pathlib import Path


class ADGPerformanceTester:
    def __init__(self):
        self.root = Path(__file__).parent
        self.adg_dir = self.root / "artifacts/adg"
        self.results = []

    def run_adg_generation(self, label: str) -> dict:
        """Run ADG generation and collect metrics."""
        print(f"\n=== Running {label} ===")

        start_time = time.time()
        try:
            result = subprocess.run(
                ["python", "tools/generate_full_adg.py"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            end_time = time.time()
            total_time = end_time - start_time

            # Parse output for metrics
            output_lines = result.stdout.split('\n')
            metrics = self._parse_adg_output(output_lines)

            metrics.update({
                'label': label,
                'total_time_seconds': total_time,
                'exit_code': result.returncode,
                'success': result.returncode == 0
            })

            print(f"✓ Completed in {total_time:.2f}s")
            print(f"  Modules: {metrics.get('modules', 'N/A')}")
            print(f"  Edges: {metrics.get('edges', 'N/A')}")
            print(f"  Cache hit rate: {metrics.get('cache_hit_rate', 'N/A')}")

            return metrics

        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT after 300s")
            return {
                'label': label,
                'total_time_seconds': 300,
                'exit_code': -1,
                'success': False,
                'error': 'TIMEOUT'
            }
        except Exception as e:
            print(f"✗ ERROR: {e}")
            return {
                'label': label,
                'total_time_seconds': 0,
                'exit_code': -1,
                'success': False,
                'error': str(e)
            }

    def _parse_adg_output(self, lines: list[str]) -> dict:
        """Parse ADG output for key metrics."""
        metrics = {}

        for line in lines:
            if "[ADG] Modules:" in line:
                metrics['modules'] = int(line.split(':')[1].strip())
            elif "[ADG] Edges:" in line:
                metrics['edges'] = int(line.split(':')[1].strip())
            elif "[ADG] Cache:" in line:
                cache_info = line.split(':')[1].strip()
                if 'hits=' in cache_info:
                    hits = int(cache_info.split('hits=')[1].split()[0])
                    misses = int(cache_info.split('misses=')[1].split()[0])
                    rate = float(cache_info.split('rate=')[1].strip().rstrip('%'))
                    metrics['cache_hits'] = hits
                    metrics['cache_misses'] = misses
                    metrics['cache_hit_rate'] = rate
            elif "entities=" in line and "relations=" in line:
                parts = line.split()
                for part in parts:
                    if part.startswith('entities='):
                        metrics['entities'] = int(part.split('=')[1])
                    elif part.startswith('relations='):
                        metrics['relations'] = int(part.split('=')[1])

        return metrics

    def get_sqlite_metrics(self, sqlite_path: Path) -> dict:
        """Extract detailed metrics from SQLite database."""
        if not sqlite_path.exists():
            return {}

        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()

        metrics = {}

        # Node counts by layer
        cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC")
        layer_counts = dict(cur.fetchall())
        metrics['layer_distribution'] = layer_counts

        # Edge counts by type
        cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC LIMIT 10")
        edge_types = dict(cur.fetchall())
        metrics['edge_type_distribution'] = edge_types

        # Database size
        metrics['sqlite_size_mb'] = sqlite_path.stat().st_size / (1024 * 1024)

        conn.close()
        return metrics

    def test_cache_performance(self) -> dict:
        """Test cache performance scenarios."""
        print("\n=== Cache Performance Test ===")

        # Clear cache first
        cache_file = self.adg_dir / "scan_result_cache.json"
        if cache_file.exists():
            cache_file.unlink()

        # Cold run
        cold_metrics = self.run_adg_generation("Cold Cache")

        # Warm run
        warm_metrics = self.run_adg_generation("Warm Cache")

        # Force cache invalidation
        if cache_file.exists():
            # Touch a file to trigger cache invalidation
            test_file = self.root / "agentic_core" / "__init__.py"
            if test_file.exists():
                test_file.touch()

        # Partial cache hit run
        partial_metrics = self.run_adg_generation("Partial Cache")

        return {
            'cold_run': cold_metrics,
            'warm_run': warm_metrics,
            'partial_run': partial_metrics,
            'cache_speedup': cold_metrics['total_time_seconds'] / warm_metrics['total_time_seconds'] if warm_metrics['success'] else 0
        }

    def test_incremental_vs_full(self) -> dict:
        """Test incremental update vs full regeneration."""
        print("\n=== Incremental vs Full Test ===")

        # Full regeneration
        full_metrics = self.run_adg_generation("Full Regeneration")

        # Make a small change
        test_file = self.root / "agentic_core" / "L0_routing" / "__init__.py"
        if test_file.exists():
            original_content = test_file.read_text()
            test_file.write_text(original_content + "\n# Performance test comment\n")

        # Test incremental update if available
        incremental_metrics = {}
        try:
            incremental_result = subprocess.run(
                ["python", "tools/adg_incremental_update.py", str(test_file)],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=120
            )

            if incremental_result.returncode == 0:
                incremental_metrics = {
                    'label': 'Incremental Update',
                    'total_time_seconds': float(incremental_result.stdout.strip().split()[-1]) if incremental_result.stdout.strip() else 0,
                    'exit_code': incremental_result.returncode,
                    'success': True
                }
            else:
                incremental_metrics = {
                    'label': 'Incremental Update',
                    'total_time_seconds': 0,
                    'exit_code': incremental_result.returncode,
                    'success': False,
                    'error': incremental_result.stderr
                }
        except Exception as e:
            incremental_metrics = {
                'label': 'Incremental Update',
                'total_time_seconds': 0,
                'exit_code': -1,
                'success': False,
                'error': str(e)
            }

        # Restore original file
        if test_file.exists():
            test_file.write_text(original_content)

        return {
            'full_regeneration': full_metrics,
            'incremental_update': incremental_metrics,
            'incremental_speedup': full_metrics['total_time_seconds'] / incremental_metrics['total_time_seconds'] if incremental_metrics['success'] else 0
        }

    def run_comprehensive_test(self) -> dict:
        """Run comprehensive performance test suite."""
        print("🚀 Starting Comprehensive ADG Performance Test")
        print("=" * 60)

        results = {
            'test_timestamp': time.time(),
            'cache_performance': self.test_cache_performance(),
            'incremental_vs_full': self.test_incremental_vs_full(),
        }

        # Get latest SQLite metrics
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if sqlite_files:
            latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
            results['sqlite_metrics'] = self.get_sqlite_metrics(latest_sqlite)

        # Calculate summary statistics
        all_runs = []
        for test_category in results.values():
            if isinstance(test_category, dict):
                for run_name, run_data in test_category.items():
                    if isinstance(run_data, dict) and 'total_time_seconds' in run_data:
                        all_runs.append(run_data['total_time_seconds'])

        if all_runs:
            results['summary'] = {
                'total_runs': len(all_runs),
                'fastest_run': min(all_runs),
                'slowest_run': max(all_runs),
                'average_time': statistics.mean(all_runs),
                'median_time': statistics.median(all_runs)
            }

        return results

    def save_results(self, results: dict):
        """Save test results to file."""
        results_file = self.root / "adg_performance_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📊 Results saved to: {results_file}")

        # Print summary
        if 'summary' in results:
            summary = results['summary']
            print("\n📈 Performance Summary:")
            print(f"  Total runs: {summary['total_runs']}")
            print(f"  Fastest: {summary['fastest_run']:.2f}s")
            print(f"  Slowest: {summary['slowest_run']:.2f}s")
            print(f"  Average: {summary['average_time']:.2f}s")
            print(f"  Median: {summary['median_time']:.2f}s")

        if 'cache_performance' in results:
            cache_perf = results['cache_performance']
            if cache_perf.get('cache_speedup', 0) > 0:
                print(f"  Cache speedup: {cache_perf['cache_speedup']:.2f}x")

        if 'incremental_vs_full' in results:
            inc_perf = results['incremental_vs_full']
            if inc_perf.get('incremental_speedup', 0) > 0:
                print(f"  Incremental speedup: {inc_perf['incremental_speedup']:.2f}x")

if __name__ == "__main__":
    tester = ADGPerformanceTester()
    results = tester.run_comprehensive_test()
    tester.save_results(results)
