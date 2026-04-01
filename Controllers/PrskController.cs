using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;

namespace PrivateSekai.Controllers;

[ApiController]
public abstract class PrskController : ControllerBase
{
    protected FileContentResult PrskResponse<T>(T data) =>
        File(PrskCrypto.PrskEncSkipNull(data), "application/octet-stream");

    protected async Task<byte[]?> ReadBodyAsync()
    {
        using var ms = new MemoryStream();
        await Request.Body.CopyToAsync(ms);
        var data = ms.ToArray();
        return data.Length == 0 ? null : data;
    }
}
