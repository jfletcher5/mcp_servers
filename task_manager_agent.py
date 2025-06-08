"""
AI-Powered Task Manager Agent
Uses LangGraph to create an intelligent agent that manages tasks by coordinating
between Task Database and Notification MCP servers.
"""

import asyncio
import os
from typing import List, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TaskManagerAgent:
    """
    Main class for the AI-powered task manager that coordinates between
    task database and notification services using LangGraph.
    """
    
    def __init__(self):
        """Initialize the task manager agent with LLM and MCP clients."""
        # Initialize the OpenAI language model
        # Using GPT-4 for better reasoning capabilities
        self.model = ChatOpenAI(
            model="gpt-4",
            temperature=0.1  # Low temperature for more consistent responses
        )
        
        # Will be initialized in setup_mcp_clients()
        self.client = None
        self.agent = None
        
    async def setup_mcp_clients(self):
        """
        Set up MCP clients for task database and notification services.
        This method configures the connections to both MCP servers.
        """
        # Configure MCP servers with their respective transports
        server_config = {
            "task_db": {
                "command": "python",
                "args": ["task_db_server.py"],
                "transport": "stdio",  # Standard input/output transport
            },
            "notification": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",  # Server-sent events transport
            }
        }
        
        # Initialize the multi-server MCP client
        self.client = MultiServerMCPClient(server_config)
        
        # Get available tools from all configured MCP servers
        tools = await self.client.get_tools()
        
        # Create the LangGraph ReAct agent with the LLM and MCP tools
        self.agent = create_react_agent(self.model, tools)
        
        print("✅ MCP clients initialized successfully")
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        
    async def process_user_request(self, user_input: str) -> str:
        """
        Process a user request through the LangGraph agent.
        
        Args:
            user_input (str): The user's natural language request
            
        Returns:
            str: The agent's response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup_mcp_clients() first.")
        
        # Format the user input for the agent
        query = {"messages": [{"role": "user", "content": user_input}]}
        
        try:
            # Process the query through the LangGraph agent
            response = await self.agent.ainvoke(query)
            
            # Extract the agent's response from the message chain
            agent_response = response['messages'][-1].content
            
            return agent_response
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    async def run_demo_queries(self):
        """
        Run a series of demo queries to showcase the task manager capabilities.
        This demonstrates the full workflow of task management.
        """
        demo_queries = [
            "Add a task to buy groceries tomorrow",
            "Add a task to call the dentist for an appointment",
            "Add a task to review the quarterly reports",
            "List all current tasks",
            "Get the total number of tasks",
            "Send a reminder for buying groceries with high priority",
            "Send a task completion notice for calling the dentist",
            "Get the notification history",
            "Schedule a daily summary notification",
            "Remove the task about calling the dentist",
            "List all tasks again to confirm removal"
        ]
        
        print("🚀 Starting Task Manager Demo")
        print("=" * 50)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 40)
            
            try:
                response = await self.process_user_request(query)
                print(f"🤖 Response: {response}")
                
                # Small delay between queries for readability
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
    
    async def interactive_mode(self):
        """
        Run the task manager in interactive mode where users can input commands.
        """
        print("🎯 Task Manager Interactive Mode")
        print("Enter your task management requests (type 'quit' to exit)")
        print("Examples:")
        print("  - 'Add a task to water the plants'")
        print("  - 'List all tasks'")
        print("  - 'Send a reminder for watering plants'")
        print("  - 'Get notification history'")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Agent: ", end="")
                response = await self.process_user_request(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def main():
    """
    Main function to run the task manager agent.
    Supports both demo mode and interactive mode.
    """
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your-key-here")
        return
    
    # Initialize the task manager agent
    agent = TaskManagerAgent()
    
    try:
        # Set up MCP client connections
        await agent.setup_mcp_clients()
        
        # Ask user for mode preference
        print("\nChoose mode:")
        print("1. Demo mode (run predefined queries)")
        print("2. Interactive mode (enter your own queries)")
        
        while True:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == "1":
                await agent.run_demo_queries()
                break
            elif choice == "2":
                await agent.interactive_mode()
                break
            else:
                print("Please enter 1 or 2")
        
    except Exception as e:
        print(f"❌ Error initializing task manager: {str(e)}")
        print("Make sure the notification server is running:")
        print("python notification_server.py")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main()) 