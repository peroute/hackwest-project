using TTUAgent.ApiService.Services;

var builder = WebApplication.CreateBuilder(args);


var configuration = new ConfigurationBuilder()
    .SetBasePath(builder.Environment.ContentRootPath)
    .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
    .Build();

builder.Services.AddScoped<MongoConnectionService>(provider =>
{
    var configuration = provider.GetRequiredService<IConfiguration>();
    var logger = provider.GetRequiredService<ILogger<MongoConnectionService>>();
    return new MongoConnectionService(configuration, logger);
});

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddControllers();
builder.Services.AddScoped<IGeminiService, GeminiService>();
builder.Services.AddScoped<ISearchService, SearchService>();
builder.Services.AddScoped<IEmbeddingService, EmbeddingService>();
// Register HttpClient for OpenAI
builder.Services.AddHttpClient();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthorization();

app.MapControllers();

app.Run();