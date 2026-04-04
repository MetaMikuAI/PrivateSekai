using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Config;
using PrivateSekai.Crypto;

namespace PrivateSekai.Controllers;

[ApiController]
public class GameVersionController : PrskController
{
    [HttpGet("/{gameVersion}/{appHash}")]
    public IActionResult GetGameVersion(string gameVersion, string appHash)
    {
        var response = new
        {
            profile = "production",
            assetbundleHostHash = "cf2d2388",
            domain = ServerConfig.GameVersionDomain,
        };

        return PrskResponse(response);
    }
}
