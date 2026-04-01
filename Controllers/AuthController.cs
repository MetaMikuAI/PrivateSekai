using MessagePack;
using Microsoft.AspNetCore.Mvc;

using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class AuthController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<AuthController> _logger;

    public AuthController(UserManager users, ILogger<AuthController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// PUT /api/user/{userId}/auth
    /// 客户端通过 credential 换取 sessionToken
    /// </summary>
    [HttpPut("api/user/{userId}/auth")]
    public async Task<IActionResult> HandleAuthUser(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserAuthRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var credential = requestData.credential;
        if (string.IsNullOrEmpty(credential))
            return BadRequest("Missing credential");

        if (!JwtSignature.VerifyCredential(credential, userId))
        {
            _logger.LogError("Invalid credential for user {UserId}", userId);
            return Unauthorized("Invalid credential");
        }

        _logger.LogInformation("User {UserId} authenticated", userId);

        var responseData = MessagePackSerializer.Deserialize<UserAuthResponse>(
            MessagePackSerializer.Serialize(_users.ApiUserAuth));
        responseData.sessionToken = JwtSignature.GenSessionToken(userId);
        responseData.updatedResources = null;

        return PrskResponse(responseData);
    }

    /// <summary>
    /// GET /api/system 获取可用版本
    /// </summary>
    [HttpGet("api/system")]
    public IActionResult HandleSystemInfo()
    {
        var responseData = MessagePackSerializer.Deserialize<SystemResponse>(
            MessagePackSerializer.Serialize(_users.ApiSystem));
        responseData.serverDate = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        return PrskResponse(responseData);
    }
}
