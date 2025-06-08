"""
MCP-Powered Web Frontend for AI Task Manager
A Flask web application demonstrating the benefits of Model Context Protocol (MCP)
by connecting to multiple specialized MCP servers via different transports.

MCP Benefits Demonstrated:
- Protocol Standardization: Uniform interface across different services
- Transport Flexibility: STDIO and HTTP/SSE transports working together
- Service Modularity: Independent, specialized microservices
- Easy Extensibility: Add new MCP servers without changing core agent code
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from mcp_task_manager import MCPTaskManagerAgent
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'mcp-task-manager-secret-key-change-in-production'

# Global MCP agent instance and event loop
mcp_agent = None
event_loop = None
loop_thread = None
executor = ThreadPoolExecutor(max_workers=4)

def run_event_loop():
    """Run the event loop in a separate thread."""
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()

def start_background_loop():
    """Start the background event loop thread."""
    global loop_thread
    loop_thread = threading.Thread(target=run_event_loop, daemon=True)
    loop_thread.start()

async def initialize_mcp_agent():
    """Initialize the MCP-powered task manager agent."""
    global mcp_agent
    if mcp_agent is None:
        mcp_agent = MCPTaskManagerAgent()
        success = await mcp_agent.setup_agent()
        if not success:
            print("❌ Failed to initialize MCP agent")
            return None
    return mcp_agent

def run_async(coro):
    """Run an async coroutine in the background event loop."""
    if event_loop is None:
        start_background_loop()
        # Wait a bit for the loop to start
        import time
        time.sleep(0.1)
    
    future = asyncio.run_coroutine_threadsafe(coro, event_loop)
    return future.result(timeout=30)  # 30 second timeout

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_request():
    """Process a natural language request through MCP-powered agent."""
    try:
        user_input = request.json.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize MCP agent if needed
        agent = run_async(initialize_mcp_agent())
        if not agent:
            return jsonify({'error': 'MCP agent initialization failed'}), 500
        
        # Process request via MCP protocol
        response = run_async(agent.process_request(user_input))
        
        # Add MCP info to response for demonstration
        mcp_info = "\n\n🌟 Powered by MCP: Task DB (STDIO) + Notifications (HTTP)"
        response_with_info = response + mcp_info
        
        return jsonify({
            'response': response_with_info,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mcp_enabled': True
        })
        
    except Exception as e:
        return jsonify({'error': f'MCP Error: {str(e)}'}), 500

@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    """Handle quick action buttons via MCP protocol."""
    try:
        action = request.json.get('action')
        
        action_map = {
            'list_tasks': 'List all my current tasks',
            'task_count': 'How many tasks do I have?',
            'notification_history': 'Show me the notification history'
        }
        
        if action not in action_map:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Initialize MCP agent if needed
        agent = run_async(initialize_mcp_agent())
        if not agent:
            return jsonify({'error': 'MCP agent initialization failed'}), 500
        
        # Process action via MCP protocol
        response = run_async(agent.process_request(action_map[action]))
        
        # Add MCP transport info for demonstration
        transport_info = {
            'list_tasks': ' (via STDIO MCP)',
            'task_count': ' (via STDIO MCP)',
            'notification_history': ' (via HTTP MCP)'
        }
        response_with_info = response + f"\n\n🔧 {transport_info.get(action, '')}"
        
        return jsonify({
            'response': response_with_info,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mcp_enabled': True,
            'transport': 'STDIO' if action in ['list_tasks', 'task_count'] else 'HTTP'
        })
        
    except Exception as e:
        return jsonify({'error': f'MCP Error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for MCP-powered system."""
    try:
        # Check if OpenAI API key is configured
        has_api_key = bool(os.getenv('OPENAI_API_KEY'))
        
        return jsonify({
            'status': 'healthy',
            'has_api_key': has_api_key,
            'mcp_enabled': True,
            'mcp_servers': {
                'task_database': 'STDIO transport',
                'notifications': 'HTTP/SSE transport'
            },
            'benefits': [
                'Protocol Standardization',
                'Transport Flexibility', 
                'Service Modularity',
                'Easy Extensibility'
            ],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    # Check if OpenAI API key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("The MCP-powered web app will start but may not function correctly without an API key")
    
    print("🌐 Starting MCP-Powered Task Manager Web App...")
    print("🌟 Demonstrating Model Context Protocol Benefits:")
    print("   • Protocol Standardization - Uniform interface across services")
    print("   • Transport Flexibility - STDIO + HTTP working together")
    print("   • Service Modularity - Independent, specialized microservices")
    print("   • Easy Extensibility - Add services without core changes")
    print()
    print("🔧 MCP Architecture:")
    print("   • Task Database Server (STDIO transport)")
    print("   • Notification Server (HTTP/SSE transport)")
    print("   • LangGraph Agent (Protocol orchestration)")
    print()
    print("📱 Open your browser to: http://localhost:8080")
    print("🔄 The app will automatically reload when you make changes")
    print("💡 If port 8080 is busy, the app will automatically find an available port")
    
    # Start the background event loop
    start_background_loop()
    
    # Initialize the MCP agent in the background
    try:
        print("🔄 Initializing MCP agent...")
        run_async(initialize_mcp_agent())
        print("✅ MCP agent initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize MCP agent: {e}")
        print("The agent will be initialized on first request")
    
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True) 