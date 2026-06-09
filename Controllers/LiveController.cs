using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

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
    public IActionResult HandleUserLiveStart(long userId, [FromBody] UserLiveRequest request)
    {
        var user = _users.GetUser(userId);
        return Ok(user.StartUserLive(request));
    }

    /// <summary>
    /// PUT /api/user/{userId}/live/{userLiveId}
    /// </summary>
    [HttpPut("api/user/{userId}/live/{userLiveId}")]
    public IActionResult HandleUserLiveClear(long userId, string userLiveId, [FromBody] UserLiveClearRequest request)
    {
        var user = _users.GetUser(userId);
        return Ok(user.ClearUserLive(userLiveId, request));
    }

    /// <summary>
    /// POST /api/user/{userId}/live-character-archive-voice/live-result
    /// </summary>
    [HttpPost("api/user/{userId}/live-character-archive-voice/live-result")]
    public IActionResult HandleUserLiveCharacterArchiveVoiceLiveResult(
        long userId,
        [FromBody] UserLiveCharacterArchiveVoiceLiveResultRequest request)
    {
        var user = _users.GetUser(userId);
        user.ReceiveLiveCharacterArchiveVoiceResult(request.liveResultCharacterArchiveVoiceGroupId);

        return Ok(new UserLiveCharacterArchiveVoiceLiveResultResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
