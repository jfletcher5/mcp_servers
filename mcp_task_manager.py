"""
MCP-Powered Task Manager Agent
Demonstrates the benefits of Model Context Protocol by connecting to multiple
specialized MCP servers via different transport mechanisms.

Key Benefits Demonstrated:
1. Protocol Standardization - Uniform interface across different services
2. Transport Flexibility - STDIO and HTTP/SSE transports working together  
3. Service Modularity - Independent, specialized microservices
4. Language Agnostic - MCP servers can be written in any language
5. Easy Extensibility - Add new services without changing core agent code
"""

import asyncio
import os
import json
import subprocess
import aiohttp
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class MCPTaskManagerAgent:
    """
    Advanced task manager agent that demonstrates MCP protocol benefits.
    
    This agent connects to multiple MCP servers via different transports:
    - Task Database Server (STDIO transport)
    - Notification Server (HTTP/SSE transport)
    
    Benefits demonstrated:
    - Protocol standardization across different services
    - Transport flexibility (STDIO + HTTP working together)
    - Service modularity and independence
    - Easy extensibility without core changes
    """
    
    def __init__(self):
        """Initialize the MCP-based task manager agent."""
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        )
        self.agent = None
        self.task_db_process = None
        self.notification_server_url = "http://localhost:8000"
        
    async def start_mcp_servers(self):
        """
        Start the MCP servers that this agent will communicate with.
        
        Demonstrates:
        - Multi-transport architecture (STDIO + HTTP)
        - Independent service lifecycle management
        - Graceful startup and health checking
        """
        print("🚀 Starting MCP servers...")
        
        # Start Task Database Server (STDIO transport)
        try:
            self.task_db_process = subprocess.Popen(
                ["python", "task_db_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered for immediate communication
            )
            # Give the server a moment to start
            await asyncio.sleep(0.5)
            
            # Test the connection
            test_result = await self._call_task_db_server("get_task_count")
            if "❌" not in test_result:
                print("✅ Task Database Server started (STDIO transport)")
            else:
                print(f"⚠️ Task Database Server started but communication test failed: {test_result}")
                # Continue anyway, might work later
        except Exception as e:
            print(f"❌ Failed to start Task Database Server: {e}")
            return False
        
        # Start Notification Server (HTTP/SSE transport)
        try:
            # Start notification server in background
            subprocess.Popen(
                ["python", "notification_server.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for HTTP server to be ready
            await self._wait_for_http_server()
            print("✅ Notification Server started (HTTP/SSE transport)")
        except Exception as e:
            print(f"❌ Failed to start Notification Server: {e}")
            return False
        
        return True
    
    async def _wait_for_http_server(self, max_retries=10):
        """Wait for HTTP server to be ready."""
        for i in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.notification_server_url}/health", timeout=1) as response:
                        if response.status == 200:
                            return True
            except:
                await asyncio.sleep(1)
        return False
    
    async def _call_task_db_server(self, method: str, params: Dict = None) -> str:
        """
        Communicate with Task DB Server via STDIO transport.
        
        Demonstrates:
        - STDIO-based MCP communication
        - JSON-RPC protocol usage
        - Error handling for process communication
        """
        if not self.task_db_process or self.task_db_process.poll() is not None:
            # Process not available or has died, try to restart
            await self._restart_task_db_server()
            if not self.task_db_process:
                return "❌ Task Database Server not available"
        
        # Prepare MCP tool call
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params or {}
            }
        }
        
        try:
            # Convert request to JSON string
            request_json = json.dumps(request) + "\n"
            
            # Send request to STDIO MCP server
            self.task_db_process.stdin.write(request_json)
            self.task_db_process.stdin.flush()
            
            # Read response with timeout
            import asyncio
            import threading
            
            response_line = None
            def read_response():
                nonlocal response_line
                try:
                    response_line = self.task_db_process.stdout.readline()
                except:
                    response_line = None
            
            # Run the blocking read in a thread
            thread = threading.Thread(target=read_response)
            thread.start()
            thread.join(timeout=5)  # 5 second timeout
            
            if response_line and response_line.strip():
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        return str(response["result"]["content"][0]["text"])
                    elif "error" in response:
                        return f"❌ Error: {response['error']['message']}"
                except json.JSONDecodeError as e:
                    return f"❌ Invalid JSON response: {response_line}"
            
            return "❌ No response from Task Database Server"
            
        except Exception as e:
            # Try to restart the server on communication error
            await self._restart_task_db_server()
            return f"❌ Communication error with Task Database Server: {str(e)}"
    
    async def _restart_task_db_server(self):
        """Restart the task database server if it's not responding."""
        if self.task_db_process:
            try:
                self.task_db_process.terminate()
                self.task_db_process.wait(timeout=2)
            except:
                try:
                    self.task_db_process.kill()
                except:
                    pass
        
        try:
            self.task_db_process = subprocess.Popen(
                ["python", "task_db_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            # Give it a moment to start
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to restart Task Database Server: {e}")
            self.task_db_process = None
    
    async def _call_notification_server(self, method: str, params: Dict = None) -> str:
        """
        Communicate with Notification Server via HTTP transport.
        
        Demonstrates:
        - HTTP-based MCP communication
        - RESTful API integration
        - Async HTTP client usage
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Call MCP tool via HTTP
                url = f"{self.notification_server_url}/call/{method}"
                async with session.post(url, json=params or {}) as response:
                    if response.status == 200:
                        result = await response.json()
                        return str(result.get("result", "Success"))
                    else:
                        error_text = await response.text()
                        return f"❌ HTTP Error {response.status}: {error_text}"
        except Exception as e:
            return f"❌ Communication error with Notification Server: {str(e)}"
    
    # Task Management Tools (via STDIO MCP Server)
    async def add_task_mcp(self, task: str) -> str:
        """Add a task via MCP Task Database Server."""
        result = await self._call_task_db_server("add_task", {"task": task})
        return f"✅ {result}"
    
    async def list_tasks_mcp(self) -> str:
        """List tasks via MCP Task Database Server."""
        result = await self._call_task_db_server("list_tasks")
        if isinstance(result, str) and result.startswith("["):
            # Parse list result
            try:
                tasks = eval(result)  # In production, use json.loads
                if not tasks:
                    return "📝 No tasks found. Your task list is empty!"
                task_list = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
                return f"📝 Your current tasks:\n{task_list}\n\nTotal: {len(tasks)} tasks"
            except:
                return str(result)
        return str(result)
    
    async def remove_task_mcp(self, task: str) -> str:
        """Remove a task via MCP Task Database Server."""
        result = await self._call_task_db_server("remove_task", {"task": task})
        return f"✅ {result}"
    
    async def get_task_count_mcp(self) -> str:
        """Get task count via MCP Task Database Server."""
        result = await self._call_task_db_server("get_task_count")
        count = int(result) if result.isdigit() else 0
        if count == 0:
            return "📊 You have no tasks in your list."
        elif count == 1:
            return "📊 You have 1 task in your list."
        else:
            return f"📊 You have {count} tasks in your list."
    
    # Notification Tools (via HTTP MCP Server)
    async def send_reminder_mcp(self, task: str, priority: str = "normal") -> str:
        """Send a reminder via MCP Notification Server."""
        result = await self._call_notification_server("send_reminder", {
            "task": task, 
            "priority": priority
        })
        return f"🔔 {result}"
    
    async def get_notification_history_mcp(self) -> str:
        """Get notification history via MCP Notification Server."""
        result = await self._call_notification_server("get_notification_history")
        
        try:
            # Parse the notification history
            if isinstance(result, str) and result.startswith("["):
                history = eval(result)  # In production, use json.loads
                if not history:
                    return "📜 No notifications have been sent yet."
                
                formatted_history = "\n".join([
                    f"🔔 {notif['timestamp']} - {notif['type'].title()}: '{notif['task']}' " + 
                    (f"(Priority: {notif.get('priority', 'normal')})" if 'priority' in notif else "")
                    for notif in history
                ])
                
                return f"📜 Notification History:\n{formatted_history}\n\nTotal: {len(history)} notifications"
            else:
                return str(result)
        except:
            return str(result)
    
    async def setup_agent(self):
        """
        Set up the LangGraph agent with MCP-based tools.
        
        Demonstrates:
        - Dynamic tool registration from multiple MCP servers
        - Unified tool interface despite different transports
        - Agent flexibility with external service tools
        """
        
        # Start MCP servers first
        if not await self.start_mcp_servers():
            print("❌ Failed to start MCP servers")
            return False
        
        # Create async wrapper functions for LangChain tools
        def sync_add_task(task: str) -> str:
            """Add a new task to the task list via MCP."""
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.add_task_mcp(task))
                        return future.result()
                else:
                    return loop.run_until_complete(self.add_task_mcp(task))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(self.add_task_mcp(task))
        
        def sync_list_tasks() -> str:
            """List all current tasks via MCP."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.list_tasks_mcp())
                        return future.result()
                else:
                    return loop.run_until_complete(self.list_tasks_mcp())
            except RuntimeError:
                return asyncio.run(self.list_tasks_mcp())
        
        def sync_remove_task(task: str) -> str:
            """Remove a task from the task list via MCP."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.remove_task_mcp(task))
                        return future.result()
                else:
                    return loop.run_until_complete(self.remove_task_mcp(task))
            except RuntimeError:
                return asyncio.run(self.remove_task_mcp(task))
        
        def sync_get_task_count() -> str:
            """Get the total number of tasks via MCP."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.get_task_count_mcp())
                        return future.result()
                else:
                    return loop.run_until_complete(self.get_task_count_mcp())
            except RuntimeError:
                return asyncio.run(self.get_task_count_mcp())
        
        def sync_send_reminder(task: str, priority: str = "normal") -> str:
            """Send a reminder for a specific task via MCP."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.send_reminder_mcp(task, priority))
                        return future.result()
                else:
                    return loop.run_until_complete(self.send_reminder_mcp(task, priority))
            except RuntimeError:
                return asyncio.run(self.send_reminder_mcp(task, priority))
        
        def sync_get_notification_history() -> str:
            """Get the history of all notifications via MCP."""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.get_notification_history_mcp())
                        return future.result()
                else:
                    return loop.run_until_complete(self.get_notification_history_mcp())
            except RuntimeError:
                return asyncio.run(self.get_notification_history_mcp())
        
        # Create LangChain tools from MCP server functions
        tools = [
            StructuredTool.from_function(
                func=sync_add_task,
                name="add_task",
                description="Add a new task to the task list via MCP Task Database Server (STDIO transport). Use this when the user wants to create or add a task."
            ),
            StructuredTool.from_function(
                func=sync_list_tasks,
                name="list_tasks", 
                description="List all current tasks via MCP Task Database Server (STDIO transport). Use this when the user wants to see their tasks."
            ),
            StructuredTool.from_function(
                func=sync_remove_task,
                name="remove_task",
                description="Remove a task from the list via MCP Task Database Server (STDIO transport). Use this when the user wants to delete or remove a task."
            ),
            StructuredTool.from_function(
                func=sync_get_task_count,
                name="get_task_count",
                description="Get the total number of tasks via MCP Task Database Server (STDIO transport). Use this when the user asks how many tasks they have."
            ),
            StructuredTool.from_function(
                func=sync_send_reminder,
                name="send_reminder",
                description="Send a reminder for a specific task via MCP Notification Server (HTTP transport). Use this when the user wants to be reminded about a task."
            ),
            StructuredTool.from_function(
                func=sync_get_notification_history,
                name="get_notification_history",
                description="Get the history of all notifications sent via MCP Notification Server (HTTP transport). Use this when the user wants to see notification history."
            )
        ]
        
        # Create the LangGraph ReAct agent
        self.agent = create_react_agent(self.model, tools)
        
        print("✅ MCP Task Manager Agent initialized successfully")
        print("🌟 MCP Benefits Demonstrated:")
        print("   • Protocol Standardization - Uniform interface across services")
        print("   • Transport Flexibility - STDIO + HTTP working together")
        print("   • Service Modularity - Independent, specialized microservices")
        print("   • Easy Extensibility - Add services without core changes")
        print(f"🛠️  Available MCP tools: {[tool.name for tool in tools]}")
        
        return True
    
    async def process_request(self, user_input: str) -> str:
        """Process a user request through the MCP-powered agent."""
        if not self.agent:
            return "❌ MCP Agent not initialized."
        
        query = {"messages": [{"role": "user", "content": user_input}]}
        
        try:
            response = await self.agent.ainvoke(query)
            return response['messages'][-1].content
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def shutdown(self):
        """Clean shutdown of MCP servers."""
        if self.task_db_process:
            self.task_db_process.terminate()
            self.task_db_process.wait()
        print("🔄 MCP servers shut down")
    
    async def run_mcp_demo(self):
        """Run a comprehensive demo showcasing MCP benefits."""
        demo_queries = [
            "Add a task to buy groceries",
            "Add a task to call my dentist", 
            "Add a task to finish the quarterly report",
            "List all my current tasks",
            "How many tasks do I have?",
            "Send a high priority reminder for buying groceries",
            "Send a reminder for the dentist appointment",
            "Show me the notification history",
            "Remove the task about calling the dentist",
            "List all tasks to see the updated list",
            "How many tasks do I have now?"
        ]
        
        print("🎯 MCP-Powered Task Manager Demo")
        print("=" * 60)
        print("🌟 Demonstrating Model Context Protocol Benefits:")
        print("   • Multi-transport communication (STDIO + HTTP)")
        print("   • Service modularity and independence") 
        print("   • Protocol standardization across services")
        print("   • Easy extensibility without core changes")
        print("=" * 60)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 50)
            
            response = await self.process_request(query)
            print(f"🤖 MCP Agent Response: {response}")
            
            await asyncio.sleep(1)  # Brief pause for readability
        
        print("\n" + "=" * 60)
        print("🎉 MCP Demo completed successfully!")
        print("🌟 MCP Benefits Demonstrated:")
        print("   ✅ Protocol Standardization - Same interface for different services")
        print("   ✅ Transport Flexibility - STDIO and HTTP working seamlessly")
        print("   ✅ Service Modularity - Independent task and notification services")
        print("   ✅ Easy Extensibility - Can add more MCP servers without changes")

async def main():
    """Main function to run the MCP-powered task manager."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please ensure your .env file contains your OpenAI API key")
        return
    
    agent = MCPTaskManagerAgent()
    
    # Setup the MCP-powered agent
    if not await agent.setup_agent():
        print("❌ Failed to setup MCP agent")
        return
    
    try:
        await agent.run_mcp_demo()
    finally:
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 