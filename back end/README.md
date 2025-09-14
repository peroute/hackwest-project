# Texas Tech University AI Assistant

A FastAPI-based AI assistant that provides educational support and campus resource information for Texas Tech University students.

## Features

- **Intelligent AI Responses**: Automatically detects question types and provides appropriate responses
- **Educational Support**: Study strategies, time management, exam preparation, and academic advice
- **Campus Resources**: Search and find fitness programs, mental health services, library resources, and tutoring
- **MongoDB Integration**: Stores and searches university resources
- **SQLite Database**: Tracks user questions and search history
- **No Authentication Required**: Simple API that accepts just the question

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "back end"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   MONGODB_URL=your_mongodb_atlas_connection_string
   GEMINI_API_KEY=your_gemini_api_key_optional
   ```

6. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - API Base URL: http://localhost:8000

## API Usage

### Ask a Question

**Endpoint:** `POST /api/v1/ask/`

**Request:**
```json
{
  "question": "How can I improve my study habits?"
}
```

**Response:**
```json
{
  "question": "How can I improve my study habits?",
  "answer": "Great question about studying! Here are some effective study strategies...",
  "relevant_resources": [],
  "user_id": null,
  "timestamp": 1694640000.0
}
```

### Search Resources

**Endpoint:** `POST /api/v1/search/`

**Request:**
```json
{
  "query": "fitness programs",
  "limit": 5
}
```

## Environment Setup

### MongoDB Atlas Setup

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/atlas
   - Sign up for a free account

2. **Create a Cluster**
   - Choose the free tier (M0)
   - Select a region close to you
   - Name your cluster

3. **Set up Database Access**
   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Create a username and password
   - Set privileges to "Read and write to any database"

4. **Set up Network Access**
   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Choose "Allow access from anywhere" (0.0.0.0/0) for development
   - For production, add specific IP addresses

5. **Get Connection String**
   - Go to "Clusters" in the left sidebar
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Replace `<dbname>` with `university_resources`

6. **Add to .env file**
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources?retryWrites=true&w=majority
   ```

### Gemini API Setup (Optional)

1. **Get Gemini API Key**
   - Go to https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key

2. **Add to .env file**
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Project Structure

```
back end/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connections
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── gemini.py            # AI logic and search
│   └── routers/
│       ├── ask.py           # Q&A endpoints
│       ├── search.py        # Search endpoints
│       ├── users.py         # User management
│       ├── resources.py     # Resource management
│       ├── analytics.py     # Analytics
│       └── upload.py        # Data upload
├── alembic/                 # Database migrations
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── ttu_resources.json       # University resources data
└── README.md               # This file
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Kill processes using port 8000
   netstat -ano | findstr :8000
   taskkill /PID <PID_NUMBER> /F
   ```

2. **MongoDB connection failed**
   - Check your MongoDB URL in `.env`
   - Ensure your IP is whitelisted in MongoDB Atlas
   - Verify your database user credentials

3. **Module not found errors**
   ```bash
   # Make sure virtual environment is activated
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   
   # Reinstall requirements
   pip install -r requirements.txt
   ```

4. **Database migration errors**
   ```bash
   # Reset and run migrations
   alembic downgrade base
   alembic upgrade head
   ```

## Development

### Adding New Resources

1. **Upload via API**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/upload/ttu-resources" \
        -H "Content-Type: application/json"
   ```

2. **Manual upload**
   - Add resources to `ttu_resources.json`
   - Use the upload endpoint to process them

### Testing

```bash
# Test the API
curl -X POST "http://localhost:8000/api/v1/ask/" \
     -H "Content-Type: application/json" \
     -d '{"question": "What fitness programs are available?"}'
```

## Production Deployment

1. **Set up production environment variables**
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Set up proper MongoDB Atlas security**
4. **Configure reverse proxy** (e.g., Nginx)
5. **Set up monitoring and logging**

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at http://localhost:8000/docs
3. Check the logs for error messages

## License

This project is for educational purposes at Texas Tech University.