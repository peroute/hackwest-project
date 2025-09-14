#!/usr/bin/env python3
"""
Team Setup Script for Texas Tech University AI Assistant
This script helps team members set up the project on their machines.
"""
import os
import sys
import subprocess
import platform

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🚀 Texas Tech University AI Assistant - Team Setup")
    print("=" * 60)
    print()
    print("📋 This script will:")
    print("   • Create a virtual environment")
    print("   • Install required dependencies")
    print("   • Set up the database")
    print("   • Create configuration files")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def create_virtual_environment():
    """Create virtual environment"""
    print("\n📦 Creating virtual environment...")
    
    # Check if virtual environment already exists
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the correct activation command for the platform"""
    if platform.system() == "Windows":
        # Check if it's MSYS2/Git Bash environment
        if os.path.exists(os.path.join("venv", "bin", "activate")):
            return "source venv/bin/activate"
        else:
            return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install project dependencies"""
    print("\n📚 Installing dependencies...")
    
    # Get the correct pip path
    if platform.system() == "Windows":
        # Check if it's MSYS2/Git Bash environment
        if os.path.exists(os.path.join("venv", "bin", "pip.exe")):
            pip_path = os.path.join("venv", "bin", "pip.exe")
        else:
            pip_path = os.path.join("venv", "Scripts", "pip.exe")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Check if pip exists
    if not os.path.exists(pip_path):
        print(f"❌ Pip not found at {pip_path}")
        print("   This might happen if the virtual environment wasn't created properly")
        print("   Try deleting the 'venv' folder and running the script again")
        return False
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    print("\n⚙️  Creating .env file template...")
    
    env_content = """# Texas Tech University AI Assistant Environment Variables

# MongoDB Atlas Connection String
# Get this from your MongoDB Atlas dashboard
# Format: mongodb+srv://username:password@cluster.mongodb.net/university_resources?retryWrites=true&w=majority
MONGODB_URL=your_mongodb_atlas_connection_string_here

# Gemini API Key (Optional - for enhanced AI responses)
# Get this from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Database URL (SQLite for development)
DATABASE_URL=sqlite:///./university_resources.db
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("   ⚠️  Please update the .env file with your actual credentials")
    else:
        print("✅ .env file already exists")

def run_database_migrations():
    """Run database migrations"""
    print("\n🗄️  Setting up database...")
    
    # Get the correct python path
    if platform.system() == "Windows":
        # Check if it's MSYS2/Git Bash environment
        if os.path.exists(os.path.join("venv", "bin", "python.exe")):
            python_path = os.path.join("venv", "bin", "python.exe")
        else:
            python_path = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_path = os.path.join("venv", "bin", "python")
    
    # Check if python exists
    if not os.path.exists(python_path):
        print(f"❌ Python not found at {python_path}")
        return False
    
    try:
        subprocess.run([python_path, "-m", "alembic", "upgrade", "head"], check=True)
        print("✅ Database migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run database migrations: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    # Get the correct python path
    if platform.system() == "Windows":
        # Check if it's MSYS2/Git Bash environment
        if os.path.exists(os.path.join("venv", "bin", "python.exe")):
            python_path = os.path.join("venv", "bin", "python.exe")
        else:
            python_path = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_path = os.path.join("venv", "bin", "python")
    
    # Check if python exists
    if not os.path.exists(python_path):
        print(f"❌ Python not found at {python_path}")
        return False
    
    try:
        # Test import
        result = subprocess.run([
            python_path, "-c", 
            "import app.main; print('✅ App imports successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("1. 📝 Update your .env file with actual credentials:")
    print("   - MongoDB Atlas connection string")
    print("   - Gemini API key (optional)")
    print()
    print("2. 🚀 Start the server:")
    activation_cmd = get_activation_command()
    print(f"   {activation_cmd}")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("3. 🌐 Access the API:")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - API Base URL: http://localhost:8000")
    print()
    print("4. 📚 Upload university resources:")
    print("   curl -X POST http://localhost:8000/api/v1/upload/ttu-resources")
    print()
    print("5. 🧪 Test the API:")
    print('   curl -X POST "http://localhost:8000/api/v1/ask/" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"question": "What fitness programs are available?"}\'')
    print()
    print("📖 For detailed instructions, see README.md")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    required_files = ["requirements.txt", "app", "alembic.ini"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("   Make sure you're running this script from the project root directory")
        return False
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Setup failed: Could not create virtual environment")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Create .env file
    create_env_file()
    
    # Run database migrations
    if not run_database_migrations():
        print("\n⚠️  Warning: Database migrations failed, but continuing...")
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Warning: Installation test failed, but continuing...")
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
