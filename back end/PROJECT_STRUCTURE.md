# 📁 Project Structure

## Core Application Files
```
back end/
├── app/                          # Main application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # Database connections (SQLite + MongoDB)
│   ├── models.py                # SQLAlchemy models for SQLite
│   ├── schemas.py               # Pydantic schemas for API validation
│   ├── gemini.py                # AI logic and search functionality
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       ├── ask.py               # Q&A endpoints
│       ├── search.py            # Resource search endpoints
│       ├── users.py             # User management
│       ├── resources.py         # Resource management
│       ├── upload.py            # Data upload endpoints
│       └── analytics.py         # Analytics and reporting
```

## Database & Migrations
```
├── alembic/                     # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Migration files
├── alembic.ini                  # Alembic configuration
└── university_resources.db      # SQLite database (auto-created)
```

## Team Setup & Documentation
```
├── setup_team.py                # Automated team setup script
├── start_server.bat             # Windows startup script
├── start_server.sh              # macOS/Linux startup script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # Complete project documentation
├── TEAM_INSTRUCTIONS.md         # Quick start for team members
├── TEAM_SETUP_GUIDE.md          # Detailed setup instructions
├── DEPLOYMENT.md                # Production deployment guide
└── PROJECT_STRUCTURE.md         # This file
```

## Data Files
```
├── ttu_resources.json           # University resources data
└── .env                         # Environment variables (create this)
```

## Virtual Environment (Not in Git)
```
└── venv/                        # Python virtual environment
    ├── bin/                     # Executables (Windows: Scripts/)
    ├── lib/                     # Installed packages
    └── pyvenv.cfg              # Virtual environment config
```

## Key Features

### ✅ **Core Functionality**
- **Intelligent AI Responses** - Automatically detects question types
- **Perfect Search** - Finds fitness, mental health, library resources
- **Educational Support** - Study strategies, time management, exam prep
- **No Authentication** - Simple API that just works

### ✅ **Team-Friendly Setup**
- **One-Command Setup** - `python setup_team.py`
- **Cross-Platform** - Windows, macOS, Linux support
- **Comprehensive Docs** - Multiple documentation levels
- **Easy Startup** - One-click server start scripts

### ✅ **Production Ready**
- **Database Migrations** - Alembic for schema management
- **Environment Config** - `.env` file for configuration
- **Error Handling** - Graceful fallbacks and error responses
- **API Documentation** - Auto-generated Swagger UI

## Quick Start Commands

### Setup
```bash
python setup_team.py
```

### Start Server
```bash
# Windows
start_server.bat

# macOS/Linux
./start_server.sh
```

### Test API
```bash
curl -X POST "http://localhost:8000/api/v1/ask/" \
     -H "Content-Type: application/json" \
     -d '{"question": "What fitness programs are available?"}'
```

## File Purposes

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application and route registration |
| `app/gemini.py` | AI logic, search, and response generation |
| `app/database.py` | Database connections and session management |
| `app/models.py` | SQLAlchemy models for user data |
| `app/schemas.py` | Pydantic models for API validation |
| `app/routers/` | API endpoint handlers |
| `setup_team.py` | Automated setup for team members |
| `requirements.txt` | Python package dependencies |
| `README.md` | Complete project documentation |
| `TEAM_INSTRUCTIONS.md` | Quick start guide for team |

## What's NOT Included

- ❌ Test files (removed for production)
- ❌ Debug scripts (removed for production)
- ❌ Temporary files (removed for production)
- ❌ Virtual environment (created by setup script)
- ❌ Environment variables (created by user)
- ❌ Database files (created automatically)

## Team Collaboration

1. **Share Repository** - Give team access to Git repo
2. **Share MongoDB Credentials** - Provide connection string
3. **Run Setup** - Each member runs `python setup_team.py`
4. **Start Development** - Use startup scripts to begin work

---

**Your project is clean, organized, and ready for team collaboration!** 🚀
