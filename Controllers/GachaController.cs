using Microsoft.AspNetCore.Mvc;
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
}
