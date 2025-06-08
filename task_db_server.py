"""
Task Database MCP Server
Handles task storage operations including listing and adding tasks.
Uses FastMCP to expose tools via MCP protocol.
"""

from mcp.server.fastmcp import FastMCP

# Initialize MCP server for task database operations
mcp = FastMCP("TaskDB")

# Mock task storage - in production this would be a real database
tasks = []

@mcp.tool()
def list_tasks() -> list:
    """
    List all tasks currently stored in the database.
    
    Returns:
        list: A list of all task strings
    """
    return tasks

@mcp.tool()
def add_task(task: str) -> str:
    """
    Add a new task to the database.
    
    Args:
        task (str): The task description to add
        
    Returns:
        str: Confirmation message indicating the task was added
    """
    tasks.append(task)
    return f"Task '{task}' added successfully."

@mcp.tool()
def remove_task(task: str) -> str:
    """
    Remove a task from the database if it exists.
    
    Args:
        task (str): The task description to remove
        
    Returns:
        str: Confirmation message indicating success or failure
    """
    if task in tasks:
        tasks.remove(task)
        return f"Task '{task}' removed successfully."
    else:
        return f"Task '{task}' not found in the database."

@mcp.tool()
def get_task_count() -> int:
    """
    Get the total number of tasks in the database.
    
    Returns:
        int: The number of tasks currently stored
    """
    return len(tasks)

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    # This allows the server to communicate via standard input/output
    mcp.run(transport="stdio") 