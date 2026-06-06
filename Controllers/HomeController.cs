using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class HomeController : PrskController
{
    private readonly UserManager _users;
    private readonly ILogger<HomeController> _logger;

    public HomeController(UserManager users, ILogger<HomeController> logger)
    {
        _users = users;
        _logger = logger;
    }

    /// <summary>
    /// PUT /api/user/{userId}/home/refresh
    /// </summary>
    [HttpPut("api/user/{userId}/home/refresh")]
    public async Task<IActionResult> HandleUserHomeRefresh(long userId)
    {
        var user = _users.GetUser(userId);

        var body = await ReadBodyAsync();
        var requestData = TryDecodeHomeRefreshRequest(body);
        if (requestData?.refreshableTypes?.Contains("lottery_action_set") == true)
            user.RefreshAreaActionSets();

        user.UpdateRefreshableTypes("userFriends");

        var responseData = new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        };
        return PrskResponse(responseData);
    }

    private HomeRefreshRequest? TryDecodeHomeRefreshRequest(byte[]? body)
    {
        if (body == null)
            return null;

        try
        {
            return PrskCrypto.PrskDec<HomeRefreshRequest>(body);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to decode home refresh request; continuing with default refresh");
            return null;
        }
    }

    /// <summary>
    /// GET /api/information
    /// </summary>
    [HttpGet("api/information")]
    public IActionResult HandleInformation()
    {
        var user = _users.GetUser(0);
        var responseData = new InformationResponse
        {
            informations = user.Data.userInformations
        };
        return PrskResponse(responseData);
    }
}
