using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class CustomProfileController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<CustomProfileController> _logger;

    public CustomProfileController(UserManager users, ILogger<CustomProfileController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// PUT /api/user/{userId}/custom-profile/{customProfileId}
    /// </summary>
    [HttpPut("api/user/{userId}/custom-profile/{customProfileId}")]
    public async Task<IActionResult> HandleSaveCustomProfile(long userId, int customProfileId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserSaveCustomProfileRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.SaveCustomProfile(customProfileId, requestData.name, requestData.customProfileCardOrders);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// POST /api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card/{customProfileCardId}
    /// </summary>
    [HttpPost("api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card/{customProfileCardId}")]
    public async Task<IActionResult> HandleCreateCustomProfileCard(
        long userId,
        int customProfileId,
        int customProfileCardId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserSaveCustomProfileCardRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.SaveCustomProfileCard(customProfileId, customProfileCardId, requestData);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// PUT /api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card/{customProfileCardId}
    /// </summary>
    [HttpPut("api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card/{customProfileCardId}")]
    public async Task<IActionResult> HandleUpdateCustomProfileCard(
        long userId,
        int customProfileId,
        int customProfileCardId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserSaveCustomProfileCardRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.SaveCustomProfileCard(customProfileId, customProfileCardId, requestData);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// DELETE /api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card
    /// </summary>
    [HttpDelete("api/user/{userId}/custom-profile/{customProfileId}/custom-profile-card")]
    public IActionResult HandleDeleteCustomProfileCard(
        long userId,
        int customProfileId,
        [FromQuery] int[] customProfileCardId)
    {
        if (customProfileCardId.Length == 0)
            return BadRequest("Missing customProfileCardId");

        var user = _users.GetUser(userId);
        user.DeleteCustomProfileCards(customProfileId, customProfileCardId);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }

    /// <summary>
    /// GET /image/custom-profile-card/thumbnail/{hash}/{thumbnailId}
    /// </summary>
    [HttpGet("image/custom-profile-card/thumbnail/{hash}/{thumbnailId}")]
    public IActionResult HandleCustomProfileThumbnail(string hash, string thumbnailId)
    {
        if (!CustomProfileThumbnailStore.TryGetThumbnail(hash, thumbnailId, out var bytes, out var contentType))
            return NotFound("Thumbnail not found");

        return File(bytes, contentType);
    }

    /// <summary>
    /// POST /api/user/{userId}/report/{reportedUserId}/custom-profile/{customProfileId}
    /// </summary>
    [HttpPost("api/user/{userId}/report/{reportedUserId}/custom-profile/{customProfileId}")]
    public async Task<IActionResult> HandleCustomProfileReport(
        long userId,
        long reportedUserId,
        int customProfileId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<PostCustomProfileCommunityReportRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var reason = requestData.userReportReason;
        _logger.LogInformation(
            "Custom profile report: reporter={ReporterUserId}, reported={ReportedUserId}, customProfileId={CustomProfileId}, reasonTypes={ReasonTypes}, location={Location}",
            userId,
            reportedUserId,
            customProfileId,
            reason?.userReportReasonTypes == null ? "" : string.Join(",", reason.userReportReasonTypes),
            reason?.userReportLocation ?? "");

        return PrskResponse(new EmptyResponse());
    }
}
