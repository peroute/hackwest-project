using System.Text;
using System.Text.Json;
using TTUAgent.ApiService.Models;
using MongoDB.Bson;
using MongoDB.Driver;

namespace TTUAgent.ApiService.Services;

public class GeminiService : IGeminiService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;
    private readonly ILogger<GeminiService> _logger;
    private readonly ISearchService _searchService;
    private readonly string _apiKey;
    private readonly string _baseUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent";

    public GeminiService(HttpClient httpClient, IConfiguration configuration, ILogger<GeminiService> logger, ISearchService searchService)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        _logger = logger;
        _searchService = searchService;

        _apiKey = configuration["Gemini:ApiKey"] ?? throw new InvalidOperationException("Gemini API key is not configured. Please set the 'Gemini:ApiKey' configuration value.");
    }

    public async Task<string> GenerateTextAsync(string prompt)
    {
        try
        {
            _logger.LogInformation("Generating text with Gemini for prompt: {Prompt}", prompt);

            var systemPrompt = @"You are a TTU (Texas Tech University) agent that helps students, faculty, and staff find educational resources and information. You have access to a comprehensive database of university resources.

When the user wants to search for resources, courses, departments, services, or anything related to Texas Tech University, always reply with a JSON object in the following format:
{
  ""isSearching"": true,
  ""action"": ""search_resources"",
  ""searchQuery"": ""..."",
  ""userMessage"": ""..."",
  ""resourcesNeeded"": true
}

When users are just casually talking or asking general questions, reply with:
{
  ""isSearching"": false,
  ""action"": ""casual_chat"",
  ""userMessage"": ""..."",
  ""resourcesNeeded"": false
}

""userMessage"" is your response to the user. Keep it helpful, educational, and focused on Texas Tech University.
If the user is searching for resources, mention that you'll help them find the relevant information.
If it's casual chat, respond naturally but keep it educational and university-related.

Do not include any other text outside the JSON object.";

            var fullPrompt = systemPrompt + "\n\nUser query: " + prompt;

            var request = new GeminiRequest
            {
                Contents = new List<Content>
                {
                    new Content
                    {
                        Parts = new List<Part>
                        {
                            new Part { Text = fullPrompt }
                        }
                    }
                }
            };

            var response = await CallGeminiApiAsync(request);

            _logger.LogInformation("Successfully generated text with Gemini");
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating text with Gemini for prompt: {Prompt}", prompt);
            throw;
        }
    }


    private async Task<string> CallGeminiApiAsync(GeminiRequest request)
    {
        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var url = $"{_baseUrl}?key={_apiKey}";
        var response = await _httpClient.PostAsync(url, content);

        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync();
            throw new HttpRequestException($"Gemini API call failed with status {response.StatusCode}: {errorContent}");
        }

        var responseContent = await response.Content.ReadAsStringAsync();
        var geminiResponse = JsonSerializer.Deserialize<GeminiResponse>(responseContent);

        if (geminiResponse?.Candidates?.FirstOrDefault()?.Content?.Parts?.FirstOrDefault()?.Text == null)
        {
            throw new InvalidOperationException("No valid response received from Gemini API");
        }

        var initialResponse = geminiResponse.Candidates.First().Content.Parts.First().Text;

        // Try to parse the JSON response to check if it's a search request
        try
        {
            var cleanedJson = initialResponse
            .Replace("```json", "")
            .Replace("```", "")
            .Trim();

            using var jsonDoc = JsonDocument.Parse(cleanedJson);
            var root = jsonDoc.RootElement;

            // Check if it's a search request
            bool isSearching = root.TryGetProperty("isSearching", out var isSearchingProp) && isSearchingProp.GetBoolean();

            if (isSearching)
            {
                _logger.LogInformation("Search request detected, performing MongoDB search");

                // Get search query from the response
                var searchQuery = root.TryGetProperty("searchQuery", out var query) ? query.GetString() : "";

                // Search for relevant resources using SearchService (returns top 3)
                var searchResults = await _searchService.SearchResourcesAsync(searchQuery);

                // Get the user message from Gemini's response
                var userMessage = root.TryGetProperty("userMessage", out var message) ? message.GetString() : "";

                // Create a simple message with search results
                if (searchResults.Count > 0)
                {
                    var resultsText = string.Join("\n\n", searchResults.Select((result, index) =>
                    {
                        if (result is Dictionary<string, object> dict)
                        {
                            var title = dict.GetValueOrDefault("title", "Resource");
                            var description = dict.GetValueOrDefault("description", "");
                            var url = dict.GetValueOrDefault("url", "");
                            var score = dict.GetValueOrDefault("score", 0);
                            return $"**{index + 1}. [{title}]({url})**\n{description}\n*Relevance: {score:F1}*";
                        }
                        return $"**{index + 1}. Resource**";
                    }));

                    return $"{userMessage}\n\nHere are the best resources I found:\n\n{resultsText}";
                }
                else
                {
                    return $"{userMessage}\n\nI couldn't find any specific resources for your search. Please try different keywords or ask me something else!";
                }
            }
            else
            {
                // Return just the message content for casual chat
                var userMessage = root.TryGetProperty("message", out var message) ? message.GetString() : initialResponse;
                return userMessage ?? initialResponse;
            }
        }
        catch (JsonException ex)
        {
            _logger.LogWarning(ex, "Failed to parse JSON response, returning as plain text: {Response}", initialResponse);
            // If it's not valid JSON, return as plain text
            return initialResponse;
        }
    }


}
