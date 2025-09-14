using Microsoft.AspNetCore.Mvc;
using MongoDB.Bson;
using MongoDB.Driver;
using TTUAgent.ApiService.Services;

namespace TTUAgent.ApiService.Controllers;

[ApiController]
[Route("api/[controller]")]
public class GeminiController : ControllerBase
{
    private readonly IGeminiService _geminiService;
    private readonly MongoConnectionService _mongoService;
    private readonly ILogger<GeminiController> _logger;
    private readonly ISearchService _searchService;

    public GeminiController(IGeminiService geminiService, MongoConnectionService mongoService, ILogger<GeminiController> logger, ISearchService searchService)
    {
        _geminiService = geminiService;
        _mongoService = mongoService;
        _logger = logger;
        _searchService = searchService;
    }

    [HttpPost("generate")]
    public async Task<IActionResult> GenerateText([FromBody] GenerateTextRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Prompt))
            {
                return BadRequest("Prompt cannot be empty");
            }

            var result = await _geminiService.GenerateTextAsync(request.Prompt);
            return Ok(new { text = result });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating text with Gemini");
            return StatusCode(500, "An error occurred while generating text");
        }
    }

    [HttpGet("test-connection")]
    public async Task<IActionResult> TestConnection()
    {
        try
        {
            _logger.LogInformation("Testing MongoDB connection");

            var database = _mongoService.GetDatabase();
            var collections = await database.ListCollectionNamesAsync();
            var collectionNames = await collections.ToListAsync();

            // Get document count for each collection
            var collectionInfo = new List<object>();
            foreach (var collectionName in collectionNames)
            {
                var collection = _mongoService.GetCollection<BsonDocument>(collectionName);
                var count = await collection.CountDocumentsAsync(FilterDefinition<BsonDocument>.Empty);
                collectionInfo.Add(new { name = collectionName, documentCount = count });
            }

            _logger.LogInformation("Connection test successful. Found {Count} collections", collectionNames.Count);
            return Ok(new
            {
                status = "Connected",
                database = "university_resources",
                collections = collectionInfo,
                message = $"Successfully connected to university_resources database with {collectionNames.Count} collections"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Connection test failed: {Error}", ex.Message);
            return StatusCode(500, new
            {
                status = "Failed",
                error = "Connection test failed",
                details = ex.Message
            });
        }
    }

    [HttpGet("collections")]
    public async Task<IActionResult> GetCollections()
    {
        try
        {
            _logger.LogInformation("Getting all collections from university_resources database");

            var database = _mongoService.GetDatabase();
            var collections = await database.ListCollectionNamesAsync();
            var collectionNames = await collections.ToListAsync();

            _logger.LogInformation("Found {Count} collections in university_resources database", collectionNames.Count);
            return Ok(new
            {
                database = "university_resources",
                collections = collectionNames,
                message = $"Found {collectionNames.Count} collections"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting collections: {Error}", ex.Message);
            return StatusCode(500, new { error = "An error occurred while getting collections", details = ex.Message });
        }
    }

    [HttpGet("collection/{collectionName}")]
    public async Task<IActionResult> GetCollectionData(string collectionName)
    {
        try
        {
            _logger.LogInformation("Retrieving data from collection: {CollectionName}", collectionName);

            var collection = _mongoService.GetCollection<BsonDocument>(collectionName);
            var documents = await collection.Find(FilterDefinition<BsonDocument>.Empty).ToListAsync();

            _logger.LogInformation("Successfully retrieved {Count} documents from collection: {CollectionName}", documents.Count, collectionName);
            return Ok(new
            {
                database = "university_resources",
                collection = collectionName,
                count = documents.Count,
                data = documents,
                message = $"Retrieved {documents.Count} documents from {collectionName} collection"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving data from collection {CollectionName}: {Error}", collectionName, ex.Message);
            return StatusCode(500, new { error = $"An error occurred while retrieving data from {collectionName}", details = ex.Message });
        }
    }

    [HttpPost("test-search")]
    public async Task<IActionResult> TestSearch([FromBody] TestSearchRequest request)
    {
        try
        {
            _logger.LogInformation("Testing search with query: {Query}", request.Query);

            // Test the search service directly
            var searchResults = await _searchService.SearchResourcesAsync(request.Query);

            return Ok(new
            {
                query = request.Query,
                results = searchResults,
                totalResults = searchResults.Count,
                message = $"Search completed successfully. Found {searchResults.Count} results."
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error testing search for query: {Query}", request.Query);
            return StatusCode(500, new { error = "An error occurred while testing search", details = ex.Message });
        }
    }

    [HttpGet("search-status")]
    public async Task<IActionResult> GetSearchStatus()
    {
        try
        {
            _logger.LogInformation("Checking search status and database connection");

            var collection = _mongoService.GetCollection<BsonDocument>("resources");

            // Get total document count
            var totalCount = await collection.CountDocumentsAsync(FilterDefinition<BsonDocument>.Empty);

            // Get count of documents with embeddings
            var embeddingCount = await collection.CountDocumentsAsync(Builders<BsonDocument>.Filter.Exists("embedding"));

            // Get a sample document to check structure
            var sampleDoc = await collection.Find(FilterDefinition<BsonDocument>.Empty).FirstOrDefaultAsync();

            var status = new
            {
                databaseConnected = true,
                totalDocuments = totalCount,
                documentsWithEmbeddings = embeddingCount,
                hasSampleDocument = sampleDoc != null,
                sampleDocumentFields = sampleDoc?.Names?.ToList() ?? new List<string>(),
                message = totalCount == 0 ? "No documents found in database. Please upload some resources first." :
                         embeddingCount == 0 ? "No documents with embeddings found. Vector search requires documents to have 'embedding' field." :
                         "Database is ready for vector search."
            };

            return Ok(status);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking search status");
            return StatusCode(500, new { error = "An error occurred while checking search status", details = ex.Message });
        }
    }

    [HttpDelete("clear-database")]
    public async Task<IActionResult> ClearDatabase()
    {
        try
        {
            _logger.LogInformation("Clearing all data from MongoDB Atlas");

            var collection = _mongoService.GetCollection<BsonDocument>("ttu_resources");
            var result = await collection.DeleteManyAsync(FilterDefinition<BsonDocument>.Empty);

            _logger.LogInformation("Successfully cleared {Count} documents from MongoDB Atlas", result.DeletedCount);
            return Ok(new { message = $"Successfully cleared {result.DeletedCount} documents from MongoDB Atlas" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error clearing database");
            return StatusCode(500, "An error occurred while clearing the database");
        }
    }

}

public record GenerateTextRequest(string Prompt);
public record TestSearchRequest(string Query);