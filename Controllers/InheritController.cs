using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class InheritController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<InheritController> _logger;

    public InheritController(UserManager users, ILogger<InheritController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// GET /api/user/{userId}/restrict-info
    /// </summary>
    [HttpGet("api/user/{userId}/restrict-info")]
    public IActionResult HandleRestrictInfo(long userId)
    {
        var responseData = new RestrictInfoResponse
        {
            isRestrictDeviceTransfer = false
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// PUT /api/user/{userId}/inherit — 设置引继码
    /// </summary>
    [HttpPut("api/user/{userId}/inherit")]
    public async Task<IActionResult> HandleSetInherit(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserInheritRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var password = requestData.password;
        if (string.IsNullOrEmpty(password))
            return BadRequest("Missing password");

        var user = _users.GetUser(userId);
        var inheritId = user.SetUserInherit(password);

        _logger.LogInformation("User {UserId} set inherit ID {InheritId}", userId, inheritId);

        var responseData = new UserInheritSetResponse
        {
            updatedResources = user.GetRefreshData(),
            userInherit = new UserInherit { inheritId = inheritId }
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// POST /api/inherit/user/{inheritId} — 执行账号引继
    /// </summary>
    [HttpPost("api/inherit/user/{inheritId}")]
    public IActionResult HandleInheritUser(string inheritId)
    {
        var isExecuteInherit = Request.Query["isExecuteInherit"].ToString();
        if (string.IsNullOrEmpty(isExecuteInherit))
            return BadRequest("Missing isExecuteInherit parameter");

        if (isExecuteInherit != "True" && isExecuteInherit != "False")
            return BadRequest("Invalid isExecuteInherit parameter value");

        var inheritToken = Request.Headers["X-Inherit-Id-Verify-Token"].ToString();
        if (string.IsNullOrEmpty(inheritToken))
            return BadRequest("Missing X-Inherit-Id-Verify-Token header");

        var inheritData = JwtSignature.VerifyToken(inheritToken);
        if (inheritData == null
            || !inheritData.TryGetValue("inheritId", out var iid)
            || iid?.ToString() != inheritId)
        {
            return Unauthorized("Invalid inherit token or inherit ID mismatch");
        }

        if (!inheritData.TryGetValue("password", out var pwd) || pwd == null)
            return BadRequest("Missing password");

        var password = pwd.ToString()!;

        long? matchedUserId = null;
        GameUser? matchedUser = null;

        foreach (var (uid, user) in _users.GetAllUsers())
        {
            if (user.VerifyInherit(inheritId, password))
            {
                matchedUserId = uid;
                matchedUser = user;
                break;
            }
        }

        if (matchedUser == null || matchedUserId == null)
        {
            _logger.LogWarning("Inherit ID {InheritId} with provided password not found", inheritId);
            return Unauthorized("Invalid inherit ID or password");
        }

        _logger.LogInformation("User {UserId} inherited account with inherit ID {InheritId}",
            matchedUserId, inheritId);

        var responseData = new InheritExecuteResponse
        {
            afterUserGamedata = matchedUser.GetAfterUserGamedata(),
            userEventDeviceTransferRestrict = new RestrictInfoResponse
            {
                isRestrictDeviceTransfer = false
            }
        };

        if (isExecuteInherit == "True")
            responseData.credential = JwtSignature.GenUserCredential(matchedUserId.Value);

        return PrskResponse(responseData);
    }
}
