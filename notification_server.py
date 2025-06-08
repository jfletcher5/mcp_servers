"""
Notification MCP Server
Handles task reminder notifications and other notification services.
Uses FastMCP with HTTP transport for web-based communication.
"""

from mcp.server.fastmcp import FastMCP
import datetime
from typing import Optional

# Initialize MCP server for notification operations
mcp = FastMCP("Notification")

# Mock notification history - in production this might be a real notification service
notification_history = []

@mcp.tool()
def send_reminder(task: str, priority: str = "normal") -> str:
    """
    Send a mock reminder notification for a specific task.
    
    Args:
        task (str): The task to send a reminder for
        priority (str): Priority level (low, normal, high)
        
    Returns:
        str: Confirmation message that the reminder was sent
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store notification in history
    notification_record = {
        "task": task,
        "priority": priority,
        "timestamp": timestamp,
        "type": "reminder"
    }
    notification_history.append(notification_record)
    
    return f"[{timestamp}] Reminder sent for task: '{task}' (Priority: {priority})"

@mcp.tool()
def send_task_completion_notice(task: str) -> str:
    """
    Send a notification when a task is completed.
    
    Args:
        task (str): The completed task
        
    Returns:
        str: Confirmation message that the completion notice was sent
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store notification in history
    notification_record = {
        "task": task,
        "timestamp": timestamp,
        "type": "completion"
    }
    notification_history.append(notification_record)
    
    return f"[{timestamp}] Task completion notice sent for: '{task}'"

@mcp.tool()
def get_notification_history() -> list:
    """
    Retrieve the history of all sent notifications.
    
    Returns:
        list: List of notification records with timestamps and details
    """
    return notification_history

@mcp.tool()
def schedule_daily_summary() -> str:
    """
    Schedule a daily task summary notification (mock implementation).
    
    Returns:
        str: Confirmation that the daily summary was scheduled
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    notification_record = {
        "type": "daily_summary_scheduled",
        "timestamp": timestamp,
        "status": "scheduled"
    }
    notification_history.append(notification_record)
    
    return f"[{timestamp}] Daily task summary notification scheduled"

if __name__ == "__main__":
    # Run the MCP server using HTTP transport on port 8000
    # This allows web-based communication with the notification service
    mcp.run(transport="sse", port=8000) 