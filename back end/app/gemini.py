"""
Google Gemini 2.5 Pro integration with PostgreSQL + MongoDB Atlas.
Handles AI search and intelligent responses.
"""
import os
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import Question, SearchLog
from .database import get_postgres_db, get_mongodb_atlas
from .schemas import SearchResult, AskResponse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
        print("✅ Gemini API configured")
    except ImportError:
        print("⚠️  Google Generative AI not installed - using fallback")
        GEMINI_AVAILABLE = False
else:
    print("⚠️  GEMINI_API_KEY not set - AI features will be limited")
    GEMINI_AVAILABLE = False

# Initialize sentence transformer model for embeddings
try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Sentence transformer model loaded")
except ImportError:
    print("⚠️  Sentence transformers not installed - using fallback")
    embedding_model = None


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for given text using sentence-transformers.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of float values representing the embedding
    """
    if not embedding_model:
        # Fallback: return a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to 384-dimensional vector
        embedding = [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(384)]
        return embedding
    
    if not text:
        return [0.0] * 384  # Return zero vector for empty text
    
    embedding = embedding_model.encode(text)
    return embedding.tolist()


def store_resource_with_embedding(
    title: str, 
    description: str, 
    url: str,
    category: str = None,
    tags: List[str] = None,
    owner_id: int = None,
    is_public: bool = True
) -> Dict[str, Any]:
    """
    Create a new resource with embedding and store ONLY in MongoDB Atlas.
    
    Args:
        title: Resource title
        description: Resource description
        url: Resource URL
        category: Resource category
        tags: List of tags
        owner_id: ID of the user who created the resource
        is_public: Whether the resource is public
        
    Returns:
        Created resource document from MongoDB Atlas
    """
    try:
        # Generate embedding
        combined_text = f"{title} {description or ''}"
        embedding = generate_embedding(combined_text)
        
        # Create MongoDB document
        mongodb_doc = {
            "title": title,
            "description": description,
            "url": url,
            "category": category,
            "tags": tags or [],
            "owner_id": owner_id,
            "is_public": is_public,
            "embedding": embedding,
            "created_at": "2024-01-01T00:00:00Z",  # Will be set by MongoDB
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Get MongoDB Atlas connection directly
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return None
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Insert document directly
        result = collection.insert_one(mongodb_doc)
        
        if result.inserted_id:
            # Add the MongoDB ID to the document (convert to string for JSON serialization)
            mongodb_doc["_id"] = str(result.inserted_id)
            mongodb_doc["resource_id"] = str(result.inserted_id)
            print(f"✅ Resource stored in MongoDB Atlas with ID: {result.inserted_id}")
            
            # Close connection
            client.close()
            return mongodb_doc
        else:
            print("❌ Error: Could not store resource in MongoDB Atlas")
            client.close()
            return None
            
    except Exception as e:
        print(f"❌ Error storing resource in MongoDB Atlas: {e}")
        return None


def search_similar_resources(
    query: str, 
    limit: int = 5, 
    score_threshold: float = 0.7,
    filters: Dict[str, Any] = None
) -> List[SearchResult]:
    """
    Search for similar resources using MongoDB Atlas.
    
    Args:
        query: Search query
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        filters: Additional filters for search
        
    Returns:
        List of similar resource results
    """
    try:
        # Get MongoDB Atlas connection directly
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return []
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Simple and effective search
        query_lower = query.lower().strip()
        
        # Category mappings for direct matching
        category_mappings = {
            "fitness": "Fitness",
            "gym": "Fitness", 
            "exercise": "Fitness",
            "workout": "Fitness",
            "sports": "Fitness",
            "mental": "Mental Health",
            "counseling": "Mental Health",
            "therapy": "Mental Health",
            "library": "Library",
            "tutoring": "Education and Academic Help",
            "academic": "Education and Academic Help",
            "study": "Education and Academic Help"
        }
        
        # Build search patterns
        search_patterns = []
        
        # 1. Direct category matching (highest priority)
        for word in query_lower.split():
            if word in category_mappings:
                search_patterns.append({"category": category_mappings[word]})
        
        # 2. Search for key terms in content
        key_terms = ["fitness", "mental", "health", "counseling", "library", "tutoring", "academic", "study", "gym", "exercise", "sports"]
        for term in key_terms:
            if term in query_lower:
                search_patterns.extend([
                    {"title": {"$regex": term, "$options": "i"}},
                    {"description": {"$regex": term, "$options": "i"}},
                    {"tags": {"$regex": term, "$options": "i"}}
                ])
        
        # If no specific patterns, do general search
        if not search_patterns:
            search_patterns = [
                {"title": {"$regex": query_lower, "$options": "i"}},
                {"description": {"$regex": query_lower, "$options": "i"}},
                {"category": {"$regex": query_lower, "$options": "i"}}
            ]
        
        # Combine patterns
        search_query = {"$or": search_patterns}
        
        if filters:
            search_query.update(filters)
        
        # Search documents
        cursor = collection.find(search_query).limit(limit * 2)
        docs = list(cursor)
        
        # Score results
        scored_docs = []
        for doc in docs:
            score = 0
            title_lower = doc.get("title", "").lower()
            desc_lower = doc.get("description", "").lower()
            category_lower = doc.get("category", "").lower()
            tags_lower = " ".join(doc.get("tags", [])).lower()
            
            # Category match gets highest score
            for word in query_lower.split():
                if word in category_mappings and category_lower == category_mappings[word].lower():
                    score += 20
                    break
            
            # Content matches
            for term in key_terms:
                if term in query_lower:
                    if term in title_lower:
                        score += 10
                    if term in desc_lower:
                        score += 5
                    if term in tags_lower:
                        score += 3
            
            if score > 0:
                doc["_relevance_score"] = score
                scored_docs.append(doc)
        
        # Sort by score and take best results
        scored_docs.sort(key=lambda x: x["_relevance_score"], reverse=True)
        docs = scored_docs[:limit]
        
        # Convert to SearchResult objects
        search_results = []
        for doc in docs:
            relevance_score = doc.get("_relevance_score", 0)
            normalized_score = min(relevance_score / 20.0, 1.0)
            
            search_result = SearchResult(
                id=str(doc["_id"]),
                title=doc["title"],
                description=doc["description"],
                url=doc["url"],
                category=doc.get("category"),
                tags=doc.get("tags", []),
                similarity_score=normalized_score,
                owner_id=doc.get("owner_id")
            )
            search_results.append(search_result)
        
        client.close()
        return search_results
        
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return []


def generate_ai_answer_with_context(question: str, resources: List[SearchResult], conversation_context: str, is_greeting: bool = False) -> str:
    """
    Generate AI answer using Gemini with conversation context and relevant resources.
    Handles general greetings and questions without requiring resource search.
    """
    try:
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Check if this is a general greeting or non-resource question
        general_greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up"]
        question_lower = question.lower().strip()
        
        # Determine if we need to search for resources
        needs_resource_search = not any(greeting in question_lower for greeting in general_greetings)
        
        # Build resources context only if needed
        resources_text = ""
        if needs_resource_search and resources:
            resources_text = "Relevant resources from the database:\n"
            for i, resource in enumerate(resources, 1):
                resources_text += f"{i}. **{resource.title}**\n"
                if resource.description:
                    resources_text += f"   {resource.description}\n"
                if resource.category:
                    resources_text += f"   📂 Category: {resource.category}\n"
                resources_text += f"   🔗 {resource.url}\n\n"
        
        # Let AI intelligently decide how to respond based on question and available resources
        if is_greeting:
            # Greeting response
            prompt = f"""You are a friendly Texas Tech University educational assistant. 
{conversation_context}
Current message: {question}

Respond briefly and conversationally. Introduce yourself and ask how you can help with academic or campus needs. Keep it short and welcoming."""
        
        elif resources:
            # Use resources if they are relevant
            prompt = f"""You are a helpful Texas Tech University assistant.
{conversation_context}
Current question: {question}

{resources_text}

Provide a concise, helpful answer based on the available resources. Keep it brief and focused. Include relevant resource links when appropriate."""
        
        else:
            # Answer directly without resources - use AI for intelligent educational responses
            prompt = f"""You are a knowledgeable Texas Tech University educational assistant.
{conversation_context}
Current question: {question}

Provide a helpful, educational response. Be informative, encouraging, and focused on academic success. 
If it's a general knowledge question, explain it clearly and provide educational value.
If it's about study strategies, provide practical advice.
Keep your response conversational but educational. Don't mention that you're an AI - just be helpful and knowledgeable."""

        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error generating AI answer with context: {e}")
        # Fallback to simple answer
        return generate_ai_answer(question, resources)


def generate_ai_answer(question: str, resources: List[SearchResult]) -> str:
    """
    Generate answer using Gemini 2.5 Pro with provided resources as context.
    
    Args:
        question: User's question
        resources: List of relevant resources
        
    Returns:
        AI-generated response string
    """
    if not GEMINI_AVAILABLE:
        return generate_simple_answer(question, resources)
    
    # Check if this is a general greeting or educational question that doesn't need resources
    general_greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up", "thanks", "thank you"]
    educational_keywords = ["what is", "explain", "tell me about", "how does", "why", "when", "study tips", "advice", "suggest", "recommend", "best way", "tips for", "how can i improve"]
    question_lower = question.lower().strip()
    
    is_general_greeting = any(greeting in question_lower for greeting in general_greetings)
    is_educational_question = any(keyword in question_lower for keyword in educational_keywords)
    
    if not resources and not is_general_greeting and not is_educational_question:
        return "I couldn't find any relevant resources to answer your question. Please try rephrasing your question or adding more resources to the database."
    
    # Format resources for the prompt
    resources_text = "\n".join([
        f"- **{resource.title}**: {resource.description or 'No description'} "
        f"(Category: {resource.category or 'Uncategorized'}) "
        f"- 🔗 {resource.url}"
        for resource in resources
    ])
    
    # Create different prompts based on question type
    if is_general_greeting or is_educational_question:
        prompt = f"""You are a friendly and knowledgeable educational assistant for Texas Tech University students. 
Current message: {question}

You can help with:
- General academic advice and study tips
- Educational concepts and explanations
- College life guidance
- Study strategies and time management
- Academic planning and career advice
- General questions about learning and education

Respond naturally and conversationally. If this is a greeting, introduce yourself as the Texas Tech University educational assistant. 
Be warm, encouraging, and focused on helping students succeed academically. 
If the question is about specific campus resources or services, suggest they ask about those specifically."""
    else:
        prompt = f"""You are a helpful university assistant with access to a comprehensive database of university resources.

The user will ask questions about university resources, services, or general information.
Use the following resources to provide accurate, helpful answers.
Always include relevant links in your response.
If the resources don't fully answer the question, say so and suggest how the user might find more information.

Available Resources:
{resources_text}

User Question: {question}

Please provide a comprehensive, helpful answer based on the available resources."""

    try:
        # Use Gemini 2.5 Pro
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return generate_simple_answer(question, resources)
            
    except Exception as e:
        print(f"❌ Error generating AI response: {e}")
        return generate_simple_answer(question, resources)


def generate_educational_response(question: str) -> str:
    """
    Generate intelligent educational responses for academic questions.
    """
    question_lower = question.lower()
    
    # Study and academic strategies
    if any(word in question_lower for word in ["study", "studying", "studies", "learn", "learning"]):
        return """Great question about studying! Here are some effective study strategies:

**Active Learning Techniques:**
• Use the Pomodoro Technique (25 min focused study, 5 min break)
• Create mind maps and concept diagrams
• Teach the material to someone else
• Use flashcards for memorization
• Practice with past exams and quizzes

**Time Management:**
• Create a study schedule and stick to it
• Study in shorter, focused sessions rather than long cramming
• Find your peak productivity hours
• Eliminate distractions (phone, social media)

**Memory Techniques:**
• Use acronyms and mnemonics
• Connect new information to what you already know
• Use spaced repetition for long-term retention

Would you like specific advice for any particular subject or exam type?"""

    # Time management
    elif any(word in question_lower for word in ["time management", "schedule", "organize", "productivity"]):
        return """Excellent question about time management! Here are proven strategies:

**Planning & Organization:**
• Use a digital or paper planner
• Break large tasks into smaller, manageable chunks
• Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
• Prioritize tasks using the Eisenhower Matrix

**Daily Habits:**
• Start with your most challenging task first
• Batch similar activities together
• Set specific times for checking email/social media
• Take regular breaks to maintain focus

**Academic-Specific Tips:**
• Create a weekly study schedule
• Use color-coding for different subjects
• Set up a dedicated study space
• Review and adjust your schedule weekly

What specific area of time management would you like to focus on?"""

    # Exam preparation
    elif any(word in question_lower for word in ["exam", "test", "prepare", "preparation"]):
        return """Great question about exam preparation! Here's a comprehensive approach:

**Before the Exam:**
• Start studying early (not the night before!)
• Review all course materials and notes
• Create a study guide with key concepts
• Practice with sample questions and past exams
• Form study groups for discussion and review

**Study Techniques:**
• Use active recall (test yourself without looking at notes)
• Explain concepts out loud or to others
• Create visual aids like diagrams and charts
• Use the Feynman Technique (explain simply)

**During the Exam:**
• Read all questions first and budget your time
• Answer easier questions first to build confidence
• Show your work for partial credit
• Review your answers if time permits

**Test-Taking Strategies:**
• For multiple choice: eliminate obviously wrong answers
• For essays: outline your response first
• Stay calm and manage test anxiety

What type of exam are you preparing for?"""

    # General academic advice
    elif any(word in question_lower for word in ["academic", "college", "university", "school", "grade", "gpa"]):
        return """I'd be happy to help with academic success! Here are some key strategies:

**Academic Excellence:**
• Attend all classes and participate actively
• Take detailed notes and review them regularly
• Build relationships with professors and classmates
• Use office hours for clarification and guidance
• Join study groups and academic clubs

**Study Skills:**
• Find your optimal learning style (visual, auditory, kinesthetic)
• Use active learning techniques
• Create a consistent study routine
• Take breaks to avoid burnout

**Campus Resources:**
• Visit the tutoring center for difficult subjects
• Use the library's research resources
• Take advantage of writing centers
• Consider academic advising for course planning

**Wellness & Balance:**
• Maintain a healthy sleep schedule
• Exercise regularly to boost brain function
• Eat nutritious meals
• Manage stress through relaxation techniques

What specific academic area would you like help with?"""

    # Science subjects
    elif any(word in question_lower for word in ["science", "biology", "chemistry", "physics", "math", "mathematics"]):
        return """Great question about science subjects! Here are effective strategies:

**For Science Courses:**
• Understand concepts before memorizing formulas
• Practice problem-solving regularly
• Draw diagrams and visual representations
• Connect theory to real-world applications
• Use the scientific method in your thinking

**For Math:**
• Practice problems daily, not just before exams
• Understand the underlying concepts, not just procedures
• Work through problems step-by-step
• Use different approaches to solve the same problem
• Don't just memorize formulas - understand when to use them

**Study Techniques:**
• Create concept maps showing relationships
• Use flashcards for definitions and formulas
• Explain problems to study partners
• Work through practice problems without looking at solutions first

**Resources:**
• Use Khan Academy for additional explanations
• Form study groups to work through difficult problems
• Visit office hours for personalized help
• Use online resources and video tutorials

What specific science or math topic are you working on?"""

    # Writing and communication
    elif any(word in question_lower for word in ["write", "writing", "essay", "paper", "report", "communication"]):
        return """Excellent question about writing! Here are proven strategies:

**Writing Process:**
• Start with brainstorming and outlining
• Write a clear thesis statement
• Use the PEEL method (Point, Evidence, Explanation, Link)
• Write multiple drafts and revise thoroughly
• Proofread carefully for grammar and clarity

**Essay Structure:**
• Introduction: Hook, background, thesis
• Body paragraphs: Topic sentence, evidence, analysis
• Conclusion: Restate thesis, summarize key points, broader implications

**Research & Sources:**
• Use credible, academic sources
• Take detailed notes with proper citations
• Avoid plagiarism by paraphrasing and citing properly
• Use the library's research databases

**Writing Resources:**
• Visit the writing center for feedback
• Use grammar checkers as a starting point
• Read your work aloud to catch errors
• Get peer feedback before final submission

**Communication Skills:**
• Practice presentations in front of a mirror
• Use visual aids effectively
• Prepare for questions and discussion
• Practice active listening in conversations

What type of writing or communication project are you working on?"""

    # General knowledge questions
    else:
        return f"""I'd be happy to help with that question! As a Texas Tech University educational assistant, I specialize in academic support and campus resources.

For your question about "{question}", I can help you with:
• Study strategies and academic success tips
• Time management and organization techniques
• Research and writing assistance
• Information about campus resources and services
• General academic guidance

Could you provide more specific details about what you'd like to know? For example:
• Are you looking for study techniques for a particular subject?
• Do you need help with time management or organization?
• Are you seeking information about specific campus resources?
• Would you like advice on academic planning or career preparation?

The more specific you can be, the better I can assist you!"""


def generate_simple_answer(question: str, resources: List[SearchResult]) -> str:
    """
    Generate a simple answer without AI when Gemini is not available.
    Handles educational conversations and resource questions.
    
    Args:
        question: User's question
        resources: List of relevant resources
        
    Returns:
        Simple response string
    """
    question_lower = question.lower().strip()
    
    # Simple greeting detection
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up", "thanks", "thank you"]
    is_greeting = any(greeting in question_lower for greeting in greetings)
    
    # Let AI intelligently decide how to respond
    if is_greeting:
        return "Hello! I'm your Texas Tech University educational assistant. How can I help you with academic or campus needs today?"
    
    elif resources:
        # Use resources if they are relevant
        response = "Here are some relevant resources:\n\n"
        for i, resource in enumerate(resources, 1):
            response += f"{i}. **{resource.title}**\n"
            if resource.description:
                response += f"   {resource.description[:100]}...\n"  # Truncate description
            response += f"   🔗 {resource.url}\n\n"
        return response
    
    else:
        # Generate intelligent educational response
        return generate_educational_response(question)


async def get_user_conversation_context(user_id: int, limit: int = 5) -> str:
    """
    Get the last N conversation messages for a user as a formatted string for Gemini context.
    This keeps the data in the database and only fetches what's needed.
    """
    try:
        from .database import get_postgres_db
        from .models import Question
        from sqlalchemy.orm import Session
        
        # Get database session
        db = next(get_postgres_db())
        
        # Get recent questions and answers for the user (limit to 5 Q&A pairs = 10 messages)
        recent_questions = db.query(Question).filter(
            Question.user_id == user_id
        ).order_by(Question.created_at.desc()).limit(limit).all()
        
        # Format as context string directly (no dictionary conversion)
        if not recent_questions:
            return ""
        
        context = "Previous conversation context:\n"
        for q in reversed(recent_questions):  # Reverse to get chronological order
            context += f"User: {q.question_text}\n"
            context += f"Assistant: {q.answer_text[:200]}...\n\n"  # Truncate long answers
        
        return context
        
    except Exception as e:
        print(f"Error getting conversation context: {e}")
        return ""


async def cleanup_old_conversation_history(user_id: int, keep_messages: int = 10):
    """
    Clean up old conversation history, keeping only the last N messages per user.
    This works directly with the database without loading data into memory.
    """
    try:
        from .database import get_postgres_db
        from .models import Question
        from sqlalchemy.orm import Session
        from sqlalchemy import text
        
        # Get database session
        db = next(get_postgres_db())
        
        # Use a single SQL query to delete old messages efficiently
        # This keeps the last N messages and deletes the rest
        delete_query = text("""
            DELETE FROM questions 
            WHERE user_id = :user_id 
            AND id NOT IN (
                SELECT id FROM questions 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT :keep_messages
            )
        """)
        
        result = db.execute(delete_query, {
            "user_id": user_id, 
            "keep_messages": keep_messages
        })
        
        db.commit()
        
        if result.rowcount > 0:
            print(f"Cleaned up {result.rowcount} old messages for user {user_id}")
        
    except Exception as e:
        print(f"Error cleaning up conversation history: {e}")


async def ask_question_with_ai(
    question: str, 
    user_id: Optional[int] = None,
    search_type: str = "semantic"
) -> AskResponse:
    """
    Ask a question and get AI-generated answer using intelligent search.
    
    Args:
        question: User's question
        user_id: ID of the user asking the question (optional)
        search_type: Type of search to perform
        
    Returns:
        AI-generated response with relevant resources
    """
    start_time = time.time()
    
    question_lower = question.lower().strip()
    
    # Simple greeting detection
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up", "thanks", "thank you"]
    is_greeting = any(greeting in question_lower for greeting in greetings)
    
    # AI intelligently decides whether to search for resources
    similar_resources = []
    
    # Check if question is asking for campus resources (be more specific)
    campus_resource_indicators = [
        "fitness", "gym", "exercise", "sports", "mental health", "counseling", "therapy",
        "library", "campus", "university", "texas tech", "ttu",
        "campus resources", "university services", "student services", "where can i find",
        "how to access", "available on campus", "campus center", "student center"
    ]
    
    # Only search if question contains campus resource indicators
    should_search = any(indicator in question_lower for indicator in campus_resource_indicators)
    
    if should_search:
        similar_resources = search_similar_resources(
            query=question,
            limit=3,
            score_threshold=0.3
        )
    
    # Generate AI answer
    if GEMINI_AVAILABLE:
        answer = generate_ai_answer_with_context(question, similar_resources, "", is_greeting)
    else:
        answer = generate_simple_answer(question, similar_resources)
    
    response_time = int((time.time() - start_time) * 1000)
    
    return AskResponse(
        question=question,
        answer=answer,
        relevant_resources=similar_resources,
        user_id=user_id,
        timestamp=time.time()
    )


def delete_resource_from_mongodb(resource_id: str):
    """
    Delete a resource from MongoDB Atlas.
    
    Args:
        resource_id: ID of the resource to delete
    """
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return False
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Delete document
        result = collection.delete_one({"_id": ObjectId(resource_id)})
        
        client.close()
        
        if result.deleted_count > 0:
            print(f"✅ Deleted resource {resource_id} from MongoDB Atlas")
            return True
        else:
            print(f"⚠️  Warning: Could not delete resource {resource_id} from MongoDB Atlas")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting resource {resource_id} from MongoDB Atlas: {e}")
        return False


def update_resource_in_mongodb(
    resource_id: str, 
    title: str, 
    description: str, 
    url: str,
    category: str = None,
    tags: List[str] = None,
    owner_id: int = None,
    is_public: bool = True
):
    """
    Update a resource in MongoDB Atlas.
    
    Args:
        resource_id: ID of the resource to update
        title: New title
        description: New description
        url: New URL
        category: New category
        tags: New tags
        owner_id: Owner ID
        is_public: Whether public
    """
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return False
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Generate new embedding
        combined_text = f"{title} {description or ''}"
        embedding = generate_embedding(combined_text)
        
        # Create updated MongoDB document
        update_doc = {
            "title": title,
            "description": description,
            "url": url,
            "category": category,
            "tags": tags or [],
            "owner_id": owner_id,
            "is_public": is_public,
            "embedding": embedding,
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Update document
        result = collection.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": update_doc}
        )
        
        client.close()
        
        if result.modified_count > 0:
            print(f"✅ Updated resource {resource_id} in MongoDB Atlas")
            return True
        else:
            print(f"⚠️  Warning: Could not update resource {resource_id} in MongoDB Atlas")
            return False
            
    except Exception as e:
        print(f"❌ Error updating resource {resource_id} in MongoDB Atlas: {e}")
        return False


def batch_process_resources(resources_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple resources in batch.
    
    Args:
        resources_data: List of resource data dictionaries
        
    Returns:
        List of created resource documents from MongoDB Atlas
    """
    created_resources = []
    
    for resource_data in resources_data:
        try:
            resource = store_resource_with_embedding(
                title=resource_data.get("title", ""),
                description=resource_data.get("description", ""),
                url=resource_data.get("url", ""),
                category=resource_data.get("category"),
                tags=resource_data.get("tags", []),
                owner_id=resource_data.get("owner_id"),
                is_public=resource_data.get("is_public", True)
            )
            if resource:
                created_resources.append(resource)
        except Exception as e:
            print(f"Error processing resource {resource_data.get('title', 'Unknown')}: {e}")
            continue
    
    return created_resources


def get_vector_database_status() -> Dict[str, Any]:
    """
    Get status of the vector database (MongoDB Atlas).
    
    Returns:
        Dictionary with vector database status information
    """
    return get_mongodb_atlas_status()


def get_mongodb_atlas_status() -> Dict[str, Any]:
    """
    Get status and statistics of MongoDB Atlas.
    
    Returns:
        Dictionary with database status information
    """
    mongodb_atlas = get_mongodb_atlas()
    
    if not mongodb_atlas.collection:
        return {"status": "not_connected", "error": "MongoDB Atlas not connected"}
    
    try:
        stats = mongodb_atlas.get_collection_stats()
        return {
            "status": "connected",
            "type": "mongodb_atlas",
            "collection_stats": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}