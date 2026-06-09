using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

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

        return Ok(new TopicResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// PUT /api/user/{userId}/appeal
    /// </summary>
    [HttpPut("api/user/{userId}/appeal")]
    public IActionResult HandleAppeal(long userId, [FromBody] UserAppealRequest request)
    {
        var user = _users.GetUser(userId);
        user.MarkAppealsViewed(request.appealIds);

        return Ok(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// POST /api/user/{userId}/{uuid}
    /// </summary>
    [HttpPost("api/user/{userId}/{uuid}")]
    public IActionResult HandleUuidEndpoint(long userId, string uuid) => Ok();
}
