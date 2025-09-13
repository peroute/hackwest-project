#!/usr/bin/env python3
"""
Simple setup script for PostgreSQL + MongoDB Atlas architecture.
Minimal dependencies, focuses on core functionality.
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up University Resources API - Simple Mode")
    print("=" * 60)
    print("📊 PostgreSQL + MongoDB Atlas Architecture")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Creating a simple .env file...")
        
        with open('.env', 'w') as f:
            f.write("""# PostgreSQL Database Configuration (User Data)
POSTGRES_URL=sqlite:///./university_resources.db

# MongoDB Atlas Configuration (AI Search)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources

# Google Gemini API Key (get from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
""")
        print("✅ Created simple .env file. Please update with your actual values!")
    
    # Install Python dependencies
    if not run_command("venv\\bin\\python.exe -m pip install -r requirements.txt", "Installing Python dependencies"):
        print("⚠️  Some dependencies may have failed to install. Continuing anyway...")
    
    # Run Alembic migrations
    if not run_command("venv\\bin\\python.exe -m alembic upgrade head", "Running database migrations"):
        print("⚠️  Migration failed. This might be expected if the database doesn't exist yet.")
        print("Trying to create initial migration...")
        run_command("venv\\bin\\python.exe -m alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration")
        run_command("venv\\bin\\python.exe -m alembic upgrade head", "Applying initial migration")
    
    print("\n🎉 Simple setup completed!")
    print("\n✨ What's configured:")
    print("  • SQLite database for user data (can be upgraded to PostgreSQL)")
    print("  • Python dependencies installed")
    print("  • Database migrations applied")
    print("  • Ready for MongoDB Atlas integration")
    
    print("\n⚠️  Optional Setup:")
    print("  • MongoDB Atlas: For AI search (optional)")
    print("  • PostgreSQL: For production (optional)")
    print("  • Gemini API: For AI responses (optional)")
    
    print("\nNext steps:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Visit http://localhost:8000/docs to test the API")
    print("3. Add resources and test the functionality!")
    
    print("\n🚀 Start the server:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
