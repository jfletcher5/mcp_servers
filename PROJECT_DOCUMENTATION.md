# MCP-Powered AI Task Manager

## 🌟 Project Overview

This project demonstrates the power and benefits of the **Model Context Protocol (MCP)** by building an intelligent task management system that connects multiple specialized services through different transport mechanisms. The system showcases how MCP enables protocol standardization, transport flexibility, service modularity, and easy extensibility.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Frontend (Flask)                     │
│                  http://localhost:8080                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                MCP Task Manager Agent                       │
│              (LangGraph + OpenAI GPT)                      │
└─────────────┬───────────────────────────┬───────────────────┘
              │                           │
     ┌────────▼────────┐         ┌────────▼────────┐
     │ Task Database   │         │  Notification   │
     │    Server       │         │     Server      │
     │ (STDIO/JSON-RPC)│         │   (HTTP/REST)   │
     │  Port: N/A      │         │  Port: 8000     │
     └─────────────────┘         └─────────────────┘
```

## 🔧 Core Components

### 1. **Web Frontend** (`web_app.py`)
- **Technology**: Flask web application
- **Purpose**: Provides a modern chat-based UI for interacting with the AI task manager
- **Features**:
  - Real-time chat interface
  - Quick action buttons
  - Health monitoring
  - Responsive design

### 2. **MCP Task Manager Agent** (`mcp_task_manager.py`)
- **Technology**: LangGraph ReAct agent with OpenAI GPT-4o-mini
- **Purpose**: Orchestrates communication between frontend and MCP servers
- **Key Features**:
  - Multi-transport MCP communication
  - Async event loop management
  - Dynamic tool registration
  - Error handling and server restart capability

### 3. **Task Database Server** (`task_db_server.py`)
- **Transport**: STDIO (Standard Input/Output)
- **Protocol**: JSON-RPC 2.0
- **Purpose**: Manages task storage and retrieval operations
- **Tools Available**:
  - `add_task(task: str)` - Add new tasks
  - `list_tasks()` - Retrieve all tasks
  - `remove_task(task: str)` - Delete specific tasks
  - `get_task_count()` - Get total task count

### 4. **Notification Server** (`notification_server.py`)
- **Transport**: HTTP/REST API
- **Protocol**: RESTful JSON API
- **Purpose**: Handles notification and reminder services
- **Endpoints**:
  - `POST /call/send_reminder` - Send task reminders
  - `POST /call/send_task_completion_notice` - Task completion notifications
  - `GET /call/get_notification_history` - Retrieve notification history
  - `POST /call/schedule_daily_summary` - Schedule daily summaries

## 🌟 MCP Benefits Demonstrated

### 1. **Protocol Standardization**
- Uniform interface across different services regardless of implementation
- Consistent tool calling mechanism for both STDIO and HTTP transports
- Standardized JSON-RPC communication protocol

### 2. **Transport Flexibility**
- **STDIO Transport**: Direct process communication for high-performance task operations
- **HTTP Transport**: Web-based API for notification services
- Same agent can communicate with both transport types seamlessly

### 3. **Service Modularity**
- Each MCP server is an independent microservice
- Services can be developed, deployed, and scaled independently
- Clear separation of concerns (task management vs. notifications)

### 4. **Easy Extensibility**
- Adding new MCP servers requires no changes to the core agent
- New tools are automatically available to the AI agent
- Support for multiple programming languages and technologies

## 🚀 Setup and Installation

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the project root:
```env
# Required: OpenAI API key for the AI agent
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Additional configuration
DEBUG=False
```

### Dependencies (`requirements.txt`)
```
# Core LangGraph and AI dependencies
langgraph>=0.2.0
langchain-openai>=0.2.0
langchain>=0.3.0

# Environment and utility dependencies
python-dotenv>=1.0.0

# HTTP client for communication
aiohttp>=3.9.0

# Web app dependencies
flask>=2.3.0
```

## 🏃‍♂️ Running the System

### Method 1: All-in-One Web Application
```bash
# Start the complete system (recommended)
python web_app.py
```

This command will:
1. Start the background event loop
2. Initialize the MCP Task Manager Agent
3. Launch both MCP servers (Task DB + Notification)
4. Start the web interface on http://localhost:8080

### Method 2: Manual Component Startup
```bash
# Terminal 1: Start Task Database Server
python task_db_server.py

# Terminal 2: Start Notification Server  
python notification_server.py

# Terminal 3: Start Web Application
python web_app.py
```

### Method 3: Standalone Demo
```bash
# Run the MCP demo without web interface
python mcp_task_manager.py
```

## 🌐 Web Interface Usage

### Accessing the Application
1. Open your browser to: `http://localhost:8080`
2. You'll see a modern chat interface with quick action buttons
3. The status indicator shows "Online" when all services are running

### Quick Actions
- **List Tasks**: View all current tasks
- **Task Count**: Get the total number of tasks
- **Notifications**: View notification history

### Chat Commands
You can interact naturally with the AI agent using commands like:
- "Add a task to water my plants"
- "Show me all my tasks"
- "Send a high priority reminder for buying groceries"
- "How many tasks do I have?"
- "Remove the task about calling the dentist"

## 🔌 API Endpoints

### Web Application APIs

#### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "has_api_key": true,
  "mcp_enabled": true,
  "mcp_servers": {
    "task_database": "STDIO transport",
    "notifications": "HTTP/SSE transport"
  },
  "benefits": ["Protocol Standardization", "Transport Flexibility", "Service Modularity", "Easy Extensibility"],
  "timestamp": "2025-06-08 18:58:08"
}
```

#### Process User Request
```http
POST /api/process
Content-Type: application/json

{
  "message": "Add a task to water my plants"
}
```

#### Quick Actions
```http
POST /api/quick-action
Content-Type: application/json

{
  "action": "list_tasks" | "task_count" | "notification_history"
}
```

### Task Database Server (STDIO)

The Task Database Server communicates via JSON-RPC over STDIO:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add_task",
    "arguments": {"task": "Water the plants"}
  }
}
```

### Notification Server (HTTP)

#### Send Reminder
```http
POST http://localhost:8000/call/send_reminder
Content-Type: application/json

{
  "task": "Water the plants",
  "priority": "high"
}
```

#### Get Notification History
```http
POST http://localhost:8000/call/get_notification_history
```

## 🔍 Technical Deep Dive

### Event Loop Management
The system uses a sophisticated event loop architecture to handle async operations in a Flask web application:

```python
# Background event loop for async operations
def run_event_loop():
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()

# Thread-safe async execution
def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, event_loop)
    return future.result(timeout=30)
```

### STDIO Communication Protocol
The Task Database Server uses a custom JSON-RPC implementation:

```python
# Request format
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {...}
  }
}

# Response format
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{"type": "text", "text": "response"}]
  }
}
```

### Error Handling and Recovery
The system includes robust error handling:
- **Server Health Monitoring**: Automatic detection of failed servers
- **Process Restart**: Automatic restart of STDIO servers on communication failure
- **Timeout Protection**: 5-second timeouts on STDIO communication
- **Graceful Degradation**: Continues operation even if one server fails

## 🧪 Testing the System

### Manual Testing
1. **Basic Task Operations**:
   ```
   User: "Add a task to buy groceries"
   System: ✅ Task 'buy groceries' added successfully.
   
   User: "List all my tasks"
   System: 📝 Your current tasks:
   1. buy groceries
   Total: 1 tasks
   ```

2. **Notification Services**:
   ```
   User: "Send a high priority reminder for buying groceries"
   System: 🔔 [2025-06-08 18:57:30] Reminder sent for task: 'buying groceries' (Priority: high)
   ```

### Automated Testing
```bash
# Test Task Database Server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add_task", "arguments": {"task": "Test task"}}}' | python task_db_server.py

# Test Notification Server
curl -X POST http://localhost:8000/call/send_reminder \
     -H "Content-Type: application/json" \
     -d '{"task": "Test reminder", "priority": "high"}'

# Test Web Application
curl -X POST http://localhost:8080/api/process \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to test the system"}'
```

## 📊 Monitoring and Debugging

### Logs and Output
The system provides comprehensive logging:
- **Server Startup**: Detailed initialization logs
- **MCP Communication**: Request/response logging
- **Error Details**: Specific error messages with context
- **Performance Metrics**: Timing information for operations

### Health Monitoring
- **Process Health**: Automatic detection of failed subprocesses
- **Communication Health**: Timeout-based health checks
- **Service Availability**: Health endpoints for each service

## 🛠️ Customization and Extension

### Adding New MCP Servers
1. **Create Server Implementation**:
   ```python
   # new_service_server.py
   class NewServiceServer:
       def __init__(self):
           self.app = Flask(__name__)
           self.setup_routes()
       
       @self.app.route('/call/<tool_name>', methods=['POST'])
       def call_tool(self, tool_name):
           # Implement your tool logic
           pass
   ```

2. **Register with Agent**:
   ```python
   # In mcp_task_manager.py
   async def _call_new_service_server(self, method: str, params: Dict = None) -> str:
       # Implement communication logic
       pass
   
   # Add to tool registration
   tools.append(StructuredTool.from_function(
       func=sync_new_service_tool,
       name="new_service_tool",
       description="Description of the new tool"
   ))
   ```

### Modifying Existing Services
Each service is independently modifiable:
- **Task Database**: Modify `task_db_server.py` to add new task operations
- **Notifications**: Extend `notification_server.py` with new notification types
- **Agent Logic**: Update `mcp_task_manager.py` to change AI behavior

## 🔒 Security Considerations

### Current Implementation
- **Environment Variables**: Secure API key storage
- **Local Development**: All services run locally
- **No Authentication**: Simplified for demonstration

### Production Recommendations
- **API Authentication**: Add JWT or API key authentication
- **HTTPS**: Use TLS for all HTTP communication
- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Implement request rate limiting
- **Process Isolation**: Run MCP servers in containers

## 🐛 Troubleshooting

### Common Issues

#### "AI is thinking" Hangs Forever
- **Cause**: Event loop conflicts or server communication failure
- **Solution**: Restart the web application, check server logs

#### Task Database Server Not Responding
- **Cause**: STDIO communication issues
- **Solution**: The system automatically restarts failed servers

#### Notification Server Unavailable
- **Cause**: Port 8000 already in use
- **Solution**: Kill existing processes or change port in configuration

#### OpenAI API Errors
- **Cause**: Missing or invalid API key
- **Solution**: Check `.env` file and API key validity

### Debug Commands
```bash
# Check running processes
ps aux | grep python

# Kill all project processes
pkill -f web_app.py
pkill -f task_db_server.py
pkill -f notification_server.py

# Test individual components
python task_db_server.py  # Should wait for STDIN input
python notification_server.py  # Should start HTTP server
curl http://localhost:8000/health  # Should return health status
```

## 📈 Performance Characteristics

### Latency
- **HTTP Transport**: ~50-100ms per request
- **STDIO Transport**: ~10-20ms per request
- **AI Processing**: ~1-3 seconds per request

### Scalability
- **Concurrent Users**: Limited by Flask development server
- **Task Storage**: In-memory (lost on restart)
- **Notification History**: In-memory (limited by RAM)

### Production Improvements
- **Database**: Replace in-memory storage with persistent database
- **Caching**: Add Redis caching for frequent operations
- **Load Balancing**: Use WSGI server with multiple workers
- **Monitoring**: Add application performance monitoring

## 🎯 Future Enhancements

### Planned Features
1. **Persistent Storage**: Database integration for tasks and notifications
2. **User Authentication**: Multi-user support with authentication
3. **Real-time Updates**: WebSocket support for live updates
4. **Mobile App**: React Native or Flutter mobile application
5. **Advanced AI**: Custom LLM fine-tuning for task management

### MCP Protocol Extensions
1. **Additional Transports**: WebSocket, gRPC support
2. **Service Discovery**: Automatic discovery of MCP servers
3. **Load Balancing**: Multiple server instances per service
4. **Monitoring**: Built-in metrics and observability

## 📚 Resources and References

### MCP (Model Context Protocol)
- **Documentation**: Official MCP specification and guides
- **Examples**: Community examples and best practices
- **Transport Types**: STDIO, HTTP, WebSocket, SSE

### Dependencies
- **LangGraph**: Agent framework for complex workflows
- **LangChain**: LLM integration and tool management
- **OpenAI**: GPT model API for natural language processing
- **Flask**: Python web framework for the frontend
- **aiohttp**: Async HTTP client for server communication

### Development Tools
- **Python 3.8+**: Programming language runtime
- **pip**: Package management
- **curl**: HTTP testing tool
- **Browser**: Modern web browser for UI testing

---

## 📄 License

This project is provided for educational and demonstration purposes. Please ensure you have appropriate licenses for all dependencies and API services used.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

For questions or support, please create an issue in the project repository. 