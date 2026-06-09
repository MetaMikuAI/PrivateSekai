using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

public class LoginController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<LoginController> _logger;

    public LoginController(UserManager users, ILogger<LoginController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// POST /api/user — 注册新用户
    /// </summary>
    [HttpPost("api/user")]
    public IActionResult HandleRegisterUser([FromBody] UserAuthRequest _)
    {
        var newUserId = _users.ForkNewUser();
        var user = _users.GetUser(newUserId);
        _logger.LogInformation("New user registered: ID={UserId}", newUserId);

        var suiteData = user.GetSuiteUserData();

        return Ok(new UserAPIResponse
        {
            userRegistration = suiteData.userRegistration,
            credential = JwtSignature.GenUserCredential(newUserId),
            updatedResources = suiteData
        });
    }

    /// <summary>
    /// GET /api/suite/user/{userId}
    /// </summary>
    [HttpGet("api/suite/user/{userId}")]
    public IActionResult HandleSuiteUser(long userId)
    {
        var user = _users.UserExists(userId)
            ? _users.GetUser(userId)
            : _users.GetUser(0);

        return Ok(user.GetSuiteUserData());
    }

    /// <summary>
    /// GET /api/suite/user/{userId}/parts?name=...
    /// </summary>
    [HttpGet("api/suite/user/{userId}/parts")]
    public IActionResult HandleSuiteUserParts(long userId, [FromQuery(Name = "name")] string[]? names)
    {
        var user = _users.UserExists(userId)
            ? _users.GetUser(userId)
            : _users.GetUser(0);

        return Ok(user.GetSuiteUserParts(names));
    }
}
