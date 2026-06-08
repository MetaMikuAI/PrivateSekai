using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class MiscController : PrskController
{
    private readonly UserManager _users;

    public MiscController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// PUT /api/user/{userId}/topic/{topicId}
    /// </summary>
    [HttpPut("api/user/{userId}/topic/{topicId}")]
    public IActionResult HandleTopic(long userId, int topicId)
    {
        var user = _users.GetUser(userId);
        user.RemoveTopic(topicId);
        var responseData = new TopicResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// PUT /api/user/{userId}/appeal
    /// </summary>
    [HttpPut("api/user/{userId}/appeal")]
    public async Task<IActionResult> HandleAppeal(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserAppealRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.MarkAppealsViewed(requestData.appealIds);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// POST /api/user/{userId}/{uuid} — 通用 stub，返回 200
    /// </summary>
    [HttpPost("api/user/{userId}/{uuid}")]
    public IActionResult HandleUuidEndpoint(long userId, string uuid)
    {
        return Ok();
    }
}
