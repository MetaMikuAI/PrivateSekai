using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class LiveController : PrskController
{
    private readonly UserManager _users;

    public LiveController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// POST /api/user/{userId}/live
    /// </summary>
    [HttpPost("api/user/{userId}/live")]
    public async Task<IActionResult> HandleUserLiveStart(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserLiveRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        return PrskResponse(user.StartUserLive(requestData));
    }

    /// <summary>
    /// PUT /api/user/{userId}/live/{userLiveId}
    /// </summary>
    [HttpPut("api/user/{userId}/live/{userLiveId}")]
    public async Task<IActionResult> HandleUserLiveClear(long userId, string userLiveId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserLiveClearRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        return PrskResponse(user.ClearUserLive(userLiveId, requestData));
    }

    /// <summary>
    /// POST /api/user/{userId}/live-character-archive-voice/live-result
    /// </summary>
    [HttpPost("api/user/{userId}/live-character-archive-voice/live-result")]
    public async Task<IActionResult> HandleUserLiveCharacterArchiveVoiceLiveResult(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserLiveCharacterArchiveVoiceLiveResultRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.ReceiveLiveCharacterArchiveVoiceResult(requestData.liveResultCharacterArchiveVoiceGroupId);

        return PrskResponse(new UserLiveCharacterArchiveVoiceLiveResultResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
