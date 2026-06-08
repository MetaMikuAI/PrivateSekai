using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class GachaController : PrskController
{
    private readonly UserManager _users;

    public GachaController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// GET /api/module-maintenance/{kind}
    /// </summary>
    [HttpGet("api/module-maintenance/{kind}")]
    public IActionResult HandleModuleMaintenance(string kind)
    {
        return PrskResponse(new ModuleMaintenanceResponse
        {
            moduleMaintenanceType = kind.ToLowerInvariant(),
            isOngoing = false
        });
    }

    /// <summary>
    /// PUT /api/user/{userId}/gacha/{gachaId}/gachaBehaviorId/{gachaBehaviorId}
    /// </summary>
    [HttpPut("api/user/{userId:long}/gacha/{gachaId:int}/gachaBehaviorId/{gachaBehaviorId:int}")]
    public IActionResult HandleUserGacha(
        long userId,
        int gachaId,
        int gachaBehaviorId,
        [FromQuery] bool isPriorityUsePaidJewel = false)
    {
        var user = _users.GetUser(userId);
        var responseData = user.ExecuteGacha(gachaId, gachaBehaviorId, isPriorityUsePaidJewel);
        return PrskResponse(responseData);
    }

    /// <summary>
    /// PUT /api/user/{userId}/exchange/gacha-ceil-item
    /// </summary>
    [HttpPut("api/user/{userId:long}/exchange/gacha-ceil-item")]
    public async Task<IActionResult> HandleGachaCeilItemExchange(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserGachaCeilExchangeRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        return PrskResponse(user.ExchangeGachaCeilItem(requestData));
    }

    /// <summary>
    /// PUT /api/user/{userId}/rate-choice-gacha-wish
    /// </summary>
    [HttpPut("api/user/{userId:long}/rate-choice-gacha-wish")]
    public async Task<IActionResult> HandleRateChoiceGachaWish(long userId)
    {
        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserRateChoiceGachaWishRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.SaveRateChoiceGachaWish(requestData);

        return PrskResponse(new UserRateChoiceGachaWishResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
