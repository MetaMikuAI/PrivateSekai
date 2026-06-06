using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class ShopController : PrskController
{
    private readonly UserManager _users;

    public ShopController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// POST /api/user/{userId}/shop/{shopId}/item/{shopItemId}
    /// </summary>
    [HttpPost("api/user/{userId}/shop/{shopId}/item/{shopItemId}")]
    public IActionResult HandleShopItemPurchase(long userId, int shopId, int shopItemId)
    {
        var user = _users.GetUser(userId);
        user.PurchaseShopItem(shopId, shopItemId);

        return PrskResponse(new SuiteUserCommonResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
