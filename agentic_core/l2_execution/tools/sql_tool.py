#!/usr/bin/env python3
"""
SQL Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class SQLTool:
    """Parameterized SQL execution"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.connection_timeout = self.config.get("connection_timeout", 30)
        self.max_rows = self.config.get("max_rows", 1000)
        self.dry_run = self.config.get("dry_run", True)  # Safety default
    
    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute parameterized SQL query"""
        try:
            # Validate query safety
            if not self._is_safe_query(query):
                return {"error": "Query contains potentially unsafe operations", "query": query}
            
            # Simulate SQL execution (placeholder)
            if "SELECT" in query.upper():
                mock_results = [
                    {"id": 1, "name": "John Doe", "skills": "Python,AWS"},
                    {"id": 2, "name": "Jane Smith", "skills": "Python,ML"},
                    {"id": 3, "name": "Bob Johnson", "skills": "AWS,Docker"}
                ]
                
                result = {
                    "status": "success",
                    "data": mock_results[:self.max_rows],
                    "row_count": len(mock_results),
                    "query": query,
                    "params": params,
                    "execution_time": 0.05
                }
            else:
                result = {
                    "status": "success",
                    "affected_rows": 1,
                    "query": query,
                    "params": params,
                    "execution_time": 0.02
                }
            
            logger.info(f"SQL query executed successfully: {len(result.get('data', []))} rows returned")
            return result
            
        except Exception as e:
            logger.error(f"SQL query execution failed: {e}")
            return {"status": "error", "error": str(e), "query": query}
    
    def execute_select(self, table: str, columns: List[str] = None, where_clause: str = None, params: List[Any] = None) -> Dict[str, Any]:
        """Execute SELECT query with builder"""
        try:
            columns_str = ", ".join(columns or ["*"])
            query = f"SELECT {columns_str} FROM {table}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            return self.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"SELECT query failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def execute_insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute INSERT query with builder"""
        try:
            columns = list(data.keys())
            placeholders = ["%s"] * len(columns)
            values = list(data.values())
            
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            return self.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"INSERT query failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def execute_update(self, table: str, data: Dict[str, Any], where_clause: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute UPDATE query with builder"""
        try:
            set_clauses = [f"{col} = %s" for col in data.keys()]
            values = list(data.values())
            
            if params:
                values.extend(params)
            
            query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            return self.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"UPDATE query failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def execute_delete(self, table: str, where_clause: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute DELETE query with builder"""
        try:
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            return self.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"DELETE query failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def batch_execute(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple SQL queries"""
        try:
            results = []
            for query_data in queries:
                query = query_data.get("query", "")
                params = query_data.get("params")
                result = self.execute_query(query, params)
                results.append(result)
            
            logger.info(f"Batch SQL execution completed: {len(results)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Batch SQL execution failed: {e}")
            return [{"status": "error", "error": str(e)} for _ in queries]
    
    def _is_safe_query(self, query: str) -> bool:
        """Validate query safety"""
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", 
            "TRUNCATE", "EXEC", "EXECUTE", "UNION", "SCRIPT"
        ]
        
        query_upper = query.upper()
        
        # Allow SELECT queries by default
        if query_upper.strip().startswith("SELECT"):
            return True
        
        # Check for dangerous keywords
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Potentially unsafe keyword detected: {keyword}")
                return False
        
        return True
    
    def get_table_schema(self, table: str) -> Dict[str, Any]:
        """Get table schema information"""
        try:
            # Simulate schema query
            mock_schema = {
                "table_name": table,
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "name", "type": "VARCHAR(255)", "nullable": False, "primary_key": False},
                    {"name": "skills", "type": "TEXT", "nullable": True, "primary_key": False},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False, "primary_key": False}
                ]
            }
            
            logger.info(f"Retrieved schema for table: {table}")
            return mock_schema
            
        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            return {"error": str(e), "table": table}

def create_sql_tool(config: Optional[Dict[str, Any]] = None) -> SQLTool:
    """Factory function to create SQL tool instance"""
    return SQLTool(config)

# Re-export components
__all__ = [
    'SQLTool', 'create_sql_tool'
]
