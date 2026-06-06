using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Config;
using PrivateSekai.Crypto;
using System.Collections.Concurrent;

namespace PrivateSekai.Controllers;

[ApiController]
public class SuiteMasterFileController : ControllerBase
{
    private static readonly ConcurrentDictionary<string, SemaphoreSlim> CacheLocks = new();

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
            var cachePath = await GetEncryptedCachePathAsync(filePath, version, filename);
            var cacheInfo = new FileInfo(cachePath);

            Response.ContentType = "application/octet-stream";
            Response.ContentLength = cacheInfo.Length;

            _logger.LogInformation(
                "Serving encrypted suite master file: {FilePath} -> {CachePath} ({Length} bytes)",
                filePath,
                cachePath,
                cacheInfo.Length);

            await using var stream = System.IO.File.OpenRead(cachePath);
            await stream.CopyToAsync(Response.Body, HttpContext.RequestAborted);
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

    private async Task<string> GetEncryptedCachePathAsync(string filePath, string version, string filename)
    {
        var cachePath = BuildEncryptedCachePath(version, filename);
        var cacheLock = CacheLocks.GetOrAdd(cachePath, _ => new SemaphoreSlim(1, 1));

        await cacheLock.WaitAsync(HttpContext.RequestAborted);
        try
        {
            if (IsEncryptedCacheFresh(filePath, cachePath))
                return cachePath;

            Directory.CreateDirectory(Path.GetDirectoryName(cachePath)!);

            var tempPath = $"{cachePath}.{Environment.ProcessId}.{Guid.NewGuid():N}.tmp";
            try
            {
                _logger.LogInformation("Building encrypted suite master cache: {FilePath} -> {CachePath}", filePath, cachePath);
                await using (var source = System.IO.File.OpenRead(filePath))
                await using (var destination = System.IO.File.Create(tempPath))
                {
                    PrskCrypto.PrskEncJsonStreamToStream(source, destination);
                }

                if (System.IO.File.Exists(cachePath))
                    System.IO.File.Delete(cachePath);
                System.IO.File.Move(tempPath, cachePath);

                var sourceInfo = new FileInfo(filePath);
                System.IO.File.SetLastWriteTimeUtc(cachePath, sourceInfo.LastWriteTimeUtc);
                return cachePath;
            }
            finally
            {
                if (System.IO.File.Exists(tempPath))
                    System.IO.File.Delete(tempPath);
            }
        }
        finally
        {
            cacheLock.Release();
        }
    }

    private static string BuildEncryptedCachePath(string version, string filename)
    {
        var cacheRoot = Path.Combine(ServerConfig.SuiteMasterFilePath, ".encrypted-cache");
        return Path.Combine(cacheRoot, version, filename);
    }

    private static bool IsEncryptedCacheFresh(string sourcePath, string cachePath)
    {
        if (!System.IO.File.Exists(cachePath))
            return false;

        var sourceInfo = new FileInfo(sourcePath);
        var cacheInfo = new FileInfo(cachePath);
        if (cacheInfo.Length == 0)
            return false;

        return cacheInfo.LastWriteTimeUtc >= sourceInfo.LastWriteTimeUtc;
    }
}
