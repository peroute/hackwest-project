using System.Text;
using System.Text.Json;

namespace TTUAgent.ApiService.Services;

public interface IEmbeddingService
{
    Task<double[]> GenerateEmbeddingAsync(string text);
    Task<List<double[]>> GenerateEmbeddingsAsync(List<string> texts);
}

public class EmbeddingService : IEmbeddingService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<EmbeddingService> _logger;
    private readonly string _apiUrl = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2";

    public EmbeddingService(HttpClient httpClient, ILogger<EmbeddingService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<double[]> GenerateEmbeddingAsync(string text)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(text))
                return new double[384];

            // Use local embedding generation for now
            return GenerateFallbackEmbedding(text);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating embedding for text: {Text}", text);
            return new double[384];
        }
    }

    public async Task<List<double[]>> GenerateEmbeddingsAsync(List<string> texts)
    {
        var embeddings = new List<double[]>();

        foreach (var text in texts)
        {
            var embedding = await GenerateEmbeddingAsync(text);
            embeddings.Add(embedding);
        }

        return embeddings;
    }

    private double[] GenerateFallbackEmbedding(string text)
    {
        var words = text.ToLowerInvariant()
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 2)
            .ToArray();

        var embedding = new double[384];
        var textHash = Math.Abs(text.GetHashCode());
        var random = new Random(textHash);

        // Create semantic features based on text content
        var semanticFeatures = new Dictionary<string, double>
        {
            {"academic", 0}, {"research", 0}, {"library", 0}, {"gym", 0}, {"fitness", 0},
            {"dining", 0}, {"food", 0}, {"hours", 0}, {"time", 0}, {"schedule", 0},
            {"location", 0}, {"building", 0}, {"center", 0}, {"facility", 0}, {"service", 0}
        };

        // Analyze text for semantic features
        foreach (var word in words)
        {
            foreach (var feature in semanticFeatures.Keys.ToList())
            {
                if (word.Contains(feature) || CalculateSimilarity(word, feature) > 0.7)
                {
                    semanticFeatures[feature] += 1.0;
                }
            }
        }

        // Generate embedding based on semantic features
        for (int i = 0; i < embedding.Length; i++)
        {
            embedding[i] = (random.NextDouble() * 2 - 1) * 0.1;
        }

        // Add semantic feature influence
        int featureIndex = 0;
        foreach (var feature in semanticFeatures.Values)
        {
            if (feature > 0)
            {
                for (int i = 0; i < 20; i++)
                {
                    var dimension = (featureIndex * 20 + i) % embedding.Length;
                    embedding[dimension] += feature * 0.1;
                }
            }
            featureIndex++;
        }

        return NormalizeEmbedding(embedding);
    }

    private double CalculateSimilarity(string word1, string word2)
    {
        if (word1 == word2) return 1.0;
        if (word1.Length == 0 || word2.Length == 0) return 0.0;

        var longer = word1.Length > word2.Length ? word1 : word2;
        var shorter = word1.Length > word2.Length ? word2 : word1;

        var editDistance = LevenshteinDistance(word1, word2);
        return (longer.Length - editDistance) / (double)longer.Length;
    }

    private int LevenshteinDistance(string s1, string s2)
    {
        var matrix = new int[s1.Length + 1, s2.Length + 1];

        for (int i = 0; i <= s1.Length; i++) matrix[i, 0] = i;
        for (int j = 0; j <= s2.Length; j++) matrix[0, j] = j;

        for (int i = 1; i <= s1.Length; i++)
        {
            for (int j = 1; j <= s2.Length; j++)
            {
                var cost = s1[i - 1] == s2[j - 1] ? 0 : 1;
                matrix[i, j] = Math.Min(
                    Math.Min(matrix[i - 1, j] + 1, matrix[i, j - 1] + 1),
                    matrix[i - 1, j - 1] + cost);
            }
        }

        return matrix[s1.Length, s2.Length];
    }

    private double[] NormalizeEmbedding(double[] embedding)
    {
        // L2 normalization
        var magnitude = Math.Sqrt(embedding.Sum(x => x * x));

        if (magnitude > 0)
        {
            for (int i = 0; i < embedding.Length; i++)
            {
                embedding[i] /= magnitude;
            }
        }

        return embedding;
    }
}
