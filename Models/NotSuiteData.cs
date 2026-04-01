namespace PrivateSekai.Models;

/// <summary>
/// 私有数据，不随 SuiteUser 导出
/// 对应原 GameUser.NotSuite JsonObject
/// </summary>
public class NotSuiteData
{
    /// <summary>引继密码（不属于游戏协议，私服专用）</summary>
    public string InheritId { get; set; } = "";
    public string InheritPassword { get; set; } = "";

    /// <summary>礼物领取历史</summary>
    public List<UserPresentHistoryData> PresentHistories { get; set; } = [];
}
