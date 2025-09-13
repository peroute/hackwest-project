# Team Setup Guide

## Quick Setup (5 minutes)

### Step 1: Run the Setup Script

**Windows:**
```bash
python setup_team.py
```

**macOS/Linux:**
```bash
python3 setup_team.py
```

### Step 2: Update Environment Variables

Edit the `.env` file with your credentials:

```env
# Get this from MongoDB Atlas dashboard
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources?retryWrites=true&w=majority

# Optional: Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 3: Start the Server

**Windows:**
```bash
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the API

Open http://localhost:8000/docs in your browser or test with curl:

```bash
curl -X POST "http://localhost:8000/api/v1/ask/" \
     -H "Content-Type: application/json" \
     -d '{"question": "What fitness programs are available?"}'
```

## MongoDB Atlas Setup

### 1. Create Account
- Go to https://www.mongodb.com/atlas
- Sign up for free account

### 2. Create Cluster
- Choose "M0 Sandbox" (free tier)
- Select region close to you
- Name your cluster (e.g., "ttu-ai-assistant")

### 3. Database Access
- Go to "Database Access" → "Add New Database User"
- Username: `ttu-ai-user`
- Password: Create a strong password
- Database User Privileges: "Read and write to any database"

### 4. Network Access
- Go to "Network Access" → "Add IP Address"
- Choose "Allow access from anywhere" (0.0.0.0/0)
- Click "Confirm"

### 5. Get Connection String
- Go to "Clusters" → Click "Connect"
- Choose "Connect your application"
- Copy the connection string
- Replace `<password>` with your database user password
- Replace `<dbname>` with `university_resources`

Example:
```
mongodb+srv://ttu-ai-user:your_password@cluster0.abc123.mongodb.net/university_resources?retryWrites=true&w=majority
```

## Gemini API Setup (Optional)

### 1. Get API Key
- Go to https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy the generated key

### 2. Add to .env
```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### MongoDB Connection Failed
1. Check your connection string in `.env`
2. Verify your IP is whitelisted in MongoDB Atlas
3. Check your database user credentials
4. Ensure your cluster is running

### Python/Pip Issues
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall requirements
pip install -r requirements.txt
```

### Database Migration Errors
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

## Project Structure

```
back end/
├── app/                    # Main application code
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── setup_team.py          # Team setup script
├── README.md              # Detailed documentation
└── TEAM_SETUP_GUIDE.md    # This file
```

## API Endpoints

- **Ask Question**: `POST /api/v1/ask/`
- **Search Resources**: `POST /api/v1/search/`
- **Upload Data**: `POST /api/v1/upload/ttu-resources`
- **API Docs**: `GET /docs`

## Need Help?

1. Check the troubleshooting section above
2. Review the full README.md
3. Check the API documentation at http://localhost:8000/docs
4. Look at the server logs for error messages

## Team Credentials

**MongoDB Atlas:**
- Cluster: `ttu-ai-assistant`
- Database: `university_resources`
- Collection: `resources`

**Shared Resources:**
- All team members can use the same MongoDB cluster
- Each person can have their own local development environment
- The `.env` file should contain the shared MongoDB credentials
