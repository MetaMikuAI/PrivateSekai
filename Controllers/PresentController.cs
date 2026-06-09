using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

public class PresentController : PrskController
{
    private readonly UserManager _users;

    public PresentController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// GET /api/user/{userId}/present/history
    /// </summary>
    [HttpGet("api/user/{userId}/present/history")]
    public IActionResult HandlePresentHistory(long userId)
    {
        var user = _users.GetUser(userId);
        return Ok(new UserPresentHistoriesResponse
        {
            userPresentHistories = user.GetPresentHistory()
        });
    }

    /// <summary>
    /// POST /api/user/{userId}/present
    /// </summary>
    [HttpPost("api/user/{userId}/present")]
    public IActionResult HandleReceivePresent(long userId, [FromBody] UserPresentRequest request)
    {
        var user = _users.GetUser(userId);
        var received = user.ReceivePresent(request.presentIds ?? []);

        return Ok(new UserPresentReceiveResponse
        {
            updatedResources = user.GetRefreshData(),
            receivedUserPresents = received
        });
    }
}
