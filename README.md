# AI-Powered Task Manager with LangGraph and MCP

A Python backend project that demonstrates an intelligent task management system using LangGraph agents and Model Context Protocol (MCP) servers. The system coordinates between task storage and notification services to provide a comprehensive task management experience.

## 🎯 Project Overview

This project showcases:
- **LangGraph Agent**: An AI agent that processes natural language requests for task management
- **MCP Servers**: Modular services for task database and notifications
- **Intelligent Coordination**: Seamless integration between different services using MCP protocol
- **Interactive Interface**: Both demo and interactive modes for user interaction

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   User Input    │    │   LangGraph      │    │   MCP Servers    │
│   (Natural      │───▶│   Agent          │───▶│                  │
│   Language)     │    │   (GPT-4)        │    │  • Task DB       │
└─────────────────┘    └──────────────────┘    │  • Notifications │
                                               └──────────────────┘
```

## 📋 Features

### Task Database Server (`task_db_server.py`)
- **Add Tasks**: Store new tasks in the database
- **List Tasks**: Retrieve all current tasks
- **Remove Tasks**: Delete specific tasks
- **Task Count**: Get total number of tasks
- **Transport**: STDIO for direct communication

### Notification Server (`notification_server.py`)
- **Send Reminders**: Create task reminders with priority levels
- **Completion Notices**: Notify when tasks are completed
- **Notification History**: Track all sent notifications
- **Daily Summaries**: Schedule recurring notifications
- **Transport**: HTTP/SSE for web-based communication

### AI Agent (`task_manager_agent.py`)
- **Natural Language Processing**: Understand user requests in plain English
- **Service Coordination**: Intelligently route requests to appropriate MCP servers
- **Demo Mode**: Predefined queries showcasing all features
- **Interactive Mode**: Real-time user interaction
- **Error Handling**: Robust error management and user feedback

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- OpenAI API key
- Git (optional, for cloning)

### Installation

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd mcp_servers
   
   # Or download and extract the project files
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```plaintext
   OPENAI_API_KEY=your-openai-api-key-here
   ```
   
   > **Note**: You can get an OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)

### Running the Project

#### Option 1: Quick Start (Demo Mode)

1. **Start the Notification Server** (Terminal 1):
   ```bash
   python notification_server.py
   ```

2. **Run the Task Manager Agent** (Terminal 2):
   ```bash
   python task_manager_agent.py
   ```
   
3. **Choose Demo Mode** when prompted (enter `1`)

#### Option 2: Interactive Mode

1. **Start the Notification Server** (Terminal 1):
   ```bash
   python notification_server.py
   ```

2. **Run the Task Manager Agent** (Terminal 2):
   ```bash
   python task_manager_agent.py
   ```
   
3. **Choose Interactive Mode** when prompted (enter `2`)

4. **Start chatting** with the agent using natural language:
   ```
   🗣️  You: Add a task to water the plants
   🤖 Agent: Task 'water the plants' added successfully.
   
   🗣️  You: List all my tasks
   🤖 Agent: The current tasks are: ['water the plants']
   
   🗣️  You: Send a reminder for watering plants
   🤖 Agent: [2024-01-15 14:30:22] Reminder sent for task: 'water the plants' (Priority: normal)
   ```

## 📖 Example Usage

### Demo Mode Output
```
🚀 Starting Task Manager Demo
==================================================

📝 Query 1: Add a task to buy groceries tomorrow
----------------------------------------
🤖 Response: Task 'buy groceries tomorrow' added successfully.

📝 Query 2: List all current tasks
----------------------------------------
🤖 Response: The current tasks are: ['buy groceries tomorrow']

📝 Query 3: Send a reminder for buying groceries with high priority
----------------------------------------
🤖 Response: [2024-01-15 14:30:22] Reminder sent for task: 'buy groceries tomorrow' (Priority: high)
```

### Natural Language Commands
The agent understands various ways to express the same request:

- **Adding Tasks**:
  - "Add a task to call mom"
  - "I need to remember to call mom"
  - "Create a task for calling mom"

- **Listing Tasks**:
  - "Show me all tasks"
  - "What tasks do I have?"
  - "List my current tasks"

- **Sending Reminders**:
  - "Remind me about calling mom"
  - "Send a reminder for the mom task"
  - "Set up a reminder to call mom"

## 🛠️ Development

### Project Structure
```
mcp_servers/
├── task_db_server.py          # Task database MCP server
├── notification_server.py     # Notification MCP server  
├── task_manager_agent.py      # Main LangGraph agent
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

### Adding New Features

#### Adding New Task Operations
1. Add a new tool function to `task_db_server.py`
2. Use the `@mcp.tool()` decorator
3. Include proper documentation
4. The agent will automatically discover and use the new tool

#### Adding New Notification Types
1. Add a new tool function to `notification_server.py`
2. Update the notification history structure if needed
3. Test with the agent to ensure proper integration

### Customization Options

#### Changing the AI Model
In `task_manager_agent.py`, modify the model initialization:
```python
self.model = ChatOpenAI(
    model="gpt-3.5-turbo",  # or "gpt-4-turbo"
    temperature=0.1
)
```

#### Modifying Server Ports
In `notification_server.py`, change the port:
```python
mcp.run(transport="sse", port=8001)  # Change from 8000 to 8001
```

And update the agent configuration in `task_manager_agent.py`:
```python
"notification": {
    "url": "http://localhost:8001/sse",  # Update port here too
    "transport": "sse",
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure you have created a `.env` file with your OpenAI API key
   - Check that the file is in the project root directory

2. **"Error initializing task manager"**
   - Make sure the notification server is running before starting the agent
   - Check that port 8000 is not being used by another application

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using Python 3.11 or higher

4. **MCP Connection Issues**
   - Verify both servers are running
   - Check terminal outputs for specific error messages
   - Try restarting both servers

### Getting Help

If you encounter issues:

1. Check the terminal outputs for detailed error messages
2. Ensure all prerequisites are met
3. Verify your OpenAI API key is valid and has credits
4. Try the demo mode first before interactive mode

## 🚀 Next Steps

This project provides a foundation for building more sophisticated task management systems. Potential enhancements include:

- **Persistent Storage**: Replace in-memory storage with a real database
- **Web Interface**: Add a web-based UI for task management
- **Advanced Scheduling**: Implement complex task scheduling and recurring tasks
- **Team Collaboration**: Multi-user support and task sharing
- **Integration**: Connect with external services (calendar, email, etc.)
- **Analytics**: Task completion tracking and productivity insights

## 📜 License

This project is provided as-is for educational and demonstration purposes. Feel free to modify and extend it for your own use cases.


