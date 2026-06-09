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
    /// PUT /api/user/{userId}/card/?behavior=exchange
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
