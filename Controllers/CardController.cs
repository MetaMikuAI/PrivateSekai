using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
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
    public async Task<IActionResult> HandleCard(long userId, [FromQuery] string? behavior)
    {
        if (!string.Equals(behavior, "exchange", StringComparison.Ordinal))
            return NotFound();

        var body = await ReadBodyAsync();
        if (body == null) return BadRequest("Empty body");

        var requestData = PrskCrypto.PrskDec<UserCardExchangeRequest>(body);
        if (requestData == null) return BadRequest("Failed to decrypt");

        var user = _users.GetUser(userId);
        user.ExchangeCards(requestData.userCards);

        return PrskResponse(new UserCardExchangeResponse
        {
            updatedResources = user.GetRefreshData()
        });
    }
}
