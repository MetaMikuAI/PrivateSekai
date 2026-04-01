using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Config;
using PrivateSekai.Crypto;

namespace PrivateSekai.Controllers;

[ApiController]
public class SuiteMasterFileController : ControllerBase
{
    private readonly ILogger<SuiteMasterFileController> _logger;

    public SuiteMasterFileController(ILogger<SuiteMasterFileController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// GET /api/suitemasterfile/{version}/{**filename}
    /// </summary>
    [HttpGet("api/suitemasterfile/{version}/{**filename}")]
    public async Task HandleSuiteMasterFile(string version, string filename)
    {
        var filePath = Path.Combine(ServerConfig.SuiteMasterFilePath, version, filename);

        if (!System.IO.File.Exists(filePath))
        {
            _logger.LogError("File not found: {FilePath}", filePath);
            Response.StatusCode = 404;
            await Response.WriteAsync("Not Found");
            return;
        }

        try
        {
            _logger.LogInformation("Serving file: {FilePath}", filePath);
            var json = await System.IO.File.ReadAllTextAsync(filePath);
            var encrypted = PrskCrypto.PrskEncFromJson(json);

            Response.ContentType = "application/octet-stream";
            Response.ContentLength = encrypted.Length;
            await Response.Body.WriteAsync(encrypted);
        }
        catch (OperationCanceledException)
        {
            // 客户端断开连接
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process file: {FilePath}", filePath);
            if (!Response.HasStarted)
            {
                Response.StatusCode = 500;
                await Response.WriteAsync("Failed to process file");
            }
        }
    }
}
