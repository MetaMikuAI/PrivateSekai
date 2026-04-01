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
    /// POST /api/user/{userId}/{uuid} — 通用 stub，返回 200
    /// </summary>
    [HttpPost("api/user/{userId}/{uuid}")]
    public IActionResult HandleUuidEndpoint(long userId, string uuid)
    {
        return Ok();
    }
}
