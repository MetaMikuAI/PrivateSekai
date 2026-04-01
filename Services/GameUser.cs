using System.Reflection;
using System.Text.Json.Nodes;
using MessagePack;
using PrivateSekai.Config;
using PrivateSekai.Crypto;
using PrivateSekai.Models;

namespace PrivateSekai.Services;

/// <summary>
/// 对应 Python game/user.py 的 User(Box) + 所有 Mixin
/// 内部数据使用强类型 SuiteUser
/// </summary>
public class GameUser
{
    /// <summary>主数据（对应 SuiteUser 结构）</summary>
    public SuiteUser Data { get; private set; }

    /// <summary>私有数据，不随 GetSuiteUserData 导出</summary>
    public NotSuiteData NotSuite { get; private set; }

    /// <summary>反射缓存：MessagePack Key → SuiteUser FieldInfo</summary>
    private static readonly Dictionary<string, FieldInfo> SuiteUserFields =
        typeof(SuiteUser).GetFields()
            .Where(f => f.GetCustomAttribute<KeyAttribute>() != null)
            .ToDictionary(
                f => f.GetCustomAttribute<KeyAttribute>()!.StringKey!,
                f => f
            );

    public GameUser(SuiteUser data)
    {
        Data = data;
        NotSuite = new NotSuiteData();
    }

    public long GetUserId() =>
        Data.userRegistration?.userId ?? 0;

    // ===================== init 方法 =====================

    public void InitAllUserId(long newUserId)
    {
        if (Data.userRegistration != null)
        {
            Data.userRegistration.userId = newUserId;
            Data.userRegistration.signature = JwtSignature.GenUserSignature(newUserId);
        }
        if (Data.userGamedata != null) Data.userGamedata.userId = newUserId;
        if (Data.userProfile != null) Data.userProfile.userId = newUserId;

        if (Data.userCards != null)
            foreach (var c in Data.userCards) c.userId = newUserId;
        if (Data.userDecks != null)
            foreach (var d in Data.userDecks) d.userId = newUserId;
        if (Data.userUnits != null)
            foreach (var u in Data.userUnits) u.userId = newUserId;
        if (Data.unreadUserTopics != null)
            foreach (var t in Data.unreadUserTopics) t.userId = newUserId;
        if (Data.userMaterialExchanges != null)
            foreach (var m in Data.userMaterialExchanges) m.userId = newUserId;
        if (Data.userGachaCeilExchanges != null)
            foreach (var g in Data.userGachaCeilExchanges) g.userId = newUserId;
        if (Data.userCharacterMissionV2Statuses != null)
            foreach (var s in Data.userCharacterMissionV2Statuses) s.userId = newUserId;
    }

    public void InitAllUserTime(long currentTime)
    {
        Data.now = currentTime;
        if (Data.userRegistration != null) Data.userRegistration.registeredAt = (ulong)currentTime;
        if (Data.userBoost != null) Data.userBoost.recoveryAt = (ulong)currentTime;

        if (Data.userCards != null)
            foreach (var card in Data.userCards) card.createdAt = currentTime;

        if (Data.userCostume3dStatuses != null)
            foreach (var status in Data.userCostume3dStatuses) status.obtainedAt = currentTime;

        if (Data.userReleaseConditions != null)
            foreach (var cond in Data.userReleaseConditions) cond.createdAt = currentTime;

        if (ServerConfig.SkipTutorial)
        {
            Data.userTutorial = new UserTutorial
            {
                tutorialStatus = "end",
                tutorialEndAt = currentTime
            };
        }
    }

    public void InitNotSuite()
    {
        NotSuite = new NotSuiteData();
    }

    // ===================== 数据导出 =====================

    public SuiteUser GetSuiteUserData()
    {
        Data.now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        // MessagePack 序列化往返实现深拷贝
        var bytes = MessagePackSerializer.Serialize(Data);
        return MessagePackSerializer.Deserialize<SuiteUser>(bytes);
    }

    public SuiteUser GetRefreshData(HashSet<string>? deleteRtypes = null)
    {
        var baseRtypes = new HashSet<string>
        {
            "now", "refreshableTypes", "userPresents", "unreadUserTopics",
            "userHomeBanners", "userMaterialExchanges", "userGachaCeilExchanges",
            "userRankMatchResult", "userViewableAppeal",
            "userBillingRefunds", "userUnprocessedOrders", "userInformations"
        };

        if (Data.refreshableTypes != null)
        {
            foreach (var r in Data.refreshableTypes)
                baseRtypes.Add(r);
        }

        if (deleteRtypes != null)
            baseRtypes.ExceptWith(deleteRtypes);

        // 清空 refreshableTypes
        Data.refreshableTypes = [];

        // 通过反射选择性拷贝字段
        var result = new SuiteUser();
        foreach (var rtype in baseRtypes)
        {
            if (SuiteUserFields.TryGetValue(rtype, out var field))
            {
                var value = field.GetValue(Data);
                if (value != null)
                    field.SetValue(result, value);
            }
        }
        result.now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

        return result;
    }
    
    public void UpdateUserName(string newName)
    {
        if (Data.userGamedata != null)
            Data.userGamedata.name = newName;
    }

    public void UpdateRefreshableTypes(string rtype)
    {
        Data.refreshableTypes ??= [];
        if (!Data.refreshableTypes.Contains(rtype))
            Data.refreshableTypes.Add(rtype);
    }

    private static readonly Dictionary<string, int[]> TutorialCardsByUnit = new()
    {
        ["light_sound_opening"]     = [1, 5, 9, 13, 81, 82, 89, 93, 97, 98, 101, 105],
        ["idol_opening"]            = [17, 21, 25, 29, 81, 83, 89, 90, 93, 97, 101, 105],
        ["street_opening"]          = [33, 37, 41, 45, 81, 84, 89, 93, 94, 97, 102, 105],
        ["theme_park_opening"]      = [49, 53, 57, 61, 81, 85, 89, 93, 97, 101, 105, 106],
        ["school_refusal_opening"]  = [65, 69, 73, 77, 81, 86, 89, 93, 97, 101, 105]
    };

    public void UpdateTutorialProgress(string newStatus)
    {
        if (Data.userTutorial == null) return;

        var oldStatus = Data.userTutorial.tutorialStatus;
        Data.userTutorial.tutorialStatus = newStatus;

        if (oldStatus != null && TutorialCardsByUnit.TryGetValue(oldStatus, out var cardIds))
        {
            UpdateRefreshableTypes("userCards");
            UpdateRefreshableTypes("userDecks");
            UpdateRefreshableTypes("userUnitEpisodeStatuses");

            foreach (var cardId in cardIds)
                AddCard(cardId);

            UpdateRefreshableTypes("userCharacterMissionV2s");
            UpdateRefreshableTypes("userCharacterMissionV2Statuses");
            UpdateRefreshableTypes("userBeginnerMissionV2s");
            UpdateRefreshableTypes("userMissionStatuses");
            UpdateRefreshableTypes("userHonorMissions");
        }

        if (newStatus == "end")
        {
            Data.userTutorial.tutorialEndAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        }

        UpdateRefreshableTypes("userTutorial");
    }

    /// <summary>cardEpisodes.json 的缓存</summary>
    private static JsonArray? _cardEpisodesCache;

    private static JsonArray LoadCardEpisodes()
    {
        if (_cardEpisodesCache != null) return _cardEpisodesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "cardEpisodes.json");
        var json = File.ReadAllText(path);
        _cardEpisodesCache = JsonNode.Parse(json)!.AsArray();
        return _cardEpisodesCache;
    }

    private static List<int> GetCardEpisodeIds(int cardId)
    {
        var episodes = LoadCardEpisodes();
        var ids = new List<int>();
        foreach (var ep in episodes)
        {
            if (ep is JsonObject obj && obj["cardId"]?.GetValue<int>() == cardId)
                ids.Add(obj["id"]!.GetValue<int>());
        }
        while (ids.Count < 2) ids.Add(0);
        return ids;
    }

    public UserCard AddCard(int cardId)
    {
        var currentTime = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var episodeIds = GetCardEpisodeIds(cardId);
        long userId = Data.userGamedata?.userId ?? 0;

        var newCard = new UserCard
        {
            userId = userId,
            cardId = cardId,
            level = 1,
            exp = 0,
            totalExp = 0,
            skillLevel = 1,
            skillExp = 0,
            totalSkillExp = 0,
            masterRank = 0,
            specialTrainingStatus = "not_doing",
            defaultImage = "original",
            duplicateCount = 0,
            createdAt = currentTime,
            episodes =
            [
                new UserCardEpisode
                {
                    cardEpisodeId = episodeIds[0],
                    scenarioStatus = "unread_before_scenario",
                    scenarioStatusReasons = [],
                    isNotSkipped = false
                },
                new UserCardEpisode
                {
                    cardEpisodeId = episodeIds[1],
                    scenarioStatus = "can_not_read",
                    scenarioStatusReasons = ["unread_before_scenario", "not_enough_release_condition"],
                    isNotSkipped = false
                }
            ]
        };

        Data.userCards ??= [];
        if (!Data.userCards.Any(c => c.cardId == cardId))
            Data.userCards.Add(newCard);

        UpdateRefreshableTypes("userCards");
        return newCard;
    }

    // ===================== Inherit Mixin =====================

    public string SetUserInherit(string password)
    {
        var inheritId = GenerateRandomString(16);

        NotSuite.InheritId = inheritId;
        NotSuite.InheritPassword = password;

        Data.userInherit = new UserInherit { inheritId = inheritId };
        UpdateRefreshableTypes("userInherit");
        return inheritId;
    }

    public UserGamedata GetAfterUserGamedata()
    {
        var gd = Data.userGamedata!;
        return new UserGamedata
        {
            userId = gd.userId,
            name = gd.name,
            deck = gd.deck,
            rank = gd.rank
        };
    }

    public bool VerifyInherit(string inheritId, string password)
    {
        return NotSuite.InheritId == inheritId
            && NotSuite.InheritPassword == password;
    }

    // ===================== Topic Mixin =====================

    public void RemoveTopic(int topicId)
    {
        if (Data.unreadUserTopics == null) return;
        Data.unreadUserTopics = Data.unreadUserTopics
            .Where(t => t.topicId != topicId).ToArray();
    }

    // ===================== Special Story Mixin =====================

    public void ReadEpisode(int specialEpisodeId)
    {
        if (Data.userSpecialEpisodeStatuses == null) return;

        foreach (var status in Data.userSpecialEpisodeStatuses)
        {
            if (status.episodeId == specialEpisodeId)
            {
                status.status = "already_read";
                UpdateRefreshableTypes("userSpecialEpisodeStatuses");
                return;
            }
        }
    }

    // ===================== Present Mixin =====================

    public List<UserPresentData> ReceivePresent(string[] presentIds)
    {
        var received = new List<UserPresentData>();
        foreach (var pid in presentIds)
        {
            var result = ReceiveOnePresent(pid);
            if (result != null)
                received.Add(result);
        }
        return received;
    }

    private UserPresentData? ReceiveOnePresent(string presentId)
    {
        if (Data.userPresents == null) return null;

        var idx = Data.userPresents.FindIndex(p => p.presentId == presentId);
        if (idx < 0) return null;

        var present = Data.userPresents[idx];
        Data.userPresents.RemoveAt(idx);

        NotSuite.PresentHistories.Add(new UserPresentHistoryData
        {
            presentId = present.presentId,
            seq = present.seq,
            resourceType = present.resourceType,
            resourceId = present.resourceId,
            resourceLevel = present.resourceLevel,
            resourceQuantity = present.resourceQuantity,
            receivedAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            reason = present.reason
        });

        return present;
    }

    public List<UserPresentHistoryData> GetPresentHistory()
    {
        return NotSuite.PresentHistories;
    }

    // ===================== Profile Mixin =====================

    public void UpdateProfile(UserProfile newProfile)
    {
        if (Data.userProfile == null) return;
        // 保留原 userId
        newProfile.userId = Data.userProfile.userId;
        Data.userProfile = newProfile;
        UpdateRefreshableTypes("userProfile");
    }

    public void UpdateUserGamedata(UserGamedata newGamedata)
    {
        Data.userGamedata = newGamedata;
    }

    // ===================== 工具方法 =====================

    private static readonly Random Rng = new();

    private static string GenerateRandomString(int length)
    {
        const string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        var result = new char[length];
        for (int i = 0; i < length; i++)
            result[i] = chars[Rng.Next(chars.Length)];
        return new string(result);
    }

    /// <summary>深拷贝当前用户（MessagePack 序列化往返）</summary>
    public GameUser DeepClone()
    {
        var bytes = MessagePackSerializer.Serialize(Data);
        var clonedData = MessagePackSerializer.Deserialize<SuiteUser>(bytes);
        var user = new GameUser(clonedData)
        {
            NotSuite = new NotSuiteData
            {
                InheritId = NotSuite.InheritId,
                InheritPassword = NotSuite.InheritPassword,
                PresentHistories = [.. NotSuite.PresentHistories]
            }
        };
        return user;
    }
}
