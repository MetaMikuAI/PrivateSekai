using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
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
        var responseData = new UserPresentHistoriesResponse
        {
            userPresentHistories = user.GetPresentHistory()
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// POST /api/user/{userId}/present — 领取礼物
    /// </summary>
    [HttpPost("api/user/{userId}/present")]
    public async Task<IActionResult> HandleReceivePresent(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserPresentRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        var received = user.ReceivePresent(requestData.presentIds ?? []);

        var responseData = new UserPresentReceiveResponse
        {
            updatedResources = user.GetRefreshData(),
            receivedUserPresents = received
        };
        return PrskResponse(responseData);
    }
}
