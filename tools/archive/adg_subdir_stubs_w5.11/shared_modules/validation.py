r"""
Extracted capability module: validation
Source: tests\unit\tools\adg\test_adg_query_bridge.py
Extracted: 2026-03-27T06:50:34.195032
"""


class TestADGQueryBridge:
    """Test suite for ADGQueryBridge."""

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = json.dumps({"status": "fresh"})
        mock_redis.hgetall.return_value = {"test": "data"}
        mock_redis.smembers.return_value = {"file1.py", "file2.py"}
        mock_redis.lrange.return_value = ["violation1", "violation2"]
        return mock_redis

    @pytest.fixture
    def mock_sqlite_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        # Create test database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                label TEXT,
                layer TEXT,
                entity_type TEXT,
                file_path TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT,
                source_file TEXT,
                line_no INTEGER,
                symbol TEXT
            )
        """)

        # Insert test data
        cursor.execute("""
            INSERT INTO nodes (label, layer, entity_type, file_path) VALUES
            ('test_node1', 'L1', 'function', 'test_file1.py'),
            ('test_node2', 'L2', 'function', 'test_file2.py'),
            ('subprocess_call', 'L3', 'function', 'subprocess_file.py')
        """)

        cursor.execute("""
            INSERT INTO edges (src_id, dst_id, relation_type, source_file, line_no, symbol) VALUES
            (1, 2, 'imports', 'test_file1.py', 10, 'import test_module'),
            (2, 3, 'calls', 'test_file2.py', 20, 'subprocess.run')
        """)

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def bridge_with_fallback(self, mock_sqlite_db):
        """Create bridge with SQLite fallback (no Redis)."""
        return ADGQueryBridge(redis_client=None, sqlite_path=mock_sqlite_db)

    @pytest.fixture
    def bridge_with_redis(self, mock_redis_client, mock_sqlite_db):
        """Create bridge with Redis and SQLite."""
        return ADGQueryBridge(redis_client=mock_redis_client, sqlite_path=mock_sqlite_db)

    def test_init_with_redis(self, mock_redis_client, mock_sqlite_db):
        """Test bridge initialization with Redis."""
        bridge = ADGQueryBridge(repo_root=str(mock_sqlite_db).replace(".sqlite", ""))
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_init_without_redis(self, mock_sqlite_db):
        """Test bridge initialization without Redis (SQLite fallback)."""
        bridge = ADGQueryBridge(repo_root=str(mock_sqlite_db).replace(".sqlite", ""))
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_init_fallback_to_ast(self):
        """Test bridge initialization falling back to AST only."""
        bridge = ADGQueryBridge(repo_root="/nonexistent/path")
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_check_cache_fresh_redis(self, bridge_with_redis):
        """Test cache freshness check with Redis."""
        assert bridge_with_redis._check_cache_fresh() is True

    def test_check_cache_fresh_sqlite(self, bridge_with_fallback):
        """Test cache freshness check with SQLite."""
        # Mock file mtime
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = Mock(st_mtime=1234567890)
            assert bridge_with_fallback._check_cache_fresh() is True

    def test_files_calling_redis(self, bridge_with_redis):
        """Test files_calling method with Redis backend."""
        results = bridge_with_redis.files_calling("subprocess.run")
        assert len(results) >= 2  # Mock returns 2 files
        assert all(isinstance(f, FileMatch) for f in results)

    def test_files_calling_sqlite(self, bridge_with_fallback):
        """Test files_calling method with SQLite backend."""
        results = bridge_with_fallback.files_calling("test_module")
        assert len(results) >= 1
        assert all(isinstance(f, FileMatch) for f in results)
        assert any("test_file1.py" in f.file_path for f in results)

    def test_files_importing_sqlite(self, bridge_with_fallback):
        """Test files_importing method with SQLite backend."""
        results = bridge_with_fallback.files_importing("test_module")
        assert len(results) >= 1
        assert all(isinstance(f, FileMatch) for f in results)

    def test_nodes_in_layer_sqlite(self, bridge_with_fallback):
        """Test nodes_in_layer method with SQLite backend."""
        results = bridge_with_fallback.nodes_in_layer("L1")
        assert len(results) >= 1
        assert all(isinstance(n, Node) for n in results)
        assert any(n.label == "test_node1" for n in results)
        assert all(n.layer == "L1" for n in results)

    def test_violations_fallback(self, bridge_with_fallback):
        """Test violations method with fallback."""
        results = bridge_with_fallback.violations()
        assert isinstance(results, list)

    def test_files_in_scope_fallback(self, bridge_with_fallback):
        """Test files_in_scope method with fallback."""
        results = bridge_with_fallback.files_in_scope("L1")
        assert isinstance(results, list)

    def test_subprocess_calls_without_timeout_fallback(self, bridge_with_fallback):
        """Test subprocess_calls_without_timeout method with fallback."""
        results = bridge_with_fallback.subprocess_calls_without_timeout()
        assert isinstance(results, list)
        assert all(isinstance(f, FileMatch) for f in results)

    def test_loops_without_progress_fallback(self, bridge_with_fallback):
        """Test loops_without_progress method with fallback."""
        results = bridge_with_fallback.loops_without_progress()
        assert isinstance(results, list)
        assert all(isinstance(f, FileMatch) for f in results)

    def test_redis_fallback_to_sqlite(self, mock_sqlite_db):
        """Test fallback from Redis to SQLite when Redis fails."""
        mock_redis = Mock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")

        bridge = ADGQueryBridge(redis_client=mock_redis, sqlite_path=mock_sqlite_db)
        assert bridge.backend == "sqlite"

    def test_sqlite_fallback_to_ast(self):
        """Test fallback from SQLite to AST when SQLite fails."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path="/nonexistent/path.sqlite")
        assert bridge.backend == "ast"

    def test_filematch_dataclass(self):
        """Test FileMatch dataclass."""
        file_match = FileMatch("test.py", 10, "test_symbol")
        assert file_match.file_path == "test.py"
        assert file_match.line_number == 10
        assert file_match.symbol == "test_symbol"

    def test_node_dataclass(self):
        """Test Node dataclass."""
        node = Node("test_node", "L1", "function", "test.py")
        assert node.label == "test_node"
        assert node.layer == "L1"
        assert node.entity_type == "function"
        assert node.file_path == "test.py"

    def test_violation_dataclass(self):
        """Test Violation dataclass."""
        violation = Violation("test.py", 10, "test_violation", "warning", "test message")
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.violation_type == "test_violation"
        assert violation.severity == "warning"
        assert violation.message == "test message"

    def test_ast_fallback_files_calling(self):
        """Test AST fallback for files_calling."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.files_calling("nonexistent_symbol")
        assert isinstance(results, list)

    def test_ast_fallback_files_importing(self):
        """Test AST fallback for files_importing."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.files_importing("nonexistent_module")
        assert isinstance(results, list)

    def test_ast_fallback_nodes_in_layer(self):
        """Test AST fallback for nodes_in_layer."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.nodes_in_layer("L1")
        assert isinstance(results, list)

    def test_error_handling(self, bridge_with_fallback):
        """Test error handling in query methods."""
        # Test with invalid parameters
        results = bridge_with_fallback.files_calling("")
        assert isinstance(results, list)

        results = bridge_with_fallback.nodes_in_layer("")
        assert isinstance(results, list)

    def test_warning_suppression(self, bridge_with_fallback):
        """Test that warnings are properly suppressed during fallback."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # This should not produce warnings
            results = bridge_with_fallback.files_calling("test")
            assert isinstance(results, list)


class TestADGQueryBridgeIntegration:
    """Integration tests for ADGQueryBridge."""

    def test_backend_selection_priority(self):
        """Test backend selection priority (Redis > SQLite > AST)."""
        # Test AST only
        bridge_ast = ADGQueryBridge(redis_client=None, sqlite_path=None)
        assert bridge_ast.backend == "ast"

        # Test SQLite fallback
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name
        Path(db_path).unlink()  # Delete the file to test fallback

        bridge_sqlite = ADGQueryBridge(redis_client=None, sqlite_path=db_path)
        assert bridge_sqlite.backend == "ast"  # Should fallback to AST

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_concurrent_queries(self, bridge_with_fallback):
        """Test that multiple concurrent queries work correctly."""
        import threading

        results = []

        def query_files_calling():
            results.append(bridge_with_fallback.files_calling("test"))

        def query_nodes_in_layer():
            results.append(bridge_with_fallback.nodes_in_layer("L1"))

        # Run queries concurrently
        threads = [
            threading.Thread(target=query_files_calling),
            threading.Thread(target=query_nodes_in_layer),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    def mock_redis_client(self):
        """Mock Redis client."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = json.dumps({"status": "fresh"})
        mock_redis.hgetall.return_value = {"test": "data"}
        mock_redis.smembers.return_value = {"file1.py", "file2.py"}
        mock_redis.lrange.return_value = ["violation1", "violation2"]
        return mock_redis

    def mock_sqlite_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        # Create test database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                label TEXT,
                layer TEXT,
                entity_type TEXT,
                file_path TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT,
                source_file TEXT,
                line_no INTEGER,
                symbol TEXT
            )
        """)

        # Insert test data
        cursor.execute("""
            INSERT INTO nodes (label, layer, entity_type, file_path) VALUES
            ('test_node1', 'L1', 'function', 'test_file1.py'),
            ('test_node2', 'L2', 'function', 'test_file2.py'),
            ('subprocess_call', 'L3', 'function', 'subprocess_file.py')
        """)

        cursor.execute("""
            INSERT INTO edges (src_id, dst_id, relation_type, source_file, line_no, symbol) VALUES
            (1, 2, 'imports', 'test_file1.py', 10, 'import test_module'),
            (2, 3, 'calls', 'test_file2.py', 20, 'subprocess.run')
        """)

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def bridge_with_fallback(self, mock_sqlite_db):
        """Create bridge with SQLite fallback (no Redis)."""
        return ADGQueryBridge(redis_client=None, sqlite_path=mock_sqlite_db)

    def bridge_with_redis(self, mock_redis_client, mock_sqlite_db):
        """Create bridge with Redis and SQLite."""
        return ADGQueryBridge(redis_client=mock_redis_client, sqlite_path=mock_sqlite_db)

    def test_init_with_redis(self, mock_redis_client, mock_sqlite_db):
        """Test bridge initialization with Redis."""
        bridge = ADGQueryBridge(repo_root=str(mock_sqlite_db).replace(".sqlite", ""))
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_init_without_redis(self, mock_sqlite_db):
        """Test bridge initialization without Redis (SQLite fallback)."""
        bridge = ADGQueryBridge(repo_root=str(mock_sqlite_db).replace(".sqlite", ""))
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_init_fallback_to_ast(self):
        """Test bridge initialization falling back to AST only."""
        bridge = ADGQueryBridge(repo_root="/nonexistent/path")
        # Test that bridge can be initialized without errors
        assert bridge.repo_root is not None

    def test_check_cache_fresh_redis(self, bridge_with_redis):
        """Test cache freshness check with Redis."""
        assert bridge_with_redis._check_cache_fresh() is True

    def test_check_cache_fresh_sqlite(self, bridge_with_fallback):
        """Test cache freshness check with SQLite."""
        # Mock file mtime
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = Mock(st_mtime=1234567890)
            assert bridge_with_fallback._check_cache_fresh() is True

    def test_files_calling_redis(self, bridge_with_redis):
        """Test files_calling method with Redis backend."""
        results = bridge_with_redis.files_calling("subprocess.run")
        assert len(results) >= 2  # Mock returns 2 files
        assert all(isinstance(f, FileMatch) for f in results)

    def test_files_calling_sqlite(self, bridge_with_fallback):
        """Test files_calling method with SQLite backend."""
        results = bridge_with_fallback.files_calling("test_module")
        assert len(results) >= 1
        assert all(isinstance(f, FileMatch) for f in results)
        assert any("test_file1.py" in f.file_path for f in results)

    def test_files_importing_sqlite(self, bridge_with_fallback):
        """Test files_importing method with SQLite backend."""
        results = bridge_with_fallback.files_importing("test_module")
        assert len(results) >= 1
        assert all(isinstance(f, FileMatch) for f in results)

    def test_nodes_in_layer_sqlite(self, bridge_with_fallback):
        """Test nodes_in_layer method with SQLite backend."""
        results = bridge_with_fallback.nodes_in_layer("L1")
        assert len(results) >= 1
        assert all(isinstance(n, Node) for n in results)
        assert any(n.label == "test_node1" for n in results)
        assert all(n.layer == "L1" for n in results)

    def test_violations_fallback(self, bridge_with_fallback):
        """Test violations method with fallback."""
        results = bridge_with_fallback.violations()
        assert isinstance(results, list)

    def test_files_in_scope_fallback(self, bridge_with_fallback):
        """Test files_in_scope method with fallback."""
        results = bridge_with_fallback.files_in_scope("L1")
        assert isinstance(results, list)

    def test_subprocess_calls_without_timeout_fallback(self, bridge_with_fallback):
        """Test subprocess_calls_without_timeout method with fallback."""
        results = bridge_with_fallback.subprocess_calls_without_timeout()
        assert isinstance(results, list)
        assert all(isinstance(f, FileMatch) for f in results)

    def test_loops_without_progress_fallback(self, bridge_with_fallback):
        """Test loops_without_progress method with fallback."""
        results = bridge_with_fallback.loops_without_progress()
        assert isinstance(results, list)
        assert all(isinstance(f, FileMatch) for f in results)

    def test_redis_fallback_to_sqlite(self, mock_sqlite_db):
        """Test fallback from Redis to SQLite when Redis fails."""
        mock_redis = Mock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")

        bridge = ADGQueryBridge(redis_client=mock_redis, sqlite_path=mock_sqlite_db)
        assert bridge.backend == "sqlite"

    def test_sqlite_fallback_to_ast(self):
        """Test fallback from SQLite to AST when SQLite fails."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path="/nonexistent/path.sqlite")
        assert bridge.backend == "ast"

    def test_filematch_dataclass(self):
        """Test FileMatch dataclass."""
        file_match = FileMatch("test.py", 10, "test_symbol")
        assert file_match.file_path == "test.py"
        assert file_match.line_number == 10
        assert file_match.symbol == "test_symbol"

    def test_node_dataclass(self):
        """Test Node dataclass."""
        node = Node("test_node", "L1", "function", "test.py")
        assert node.label == "test_node"
        assert node.layer == "L1"
        assert node.entity_type == "function"
        assert node.file_path == "test.py"

    def test_violation_dataclass(self):
        """Test Violation dataclass."""
        violation = Violation("test.py", 10, "test_violation", "warning", "test message")
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.violation_type == "test_violation"
        assert violation.severity == "warning"
        assert violation.message == "test message"

    def test_ast_fallback_files_calling(self):
        """Test AST fallback for files_calling."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.files_calling("nonexistent_symbol")
        assert isinstance(results, list)

    def test_ast_fallback_files_importing(self):
        """Test AST fallback for files_importing."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.files_importing("nonexistent_module")
        assert isinstance(results, list)

    def test_ast_fallback_nodes_in_layer(self):
        """Test AST fallback for nodes_in_layer."""
        bridge = ADGQueryBridge(redis_client=None, sqlite_path=None)
        results = bridge.nodes_in_layer("L1")
        assert isinstance(results, list)

    def test_error_handling(self, bridge_with_fallback):
        """Test error handling in query methods."""
        # Test with invalid parameters
        results = bridge_with_fallback.files_calling("")
        assert isinstance(results, list)

        results = bridge_with_fallback.nodes_in_layer("")
        assert isinstance(results, list)

    def test_warning_suppression(self, bridge_with_fallback):
        """Test that warnings are properly suppressed during fallback."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # This should not produce warnings
            results = bridge_with_fallback.files_calling("test")
            assert isinstance(results, list)

    def test_backend_selection_priority(self):
        """Test backend selection priority (Redis > SQLite > AST)."""
        # Test AST only
        bridge_ast = ADGQueryBridge(redis_client=None, sqlite_path=None)
        assert bridge_ast.backend == "ast"

        # Test SQLite fallback
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name
        Path(db_path).unlink()  # Delete the file to test fallback

        bridge_sqlite = ADGQueryBridge(redis_client=None, sqlite_path=db_path)
        assert bridge_sqlite.backend == "ast"  # Should fallback to AST

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_concurrent_queries(self, bridge_with_fallback):
        """Test that multiple concurrent queries work correctly."""
        import threading

        results = []

        def query_files_calling():
            results.append(bridge_with_fallback.files_calling("test"))

        def query_nodes_in_layer():
            results.append(bridge_with_fallback.nodes_in_layer("L1"))

        # Run queries concurrently
        threads = [
            threading.Thread(target=query_files_calling),
            threading.Thread(target=query_nodes_in_layer),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    class FileMatch:
        def __init__(self, file_path, line_number=None, symbol=None, context=None):
            self.file_path = file_path
            self.line_number = line_number
            self.symbol = symbol
            self.context = context

    class Node:
        def __init__(self, label, layer, entity_type, file_path):
            self.label = label
            self.layer = layer
            self.entity_type = entity_type
            self.file_path = file_path

    class Violation:
        def __init__(self, file_path, line_number, category, evidence="", symbol=None):
            self.file_path = file_path
            self.line_number = line_number
            self.category = category
            self.evidence = evidence
            self.symbol = symbol

    class ADGQueryBridge:
        def __init__(self, repo_root=None):
            self.repo_root = repo_root

        def files_calling(self, symbol):
            return []

        def files_importing(self, module):
            return []

        def nodes_in_layer(self, layer):
            return []

        def violations(self):
            return []

        def query_files_calling():
            results.append(bridge_with_fallback.files_calling("test"))

        def query_nodes_in_layer():
            results.append(bridge_with_fallback.nodes_in_layer("L1"))

        def files_calling(self, symbol):
            return []

        def files_importing(self, module):
            return []

        def nodes_in_layer(self, layer):
            return []

        def violations(self):
            return []
