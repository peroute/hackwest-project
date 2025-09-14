# 🚀 Team Instructions - Texas Tech University AI Assistant

## Quick Start (5 minutes)

### 1. Run Setup Script
```bash
python setup_team.py
```

### 2. Update Environment Variables
Edit `.env` file with your MongoDB credentials:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources?retryWrites=true&w=majority
```

### 3. Start Server
**Windows:**
```bash
start_server.bat
```

**macOS/Linux:**
```bash
./start_server.sh
```

### 4. Test API
Open http://localhost:8000/docs in your browser

## What Your Teammates Need to Do

### Step 1: Get the Code
```bash
git clone <your-repo-url>
cd "back end"
```

### Step 2: Run Setup
```bash
python setup_team.py
```

### Step 3: Get MongoDB Credentials
- Ask you for the MongoDB Atlas connection string
- Or follow the MongoDB setup guide in `TEAM_SETUP_GUIDE.md`

### Step 4: Start Development
```bash
# Windows
start_server.bat

# macOS/Linux  
./start_server.sh
```

## Project Features

✅ **Intelligent AI Responses**
- Automatically detects question types
- Provides educational advice for academic questions
- Searches and finds campus resources when needed

✅ **No Authentication Required**
- Simple API that accepts just the question
- Works immediately without user setup

✅ **Perfect Search**
- Finds fitness, mental health, library, and tutoring resources
- Intelligent resource detection

✅ **Educational Support**
- Study strategies and time management
- Exam preparation and academic advice
- Writing and communication help

## API Usage

### Ask a Question
```bash
curl -X POST "http://localhost:8000/api/v1/ask/" \
     -H "Content-Type: application/json" \
     -d '{"question": "What fitness programs are available?"}'
```

### Search Resources
```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "mental health", "limit": 5}'
```

## Files Created for Team

- `setup_team.py` - Automated setup script
- `README.md` - Complete documentation
- `TEAM_SETUP_GUIDE.md` - Step-by-step setup guide
- `DEPLOYMENT.md` - Production deployment guide
- `start_server.bat` - Windows startup script
- `start_server.sh` - macOS/Linux startup script
- `test_setup.py` - Test script to verify setup

## Troubleshooting

### Common Issues

1. **Port 8000 in use:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -ti:8000 | xargs kill -9
   ```

2. **MongoDB connection failed:**
   - Check `.env` file has correct MongoDB URL
   - Verify IP is whitelisted in MongoDB Atlas

3. **Python/pip issues:**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

## Team Credentials

**MongoDB Atlas:**
- Cluster: `ttu-ai-assistant`
- Database: `university_resources`
- Collection: `resources`

**Shared Access:**
- All team members use the same MongoDB cluster
- Each person has their own local development environment
- The `.env` file contains shared MongoDB credentials

## Next Steps for Team

1. **Share MongoDB credentials** with team members
2. **Test the setup** using `test_setup.py`
3. **Upload resources** using the upload endpoint
4. **Start developing** the frontend integration

## Support

- **Full Documentation:** `README.md`
- **Setup Guide:** `TEAM_SETUP_GUIDE.md`
- **API Docs:** http://localhost:8000/docs
- **Test Script:** `python test_setup.py`

---

**Your MVP is ready for team collaboration!** 🎉
