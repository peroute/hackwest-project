using MongoDB.Bson;
using MongoDB.Driver;
using TTUAgent.ApiService.Models;

namespace TTUAgent.ApiService.Services;

public class SearchService : ISearchService
{
    private readonly MongoConnectionService _mongoService;
    private readonly ILogger<SearchService> _logger;
    private readonly IEmbeddingService _embeddingService;

    public SearchService(MongoConnectionService mongoService, ILogger<SearchService> logger, IEmbeddingService embeddingService)
    {
        _mongoService = mongoService;
        _logger = logger;
        _embeddingService = embeddingService;
    }

    public async Task<List<object>> SearchResourcesAsync(string searchQuery)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(searchQuery))
                return new List<object>();

            var collection = _mongoService.GetCollection<BsonDocument>("resources");

            // Generate embedding for the search query
            var queryEmbedding = await _embeddingService.GenerateEmbeddingAsync(searchQuery);

            // Run vector search using MongoDB $vectorSearch
            var pipeline = new[]
            {
                new BsonDocument("$vectorSearch", new BsonDocument
                {
                    { "index", "embeddingIndex" },
                    { "path", "embedding" },
                    { "queryVector", new BsonArray(queryEmbedding) },
                    { "numCandidates", 100 },
                    { "limit", 3 }
                }),
                new BsonDocument("$project", new BsonDocument
                {
                    { "title", 1 },
                    { "description", 1 },
                    { "category", 1 },
                    { "url", 1 },
                    { "score", new BsonDocument("$meta", "vectorSearchScore") }
                })
            };

            var results = await collection.Aggregate<BsonDocument>(pipeline).ToListAsync();

            return results.Select(doc => new Dictionary<string, object>
            {
                { "id", doc.GetValue("_id").ToString() },
                { "title", GetStringValue(doc, "title") },
                { "description", GetStringValue(doc, "description") },
                { "url", GetStringValue(doc, "url") },
                { "category", GetStringValue(doc, "category") },
                { "score", Math.Round(doc.GetValue("score", 0.0).ToDouble(), 3) }
            }).Cast<object>().ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching resources: {Query}", searchQuery);
            return new List<object>();
        }
    }


    private string GetStringValue(BsonDocument doc, string fieldName)
    {
        try
        {
            var value = doc.GetValue(fieldName, BsonNull.Value);
            return value.IsBsonNull ? "" : value.AsString;
        }
        catch
        {
            return "";
        }
    }
}

