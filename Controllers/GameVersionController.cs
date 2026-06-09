using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Config;

namespace PrivateSekai.Controllers;

public class GameVersionController : PrskController
{
    [HttpGet("/{gameVersion}/{appHash}")]
    public IActionResult GetGameVersion(string gameVersion, string appHash)
    {
        return Ok(new
        {
            profile = "production",
            assetbundleHostHash = "cf2d2388",
            domain = ServerConfig.GameVersionDomain,
        });
    }
}
