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

            // Try vector search first using your vector_index
            try
            {
                var queryEmbedding = await _embeddingService.GenerateEmbeddingAsync(searchQuery);

                var pipeline = new[]
                {
                    new BsonDocument("$vectorSearch", new BsonDocument
                    {
                        { "index", "vector_index" },
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

                if (results.Count > 0)
                {
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
            }
            catch (Exception vectorEx)
            {
                _logger.LogWarning(vectorEx, "Vector search failed, falling back to semantic search");
            }

            // Fallback to semantic search if vector search fails
            var fallbackQueryEmbedding = await _embeddingService.GenerateEmbeddingAsync(searchQuery);
            var allDocs = await collection.Find(FilterDefinition<BsonDocument>.Empty).ToListAsync();

            var fallbackResults = new List<(BsonDocument doc, double score)>();

            foreach (var doc in allDocs)
            {
                var title = GetStringValue(doc, "title");
                var description = GetStringValue(doc, "description");
                var category = GetStringValue(doc, "category");

                var docText = $"{title} {description} {category}";
                var docEmbedding = await _embeddingService.GenerateEmbeddingAsync(docText);
                var similarity = CalculateCosineSimilarity(fallbackQueryEmbedding, docEmbedding);

                if (similarity > 0.1)
                    fallbackResults.Add((doc, similarity));
            }

            return fallbackResults
                .OrderByDescending(x => x.score)
                .Take(3)
                .Select(x => new Dictionary<string, object>
                {
                    { "id", x.doc.GetValue("_id").ToString() },
                    { "title", GetStringValue(x.doc, "title") },
                    { "description", GetStringValue(x.doc, "description") },
                    { "url", GetStringValue(x.doc, "url") },
                    { "category", GetStringValue(x.doc, "category") },
                    { "score", Math.Round(x.score, 3) }
                })
                .Cast<object>()
                .ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching resources: {Query}", searchQuery);
            return new List<object>();
        }
    }


    private double CalculateCosineSimilarity(double[] vector1, double[] vector2)
    {
        if (vector1.Length != vector2.Length) return 0;

        double dotProduct = 0, magnitude1 = 0, magnitude2 = 0;

        for (int i = 0; i < vector1.Length; i++)
        {
            dotProduct += vector1[i] * vector2[i];
            magnitude1 += vector1[i] * vector1[i];
            magnitude2 += vector2[i] * vector2[i];
        }

        return magnitude1 == 0 || magnitude2 == 0 ? 0 : dotProduct / (Math.Sqrt(magnitude1) * Math.Sqrt(magnitude2));
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

