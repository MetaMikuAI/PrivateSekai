using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class ProfileController : PrskController
{
    private readonly UserManager _users;

    public ProfileController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// PUT /api/user/{userId}/profile — 更新个人资料
    /// </summary>
    [HttpPut("api/user/{userId}/profile")]
    public async Task<IActionResult> HandleUserProfile(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserProfileRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.UpdateProfile(new UserProfile
        {
            word = requestData.word,
            twitterId = requestData.twitterId,
            profileImageType = requestData.profileImageType,
            profileImageId = requestData.profileImageId ?? 0
        });

        var responseData = new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// PUT /api/user/{userId} — 更新用户游戏数据
    /// </summary>
    [HttpPut("api/user/{userId}")]
    public async Task<IActionResult> HandleUserUpdate(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserGamedataUpdateRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        if (requestData.userGamedata == null)
            return BadRequest("Missing userGamedata");

        var user = _users.GetUser(userId);
        user.MergeUserGamedata(requestData.userGamedata);

        var responseData = new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }
}
