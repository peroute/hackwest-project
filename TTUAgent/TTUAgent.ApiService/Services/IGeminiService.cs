namespace TTUAgent.ApiService.Services;

public interface IGeminiService
{
    Task<string> GenerateTextAsync(string prompt);
}
