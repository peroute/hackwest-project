using TTUAgent.ApiService.Models;

namespace TTUAgent.ApiService.Services;

public interface ISearchService
{
    Task<List<object>> SearchResourcesAsync(string searchQuery);
    //Task<double[]> GetEmbeddingAsync(string text);
    //Task<List<object>> PerformVectorSearchAsync(double[] queryEmbedding, int limit = 5);
}
