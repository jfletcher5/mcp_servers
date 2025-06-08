"""
Working AI-Powered Task Manager
This version uses direct tool integration with LangGraph instead of MCP protocol
to demonstrate the core functionality without transport complications.
"""

import asyncio
import os
from typing import List, Dict, Any
from langchain.tools import BaseTool
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Global task storage (in production this would be a database)
task_storage = []
notification_history = []

class TaskManagerTools:
    """
    Task management tools that work directly with LangGraph.
    These replace the MCP servers with direct function calls.
    """
    
    @staticmethod
    def add_task(task: str) -> str:
        """
        Add a new task to the task list.
        
        Args:
            task (str): The task description to add
            
        Returns:
            str: Confirmation message
        """
        task_storage.append(task)
        return f"✅ Task '{task}' added successfully. You now have {len(task_storage)} tasks."
    
    @staticmethod
    def list_tasks() -> str:
        """
        List all current tasks.
        
        Returns:
            str: Formatted list of all tasks
        """
        if not task_storage:
            return "📝 No tasks found. Your task list is empty!"
        
        task_list = "\n".join([f"{i+1}. {task}" for i, task in enumerate(task_storage)])
        return f"📝 Your current tasks:\n{task_list}\n\nTotal: {len(task_storage)} tasks"
    
    @staticmethod
    def remove_task(task: str) -> str:
        """
        Remove a task from the task list.
        
        Args:
            task (str): The task description to remove (partial match)
            
        Returns:
            str: Confirmation message
        """
        # Find tasks that contain the search term
        matching_tasks = [t for t in task_storage if task.lower() in t.lower()]
        
        if not matching_tasks:
            return f"❌ No tasks found matching '{task}'. Current tasks: {task_storage}"
        
        # Remove the first matching task
        task_to_remove = matching_tasks[0]
        task_storage.remove(task_to_remove)
        return f"✅ Removed task: '{task_to_remove}'. You now have {len(task_storage)} tasks remaining."
    
    @staticmethod
    def get_task_count() -> str:
        """
        Get the total number of tasks.
        
        Returns:
            str: Task count message
        """
        count = len(task_storage)
        if count == 0:
            return "📊 You have no tasks in your list."
        elif count == 1:
            return "📊 You have 1 task in your list."
        else:
            return f"📊 You have {count} tasks in your list."
    
    @staticmethod
    def send_reminder(task: str, priority: str = "normal") -> str:
        """
        Send a reminder for a specific task.
        
        Args:
            task (str): The task to remind about
            priority (str): Priority level (low, normal, high)
            
        Returns:
            str: Confirmation message
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        reminder = {
            "task": task,
            "priority": priority,
            "timestamp": timestamp,
            "type": "reminder"
        }
        notification_history.append(reminder)
        
        return f"🔔 [{timestamp}] Reminder sent for task: '{task}' (Priority: {priority})"
    
    @staticmethod
    def get_notification_history() -> str:
        """
        Get the history of all notifications.
        
        Returns:
            str: Formatted notification history
        """
        if not notification_history:
            return "📜 No notifications have been sent yet."
        
        history = "\n".join([
            f"🔔 {notif['timestamp']} - {notif['type'].title()}: '{notif['task']}' (Priority: {notif.get('priority', 'normal')})"
            for notif in notification_history
        ])
        
        return f"📜 Notification History:\n{history}\n\nTotal: {len(notification_history)} notifications"

class WorkingTaskManagerAgent:
    """
    Working task manager agent using direct LangGraph tool integration.
    """
    
    def __init__(self):
        """Initialize the working task manager agent."""
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        )
        self.agent = None
        
    def setup_agent(self):
        """Set up the LangGraph agent with direct tools."""
        
        # Create LangChain tools from our task manager functions
        tools = [
            StructuredTool.from_function(
                func=TaskManagerTools.add_task,
                name="add_task",
                description="Add a new task to the task list. Use this when the user wants to create or add a task."
            ),
            StructuredTool.from_function(
                func=TaskManagerTools.list_tasks,
                name="list_tasks", 
                description="List all current tasks. Use this when the user wants to see their tasks."
            ),
            StructuredTool.from_function(
                func=TaskManagerTools.remove_task,
                name="remove_task",
                description="Remove a task from the list. Use this when the user wants to delete or remove a task."
            ),
            StructuredTool.from_function(
                func=TaskManagerTools.get_task_count,
                name="get_task_count",
                description="Get the total number of tasks. Use this when the user asks how many tasks they have."
            ),
            StructuredTool.from_function(
                func=TaskManagerTools.send_reminder,
                name="send_reminder",
                description="Send a reminder for a specific task. Use this when the user wants to be reminded about a task."
            ),
            StructuredTool.from_function(
                func=TaskManagerTools.get_notification_history,
                name="get_notification_history",
                description="Get the history of all notifications sent. Use this when the user wants to see notification history."
            )
        ]
        
        # Create the LangGraph ReAct agent
        self.agent = create_react_agent(self.model, tools)
        
        print("✅ Working Task Manager Agent initialized successfully")
        print(f"🛠️  Available tools: {[tool.name for tool in tools]}")
        
        return True
    
    async def process_request(self, user_input: str) -> str:
        """Process a user request through the agent."""
        if not self.agent:
            return "❌ Agent not initialized."
        
        query = {"messages": [{"role": "user", "content": user_input}]}
        
        try:
            response = await self.agent.ainvoke(query)
            return response['messages'][-1].content
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def run_demo(self):
        """Run a comprehensive demo of the task manager."""
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
        
        print("🎯 Working Task Manager Demo")
        print("=" * 50)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 40)
            
            response = await self.process_request(query)
            print(f"🤖 Response: {response}")
            
            await asyncio.sleep(0.5)  # Brief pause for readability
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        print("🎯 Working Task Manager - Interactive Mode")
        print("Talk to me naturally about your tasks!")
        print("Examples:")
        print("  - 'Add a task to water the plants'")
        print("  - 'Show me all my tasks'")
        print("  - 'Remind me about watering plants'")
        print("  - 'Remove the plant task'")
        print("  - 'How many tasks do I have?'")
        print("\nType 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Thanks for using the task manager!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Agent: ", end="")
                response = await self.process_request(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def main():
    """Main function."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please ensure your .env file contains your OpenAI API key")
        return
    
    agent = WorkingTaskManagerAgent()
    
    # Setup the agent
    agent.setup_agent()
    
    # Choose mode
    print("\nChoose mode:")
    print("1. Demo mode (showcase all features)")
    print("2. Interactive mode (natural conversation)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "1":
            await agent.run_demo()
            break
        elif choice == "2":
            await agent.interactive_mode()
            break
        else:
            print("Please enter 1 or 2")

if __name__ == "__main__":
    asyncio.run(main()) 