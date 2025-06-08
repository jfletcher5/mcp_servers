"""
Simplified AI-Powered Task Manager Agent
Uses only the task database via STDIO transport to avoid HTTP transport issues.
This version focuses on the core functionality first.
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

class SimpleTaskManagerAgent:
    """
    Simplified task manager that uses only the task database MCP server.
    This version avoids HTTP transport issues by focusing on STDIO transport only.
    """
    
    def __init__(self):
        """Initialize the simplified task manager agent."""
        # Initialize the OpenAI language model
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for faster responses
            temperature=0.1
        )
        
        # Will be initialized in setup_mcp_clients()
        self.client = None
        self.agent = None
        
    async def setup_mcp_clients(self):
        """
        Set up MCP client for task database only.
        This simplified version uses only STDIO transport.
        """
        # Configure only the task database MCP server
        server_config = {
            "task_db": {
                "command": "python",
                "args": ["task_db_server.py"],
                "transport": "stdio",  # Standard input/output transport only
            }
        }
        
        try:
            # Initialize the MCP client
            self.client = MultiServerMCPClient(server_config)
            
            # Get available tools from the task database server
            tools = await self.client.get_tools()
            
            # Create the LangGraph ReAct agent with the LLM and MCP tools
            self.agent = create_react_agent(self.model, tools)
            
            print("✅ Task Database MCP client initialized successfully")
            print(f"📋 Available tools: {[tool.name for tool in tools]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up MCP client: {e}")
            return False
        
    async def process_user_request(self, user_input: str) -> str:
        """
        Process a user request through the LangGraph agent.
        
        Args:
            user_input (str): The user's natural language request
            
        Returns:
            str: The agent's response
        """
        if not self.agent:
            return "❌ Agent not initialized. Please run setup first."
        
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
    
    async def run_simple_demo(self):
        """
        Run a simplified demo focusing on task database operations.
        """
        demo_queries = [
            "Add a task to buy groceries",
            "Add a task to call mom",
            "Add a task to finish the project report", 
            "List all my current tasks",
            "How many tasks do I have?",
            "Remove the task about calling mom",
            "List all tasks again to see the updated list"
        ]
        
        print("🚀 Starting Simple Task Manager Demo")
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
        print("✅ Simple demo completed!")
    
    async def interactive_mode(self):
        """
        Run the simplified task manager in interactive mode.
        """
        print("🎯 Simple Task Manager Interactive Mode")
        print("Focus: Task database operations (add, list, remove, count)")
        print("Enter your task management requests (type 'quit' to exit)")
        print("Examples:")
        print("  - 'Add a task to water the plants'")
        print("  - 'List all tasks'")
        print("  - 'Remove the task about watering plants'")
        print("  - 'How many tasks do I have?'")
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
    Main function to run the simplified task manager agent.
    """
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please ensure your .env file contains your OpenAI API key:")
        print("OPENAI_API_KEY=your-key-here")
        return
    
    # Initialize the simple task manager agent
    agent = SimpleTaskManagerAgent()
    
    try:
        # Set up MCP client connection
        setup_success = await agent.setup_mcp_clients()
        
        if not setup_success:
            print("❌ Failed to initialize MCP client. Please check the error above.")
            return
        
        # Ask user for mode preference
        print("\nChoose mode:")
        print("1. Simple demo (task database operations)")
        print("2. Interactive mode (chat with the task manager)")
        
        while True:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == "1":
                await agent.run_simple_demo()
                break
            elif choice == "2":
                await agent.interactive_mode()
                break
            else:
                print("Please enter 1 or 2")
        
    except Exception as e:
        print(f"❌ Error running task manager: {str(e)}")
        print("Check the error details above and try again.")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main()) 