"""
Simplified Task Database MCP Server
Handles task storage operations with direct JSON-RPC over STDIO.
More reliable than FastMCP for web application integration.
"""

import json
import sys
import threading
from typing import List, Dict, Any

class TaskDatabaseServer:
    """Simple task database server with JSON-RPC over STDIO."""
    
    def __init__(self):
        # Mock task storage - in production this would be a real database
        self.tasks = []
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            # Route to appropriate method
            if method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                # Call the appropriate tool
                if tool_name == "list_tasks":
                    result = self.list_tasks()
                elif tool_name == "add_task":
                    result = self.add_task(tool_args.get("task", ""))
                elif tool_name == "remove_task":
                    result = self.remove_task(tool_args.get("task", ""))
                elif tool_name == "get_task_count":
                    result = self.get_task_count()
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {tool_name}"}
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": str(result)}]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
    
    def list_tasks(self) -> List[str]:
        """List all tasks currently stored in the database."""
        return self.tasks
    
    def add_task(self, task: str) -> str:
        """Add a new task to the database."""
        if task and task.strip():
            self.tasks.append(task.strip())
            return f"Task '{task}' added successfully."
        return "Cannot add empty task."
    
    def remove_task(self, task: str) -> str:
        """Remove a task from the database if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)
            return f"Task '{task}' removed successfully."
        else:
            return f"Task '{task}' not found in the database."
    
    def get_task_count(self) -> int:
        """Get the total number of tasks in the database."""
        return len(self.tasks)
    
    def run(self):
        """Run the server, listening for JSON-RPC requests on STDIN."""
        try:
            while True:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                    
                try:
                    # Parse JSON request
                    request = json.loads(line.strip())
                    
                    # Handle request
                    response = self.handle_request(request)
                    
                    # Send response to stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError:
                    # Invalid JSON
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except (EOFError, KeyboardInterrupt):
            # Clean shutdown
            pass

if __name__ == "__main__":
    # Create and run the task database server
    server = TaskDatabaseServer()
    server.run() 