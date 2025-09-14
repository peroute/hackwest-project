using System.Text.Json.Serialization;

namespace TTUAgent.ApiService.Models;

public class GeminiRequest
{
    [JsonPropertyName("contents")]
    public List<Content> Contents { get; set; } = new();
}

public class Content
{
    [JsonPropertyName("parts")]
    public List<Part> Parts { get; set; } = new();
}

public class Part
{
    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;
}

public class GeminiResponse
{
    [JsonPropertyName("candidates")]
    public List<Candidate> Candidates { get; set; } = new();
}

public class Candidate
{
    [JsonPropertyName("content")]
    public Content Content { get; set; } = new();

    [JsonPropertyName("finishReason")]
    public string FinishReason { get; set; } = string.Empty;
}
