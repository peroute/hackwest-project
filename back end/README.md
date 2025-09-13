# University Resources API - PostgreSQL + MongoDB Atlas

A powerful FastAPI application with **PostgreSQL + MongoDB Atlas** for large-scale resource management and AI-powered semantic search using Google Gemini 2.5 Pro.

## 🏗️ **Hybrid Architecture Overview**

This system combines the best of both worlds:

- **🗄️ PostgreSQL**: Reliable relational database for user data, metadata, and analytics
- **☁️ MongoDB Atlas**: Cloud-based vector database for large-scale semantic search
- **🤖 Gemini AI**: Google's advanced AI for intelligent responses
- **📊 Analytics**: Comprehensive search logging and user behavior tracking

## ✨ **Key Features**

- **Large-Scale Data**: Handles millions of resources with vector embeddings
- **AI-Powered Search**: Semantic understanding with Gemini 2.5 Pro
- **User Management**: Complete user authentication and profile system
- **Advanced Analytics**: Search patterns, user behavior, and performance metrics
- **Batch Processing**: Efficient bulk operations for big data
- **Real-Time Search**: Sub-second response times with vector similarity
- **Scalable Architecture**: Designed for production workloads
- **Cloud-Native**: MongoDB Atlas provides global scalability

## 🚀 **Quick Start**

### **1. Prerequisites**

- **PostgreSQL 12+** (for user data)
- **MongoDB Atlas Account** (for vector search)
- **Python 3.8+** (for the application)

### **2. Setup**

```bash
# Clone and navigate to the project
cd "back end"

# Run the hybrid setup script
python setup_hybrid.py
```

### **3. Start the Application**

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **4. Access the API**

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 **Database Architecture**

### **PostgreSQL (User Data & Metadata)**
```sql
-- Users table
users (id, username, email, hashed_password, is_active, is_admin, created_at, updated_at)

-- Resources table (metadata only)
resources (
    id, title, description, url, category, tags, is_public, owner_id, 
    mongodb_id, created_at, updated_at
)

-- Questions table
questions (id, question_text, answer_text, user_id, resource_id, similarity_score, created_at)

-- Search logs table
search_logs (id, query, results_count, user_id, search_type, response_time_ms, created_at)
```

### **MongoDB Atlas (Vector Search)**
```json
{
  "_id": 1,
  "resource_id": 1,
  "title": "Library Study Spaces",
  "description": "Quiet study areas with computers and research materials",
  "url": "https://library.university.edu/study",
  "category": "Study Spaces",
  "tags": ["library", "study", "quiet"],
  "owner_id": 1,
  "is_public": true,
  "embedding": [0.1, 0.2, 0.3, ...], // 384-dimensional vector
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### **Vector Search with MongoDB Atlas Search**
```javascript
// Vector search using MongoDB Atlas Search
{
  "$vectorSearch": {
    "index": "vector_search_index",
    "path": "embedding",
    "queryVector": [0.1, 0.2, 0.3, ...],
    "numCandidates": 50,
    "limit": 5
  }
}
```

## 🔧 **API Endpoints**

### **Resources Management**
- `POST /api/v1/resources/` - Create resource with vector embedding
- `GET /api/v1/resources/` - List resources with filtering
- `POST /api/v1/resources/batch` - Batch create resources
- `GET /api/v1/resources/categories/list` - List all categories
- `GET /api/v1/resources/stats/summary` - Resource statistics

### **AI-Powered Search**
- `POST /api/v1/ask/` - Ask questions with AI responses
- `POST /api/v1/search/semantic` - Semantic vector search
- `POST /api/v1/search/vector` - Direct vector search
- `GET /api/v1/search/status` - Search system status

### **User Management**
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### **Analytics & Monitoring**
- `GET /api/v1/analytics/search-stats` - Search statistics
- `GET /api/v1/analytics/user-activity/{user_id}` - User activity
- `GET /api/v1/analytics/system-health` - System health metrics
- `GET /api/v1/analytics/search-trends` - Search trends over time

## 💡 **Usage Examples**

### **Create a Resource**
```bash
curl -X POST "http://localhost:8000/api/v1/resources/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Library Study Spaces",
    "description": "Quiet study areas with computers and research materials",
    "url": "https://library.university.edu/study",
    "category": "Study Spaces",
    "tags": ["library", "study", "quiet"],
    "is_public": true
  }'
```

### **Ask a Question**
```bash
curl -X POST "http://localhost:8000/api/v1/ask/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Where can I find quiet places to study?",
    "user_id": 1,
    "search_type": "semantic"
  }'
```

### **Semantic Search**
```bash
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "computer labs for programming",
    "limit": 5,
    "score_threshold": 0.7
  }'
```

## 🔍 **Search Types**

### **1. Semantic Search**
- Uses vector embeddings for meaning-based search
- Finds conceptually similar content
- Powered by sentence-transformers + MongoDB Atlas Search

### **2. Vector Search**
- Direct vector similarity search
- Configurable similarity thresholds
- Real-time performance

### **3. Hybrid Search**
- Combines semantic and keyword search
- Best of both approaches
- Intelligent result ranking

## 📈 **Performance & Scalability**

### **Vector Database (MongoDB Atlas)**
- **Capacity**: Millions of vectors
- **Speed**: Sub-second search times
- **Memory**: Efficient vector storage
- **Scalability**: Global cloud scaling
- **Availability**: 99.99% uptime SLA

### **PostgreSQL**
- **ACID Compliance**: Reliable data integrity
- **Indexing**: Fast metadata queries
- **Relationships**: Complex data modeling
- **Analytics**: Advanced reporting capabilities

### **AI Integration**
- **Gemini 2.5 Pro**: Latest Google AI model
- **Context Awareness**: Understands user intent
- **Response Quality**: Human-like answers
- **Scalability**: Handles concurrent requests

## 🛠️ **Configuration**

### **Environment Variables**
```env
# PostgreSQL Database (User Data)
POSTGRES_URL=postgresql://postgres:password@localhost:5432/university_resources

# MongoDB Atlas (Vector Search)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/university_resources

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
```

### **MongoDB Atlas Setup**
```javascript
// 1. Create a new cluster in MongoDB Atlas
// 2. Get your connection string
// 3. Create a database named 'university_resources'
// 4. Create a collection named 'resources'
// 5. Create a vector search index:

{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    },
    {
      "type": "string",
      "path": "title"
    },
    {
      "type": "string",
      "path": "description"
    },
    {
      "type": "string",
      "path": "category"
    }
  ]
}
```

## 📊 **Monitoring & Analytics**

### **Search Analytics**
- Query patterns and trends
- Response time metrics
- User behavior analysis
- Search success rates

### **System Health**
- Database connection status
- Vector database performance
- AI service availability
- Resource utilization

### **User Insights**
- Most active users
- Popular search terms
- Resource usage patterns
- Question-answer pairs

## 🚀 **Production Deployment**

### **1. Database Setup**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb university_resources

# MongoDB Atlas
# - Create account at https://www.mongodb.com/atlas
# - Create new cluster
# - Get connection string
# - Create vector search index
```

### **2. Application Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **3. Load Balancing**
- Use Nginx or similar for load balancing
- Multiple application instances
- Database connection pooling
- MongoDB Atlas auto-scaling

## 🔧 **Development**

### **Running Tests**
```bash
python test_api.py
```

### **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### **MongoDB Atlas Management**
```javascript
// View collection statistics
db.resources.stats()

// View search indexes
db.resources.listSearchIndexes()

// Test vector search
db.resources.aggregate([
  {
    "$vectorSearch": {
      "index": "vector_search_index",
      "path": "embedding",
      "queryVector": [0.1, 0.2, 0.3, ...],
      "numCandidates": 10,
      "limit": 5
    }
  }
])
```

## 🆚 **Architecture Comparison**

| Feature | PostgreSQL + MongoDB Atlas | PostgreSQL + pgvector | Qdrant |
|---------|---------------------------|----------------------|--------|
| **Data Scale** | Millions | Millions | Millions |
| **Search Speed** | Sub-second | Sub-second | Sub-second |
| **AI Integration** | Advanced | Advanced | Advanced |
| **User Management** | Full | Full | Full |
| **Analytics** | Comprehensive | Comprehensive | Good |
| **Scalability** | High | High | High |
| **Setup Complexity** | Medium | Medium | Low |
| **Maintenance** | Low | Medium | Low |
| **Cloud Native** | Yes | No | Yes |
| **Global Scaling** | Yes | No | Yes |

## 🎯 **Use Cases**

### **Perfect For:**
- Large university resource databases
- AI-powered search systems
- User management applications
- Analytics and reporting
- Production-scale deployments
- Global applications
- Cloud-native solutions

### **Not Ideal For:**
- Simple static websites
- Basic CRUD applications
- Development prototypes
- Single-user systems
- On-premise only solutions

## 📚 **API Documentation**

Complete API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is open source and available under the MIT License.

---

**Built with ❤️ for large-scale AI-powered resource management with cloud-native architecture**