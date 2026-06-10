using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

public class CardController : PrskController
{
    private readonly UserManager _users;

    public CardController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// 执行等待室卡牌转换。客户端把确认转换的卡牌汇总成 `userCards` 发给服务端，请求成功后合并返回的用户资源差异，并刷新等待室显示。
    /// </summary>
    [HttpPut("api/user/{userId}/card")]
    [HttpPut("api/user/{userId}/card/")]
    public IActionResult HandleCard(long userId, [FromQuery] string? behavior, [FromBody] UserCardExchangeRequest request)
    {
        if (!string.Equals(behavior, "exchange", StringComparison.Ordinal))
            return NotFound();

        var user = _users.GetUser(userId);
        user.ExchangeCards(request.userCards);

        return Ok(new UserCardExchangeResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
