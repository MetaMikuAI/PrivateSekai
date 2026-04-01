using System.Text.Json;
using PrivateSekai.Config;
using PrivateSekai.Models;

namespace PrivateSekai.Services;

/// <summary>
/// 对应 Python game/users.py 的 Users 类
/// 管理所有在线用户数据，DI 注册为 Singleton
/// </summary>
public class UserManager
{
    private static readonly JsonSerializerOptions JsonOpts = new() { IncludeFields = true };

    private readonly Dictionary<long, GameUser> _users = new();
    private readonly ILogger<UserManager> _logger;

    /// <summary>模板数据（对应 template/api_user_auth.json）</summary>
    public UserAuthResponse ApiUserAuth { get; private set; } = null!;

    /// <summary>模板数据（对应 template/api_system.json）</summary>
    public SystemResponse ApiSystem { get; private set; } = null!;

    /// <summary>用户自定义补丁回调</summary>
    public Action<GameUser>? UserCustomizePatch { get; set; }

    public UserManager(ILogger<UserManager> logger)
    {
        _logger = logger;
        LoadTemplates();
        CreateUser0();
    }

    private void LoadTemplates()
    {
        var basePath = ServerConfig.TemplatePath;

        var authPath = Path.Combine(basePath, "api_user_auth.json");
        ApiUserAuth = JsonSerializer.Deserialize<UserAuthResponse>(
            File.ReadAllText(authPath), JsonOpts)!;

        var sysPath = Path.Combine(basePath, "api_system.json");
        ApiSystem = JsonSerializer.Deserialize<SystemResponse>(
            File.ReadAllText(sysPath), JsonOpts)!;
    }

    private void CreateUser0()
    {
        var templatePath = Path.Combine(ServerConfig.TemplatePath, "user_0.json");
        var json = File.ReadAllText(templatePath);
        var data = JsonSerializer.Deserialize<SuiteUser>(json, JsonOpts)!;

        var user = new GameUser(data);

        // 对应 Python config.py 的 user_customize_patch
        UserCustomizePatch?.Invoke(user);
        // 默认补丁：设置 paid = 20070831
        if (user.Data.userChargedCurrency != null)
            user.Data.userChargedCurrency.paid = 20070831;

        _users[0] = user;
    }

    public GameUser GetUser(long userId)
    {
        if (!_users.ContainsKey(userId))
            _users[userId] = new GameUser(new SuiteUser());
        return _users[userId];
    }

    public bool UserExists(long userId) => _users.ContainsKey(userId);

    public long GetNewUserId() =>
        _users.Keys.DefaultIfEmpty(-1).Max() + 1;

    public long ForkNewUser(long? userId = null)
    {
        var newUserId = userId ?? GetNewUserId();
        var fromUser = GetUser(0);
        var newUser = fromUser.DeepClone();

        newUser.InitAllUserId(newUserId);
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        newUser.InitAllUserTime(now);
        newUser.InitNotSuite();

        _users[newUserId] = newUser;
        _logger.LogInformation("New user forked: ID={UserId}", newUserId);
        return newUserId;
    }

    public string GetUserListJson()
    {
        var list = _users.Keys.Select(id => new { userId = id });
        return JsonSerializer.Serialize(list);
    }

    public IEnumerable<(long UserId, GameUser User)> GetAllUsers()
    {
        foreach (var kv in _users)
            yield return (kv.Key, kv.Value);
    }
}
