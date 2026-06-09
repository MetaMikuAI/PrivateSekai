using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

public class ProfileController : PrskController
{
    private readonly UserManager _users;

    public ProfileController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// PUT /api/user/{userId}/profile
    /// </summary>
    [HttpPut("api/user/{userId}/profile")]
    public IActionResult HandleUserProfile(long userId, [FromBody] UserProfileRequest request)
    {
        var user = _users.GetUser(userId);
        user.UpdateProfile(new UserProfile
        {
            word = request.word,
            twitterId = request.twitterId,
            profileImageType = request.profileImageType,
            profileImageId = request.profileImageId ?? 0
        });

        return Ok(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// PUT /api/user/{userId}
    /// </summary>
    [HttpPut("api/user/{userId}")]
    public IActionResult HandleUserUpdate(long userId, [FromBody] UserGamedataUpdateRequest request)
    {
        if (request.userGamedata == null)
            return BadRequest("Missing userGamedata");

        var user = _users.GetUser(userId);
        user.MergeUserGamedata(request.userGamedata);

        return Ok(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
