#!/usr/bin/env python3
"""
Setup script for AI-Powered Task Manager with LangGraph and MCP
This script helps users validate their environment and create necessary configuration files.
"""

import os
import sys
import subprocess
import pkg_resources

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        if version.minor < 11:
            print("ℹ️  Note: Python 3.11+ is recommended, but 3.10 should work")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("⚠️  Please install Python 3.10 or higher")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'langchain-mcp-adapters',
        'langgraph', 
        'langchain-openai',
        'mcp',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"✅ {package} is installed")
        except pkg_resources.DistributionNotFound:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    print("\n🔑 Checking environment configuration...")
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        
        # Check if it contains OpenAI API key
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content and not content.count('your-') > 0:
                print("✅ OpenAI API key appears to be configured")
                return True
            else:
                print("⚠️  OpenAI API key may not be properly configured")
    else:
        print("📝 Creating .env file template...")
        try:
            with open(env_file, 'w') as f:
                f.write("# AI-Powered Task Manager Environment Configuration\n")
                f.write("# Replace 'your-openai-api-key-here' with your actual OpenAI API key\n")
                f.write("# Get your API key from: https://platform.openai.com/api-keys\n\n")
                f.write("OPENAI_API_KEY=your-openai-api-key-here\n")
            
            print("✅ .env file created successfully")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    print("\n🔧 Next steps for .env configuration:")
    print("1. Open the .env file in your text editor")
    print("2. Replace 'your-openai-api-key-here' with your actual OpenAI API key")
    print("3. Save the file")
    print("4. Get your API key from: https://platform.openai.com/api-keys")
    
    return False  # Return False to indicate user action needed

def run_basic_tests():
    """Run basic import tests to verify setup."""
    print("\n🧪 Running basic import tests...")
    
    test_imports = [
        ('langchain_mcp_adapters.client', 'MultiServerMCPClient'),
        ('langgraph.prebuilt', 'create_react_agent'),
        ('langchain_openai', 'ChatOpenAI'),
        ('mcp.server.fastmcp', 'FastMCP'),
        ('dotenv', 'load_dotenv')
    ]
    
    all_passed = True
    
    for module, item in test_imports:
        try:
            exec(f"from {module} import {item}")
            print(f"✅ Successfully imported {item} from {module}")
        except ImportError as e:
            print(f"❌ Failed to import {item} from {module}: {e}")
            all_passed = False
    
    return all_passed

def show_usage_instructions():
    """Show instructions for running the project."""
    print("\n🚀 Usage Instructions:")
    print("=" * 50)
    
    print("\n1. Install dependencies (if not already done):")
    print("   pip install -r requirements.txt")
    
    print("\n2. Configure your OpenAI API key in .env file")
    
    print("\n3. Start the notification server (Terminal 1):")
    print("   python notification_server.py")
    
    print("\n4. Run the task manager agent (Terminal 2):")
    print("   python task_manager_agent.py")
    
    print("\n5. Choose demo mode (1) or interactive mode (2)")
    
    print("\n📚 For detailed instructions, see README.md")

def main():
    """Main setup function."""
    print("🎯 AI-Powered Task Manager Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Create/check .env file
    env_ok = create_env_file()
    
    # Run basic tests
    if deps_ok:
        tests_ok = run_basic_tests()
    else:
        tests_ok = False
    
    # Summary
    print(f"\n📋 Setup Summary:")
    print(f"   Python Version: {'✅' if True else '❌'}")
    print(f"   Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"   Environment: {'✅' if env_ok else '⚠️ '}")
    print(f"   Import Tests: {'✅' if tests_ok else '❌'}")
    
    if deps_ok and tests_ok and env_ok:
        print("\n🎉 Setup completed successfully!")
        print("You're ready to run the task manager!")
    elif deps_ok and tests_ok:
        print("\n⚠️  Setup mostly complete!")
        print("Please configure your OpenAI API key in the .env file")
    else:
        print("\n❌ Setup needs attention:")
        if not deps_ok:
            print("   - Install missing dependencies")
        if not tests_ok:
            print("   - Fix import issues")
        if not env_ok:
            print("   - Configure OpenAI API key")
    
    show_usage_instructions()
    
    return deps_ok and tests_ok and env_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 