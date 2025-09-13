# Deployment Guide

## Local Development

### Quick Start
1. Run the setup script: `python setup_team.py`
2. Update `.env` with your credentials
3. Start server: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Windows
```bash
# Setup
python setup_team.py

# Start server
start_server.bat
# OR
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### macOS/Linux
```bash
# Setup
python3 setup_team.py

# Start server
./start_server.sh
# OR
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

### 1. Environment Setup

Create production `.env`:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources?retryWrites=true&w=majority
GEMINI_API_KEY=your_production_api_key
DATABASE_URL=sqlite:///./university_resources.db
```

### 2. Install Production Dependencies

```bash
# Install production server
pip install gunicorn

# Install all dependencies
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python -m alembic upgrade head
```

### 4. Start Production Server

```bash
# Using Gunicorn (recommended)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Nginx Configuration (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Run

```bash
# Build image
docker build -t ttu-ai-assistant .

# Run container
docker run -p 8000:8000 --env-file .env ttu-ai-assistant
```

## Cloud Deployment

### Heroku

1. **Create Procfile:**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Railway

1. **Connect GitHub repository**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically**

### DigitalOcean App Platform

1. **Create new app from GitHub**
2. **Set environment variables**
3. **Deploy**

## Environment Variables

### Required
- `MONGODB_URL`: MongoDB Atlas connection string

### Optional
- `GEMINI_API_KEY`: Google Gemini API key for enhanced responses
- `DATABASE_URL`: Database connection string (defaults to SQLite)

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Development: http://localhost:8000/docs
- Production: https://your-domain.com/docs

### Logs
```bash
# View logs
tail -f logs/app.log

# Or with systemd
journalctl -u ttu-ai-assistant -f
```

## Security Considerations

1. **MongoDB Atlas Security:**
   - Use strong passwords
   - Whitelist specific IP addresses
   - Enable authentication

2. **API Security:**
   - Add rate limiting
   - Implement authentication if needed
   - Use HTTPS in production

3. **Environment Variables:**
   - Never commit `.env` files
   - Use secure secret management
   - Rotate API keys regularly

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **MongoDB connection failed:**
   - Check connection string
   - Verify IP whitelist
   - Check credentials

3. **Module not found:**
   - Activate virtual environment
   - Reinstall requirements
   - Check Python path

### Performance Optimization

1. **Database:**
   - Add indexes for frequently queried fields
   - Use connection pooling
   - Monitor query performance

2. **API:**
   - Implement caching
   - Use async/await properly
   - Monitor response times

3. **MongoDB Atlas:**
   - Upgrade to higher tier if needed
   - Monitor usage and performance
   - Optimize queries

## Backup and Recovery

### Database Backup
```bash
# MongoDB Atlas has automatic backups
# For SQLite, backup the database file
cp university_resources.db backup_$(date +%Y%m%d).db
```

### Application Backup
```bash
# Backup application code
tar -czf ttu-ai-assistant-$(date +%Y%m%d).tar.gz .
```

## Scaling

### Horizontal Scaling
- Use load balancer
- Deploy multiple instances
- Use container orchestration (Kubernetes)

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Use caching strategies
