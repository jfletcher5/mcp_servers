"""
Web Frontend for AI-Powered Task Manager
A Flask web application that provides a beautiful interface for the task manager.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from task_manager_working import WorkingTaskManagerAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'task-manager-secret-key-change-in-production'

# Global agent instance
task_agent = None

def initialize_agent():
    """Initialize the task manager agent."""
    global task_agent
    if task_agent is None:
        task_agent = WorkingTaskManagerAgent()
        task_agent.setup_agent()
    return task_agent

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_request():
    """Process a natural language request from the user."""
    try:
        agent = initialize_agent()
        user_input = request.json.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the request through the agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(agent.process_request(user_input))
        finally:
            loop.close()
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    """Handle quick action buttons."""
    try:
        agent = initialize_agent()
        action = request.json.get('action')
        
        action_map = {
            'list_tasks': 'List all my current tasks',
            'task_count': 'How many tasks do I have?',
            'notification_history': 'Show me the notification history'
        }
        
        if action not in action_map:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Process the action
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(agent.process_request(action_map[action]))
        finally:
            loop.close()
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check if OpenAI API key is configured
        has_api_key = bool(os.getenv('OPENAI_API_KEY'))
        
        return jsonify({
            'status': 'healthy',
            'has_api_key': has_api_key,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    # Check if OpenAI API key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("The web app will start but may not function correctly without an API key")
    
    print("🌐 Starting Task Manager Web App...")
    print("📱 Open your browser to: http://localhost:8080")
    print("🔄 The app will automatically reload when you make changes")
    print("💡 If port 8080 is also busy, the app will automatically find an available port")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 