using MessagePack;
using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

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
    /// </summary>
    [HttpPut("api/user/{userId}/auth")]
    public IActionResult HandleAuthUser(long userId, [FromBody] UserAuthRequest request)
    {
        if (string.IsNullOrEmpty(request.credential))
            return BadRequest("Missing credential");

        if (!JwtSignature.VerifyCredential(request.credential, userId))
        {
            _logger.LogError("Invalid credential for user {UserId}", userId);
            return Unauthorized("Invalid credential");
        }

        _logger.LogInformation("User {UserId} authenticated", userId);

        var responseData = MessagePackSerializer.Deserialize<UserAuthResponse>(
            MessagePackSerializer.Serialize(_users.ApiUserAuth));
        responseData.sessionToken = JwtSignature.GenSessionToken(userId);
        responseData.updatedResources = null;

        return Ok(responseData);
    }

    /// <summary>
    /// GET /api/system
    /// </summary>
    [HttpGet("api/system")]
    public IActionResult HandleSystemInfo()
    {
        var responseData = MessagePackSerializer.Deserialize<SystemResponse>(
            MessagePackSerializer.Serialize(_users.ApiSystem));
        responseData.serverDate = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        return Ok(responseData);
    }
}
