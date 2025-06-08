"""
Simplified Notification MCP Server
Handles notification services via HTTP API instead of FastMCP.
More reliable and easier to integrate with web applications.
"""

from flask import Flask, request, jsonify
import datetime
from typing import List, Dict, Any
import threading

class NotificationServer:
    """Simple notification server with HTTP API."""
    
    def __init__(self):
        # Mock notification history - in production this might be a real notification service
        self.notification_history = []
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "healthy", "server": "NotificationServer"})
        
        @self.app.route('/call/<tool_name>', methods=['POST'])
        def call_tool(tool_name):
            """Handle MCP tool calls via HTTP."""
            try:
                params = request.get_json() or {}
                
                # Call the appropriate tool
                if tool_name == "send_reminder":
                    task = params.get("task", "")
                    priority = params.get("priority", "normal")
                    result = self.send_reminder(task, priority)
                elif tool_name == "send_task_completion_notice":
                    task = params.get("task", "")
                    result = self.send_task_completion_notice(task)
                elif tool_name == "get_notification_history":
                    result = self.get_notification_history()
                elif tool_name == "schedule_daily_summary":
                    result = self.schedule_daily_summary()
                else:
                    return jsonify({"error": f"Tool not found: {tool_name}"}), 404
                
                return jsonify({"result": result})
                
            except Exception as e:
                return jsonify({"error": f"Internal error: {str(e)}"}), 500
    
    def send_reminder(self, task: str, priority: str = "normal") -> str:
        """Send a mock reminder notification for a specific task."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store notification in history
        notification_record = {
            "task": task,
            "priority": priority,
            "timestamp": timestamp,
            "type": "reminder"
        }
        self.notification_history.append(notification_record)
        
        return f"[{timestamp}] Reminder sent for task: '{task}' (Priority: {priority})"
    
    def send_task_completion_notice(self, task: str) -> str:
        """Send a notification when a task is completed."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store notification in history
        notification_record = {
            "task": task,
            "timestamp": timestamp,
            "type": "completion"
        }
        self.notification_history.append(notification_record)
        
        return f"[{timestamp}] Task completion notice sent for: '{task}'"
    
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Retrieve the history of all sent notifications."""
        return self.notification_history
    
    def schedule_daily_summary(self) -> str:
        """Schedule a daily task summary notification (mock implementation)."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        notification_record = {
            "type": "daily_summary_scheduled",
            "timestamp": timestamp,
            "status": "scheduled"
        }
        self.notification_history.append(notification_record)
        
        return f"[{timestamp}] Daily task summary notification scheduled"
    
    def run(self, host='localhost', port=8000):
        """Run the HTTP server."""
        self.app.run(host=host, port=port, debug=False, threaded=True)

def run_server():
    """Run the notification server in a separate thread."""
    server = NotificationServer()
    server.run()

if __name__ == "__main__":
    # Create and run the notification server
    print("🔔 Starting Notification Server on http://localhost:8000")
    server = NotificationServer()
    server.run() 