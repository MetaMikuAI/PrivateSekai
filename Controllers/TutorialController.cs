using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class TutorialController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<TutorialController> _logger;

    public TutorialController(UserManager users, ILogger<TutorialController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// PATCH /api/user/{userId}/tutorial — 更新新手引导进度
    /// </summary>
    [HttpPatch("api/user/{userId}/tutorial")]
    public async Task<IActionResult> HandleTutorialUpdate(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserTutorialRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var tutorialStatus = requestData.tutorialStatus;
        if (string.IsNullOrEmpty(tutorialStatus))
            return BadRequest("Missing tutorialStatus");

        _logger.LogInformation("User {UserId} updated tutorial status to `{Status}`", userId, tutorialStatus);

        var user = _users.GetUser(userId);
        user.UpdateTutorialProgress(tutorialStatus);

        var responseData = new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// PATCH /api/user/{userId} — 更新用户名（新手引导中设名字）
    /// </summary>
    [HttpPatch("api/user/{userId}")]
    public async Task<IActionResult> HandleUserUpdate(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserNameRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var newName = requestData.userGamedata?.name;
        if (string.IsNullOrEmpty(newName))
            return BadRequest("Missing name in userGamedata");

        var user = _users.GetUser(userId);
        user.UpdateUserName(newName);
        user.UpdateRefreshableTypes("userGamedata");

        _logger.LogInformation("User {UserId} gamedata updated", userId);

        var responseData = new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }
}
