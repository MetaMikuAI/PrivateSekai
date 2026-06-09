using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

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
        return Ok(new ModuleMaintenanceResponse
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
        return Ok(user.ExecuteGacha(gachaId, gachaBehaviorId, isPriorityUsePaidJewel));
    }

    /// <summary>
    /// PUT /api/user/{userId}/exchange/gacha-ceil-item
    /// </summary>
    [HttpPut("api/user/{userId:long}/exchange/gacha-ceil-item")]
    public IActionResult HandleGachaCeilItemExchange(long userId, [FromBody] UserGachaCeilExchangeRequest request)
    {
        var user = _users.GetUser(userId);
        return Ok(user.ExchangeGachaCeilItem(request));
    }

    /// <summary>
    /// PUT /api/user/{userId}/rate-choice-gacha-wish
    /// </summary>
    [HttpPut("api/user/{userId:long}/rate-choice-gacha-wish")]
    public IActionResult HandleRateChoiceGachaWish(long userId, [FromBody] UserRateChoiceGachaWishRequest request)
    {
        var user = _users.GetUser(userId);
        user.SaveRateChoiceGachaWish(request);

        return Ok(new UserRateChoiceGachaWishResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
