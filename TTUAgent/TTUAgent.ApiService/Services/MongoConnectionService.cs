using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MongoDB.Driver;

namespace TTUAgent.ApiService.Services;

public class MongoConnectionService
{
    private readonly IMongoDatabase _database;
    private readonly ILogger<MongoConnectionService> _logger;

    public MongoConnectionService(IConfiguration configuration, ILogger<MongoConnectionService> logger)
    {
        _logger = logger;

        var connectionString = configuration["MongoDB:ConnectionString"];
        var databaseName = configuration["MongoDB:DatabaseName"];

        if (string.IsNullOrEmpty(connectionString))
        {
            throw new InvalidOperationException("MongoDB connection string is not configured.");
        }

        if (string.IsNullOrEmpty(databaseName))
        {
            throw new InvalidOperationException("MongoDB database name is not configured.");
        }

        var client = new MongoClient(connectionString);
        _database = client.GetDatabase(databaseName);

        _logger.LogInformation("MongoDB connection established to database: {DatabaseName}", databaseName);
    }

    public IMongoDatabase GetDatabase()
    {
        return _database;
    }

    public IMongoCollection<T> GetCollection<T>(string collectionName)
    {
        return _database.GetCollection<T>(collectionName);
    }
}
