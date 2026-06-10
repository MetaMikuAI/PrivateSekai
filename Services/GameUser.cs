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
    /// <summary>
    /// 广为人知的 Suite 数据
    /// </summary>
    public SuiteUser Data { get; private set; }

    /// <summary>
    /// 不随 GetSuiteUserData 导出的私有数据
    /// </summary>
    public NotSuiteData NotSuite { get; private set; }

    /// <summary>反射缓存：MessagePack Key → SuiteUser FieldInfo</summary>
    private static readonly Dictionary<string, FieldInfo> SuiteUserFields =
        typeof(SuiteUser).GetFields()
            .Where(f => f.GetCustomAttribute<KeyAttribute>() != null)
            .ToDictionary(
                f => f.GetCustomAttribute<KeyAttribute>()!.StringKey!,
                f => f
            );

    private static readonly Dictionary<string, string> SuiteUserFieldKeys =
        typeof(SuiteUser).GetFields()
            .Where(f => f.GetCustomAttribute<KeyAttribute>()?.StringKey != null)
            .ToDictionary(
                f => f.Name,
                f => f.GetCustomAttribute<KeyAttribute>()!.StringKey!
            );

    /// <summary>
    /// 无实义
    /// </summary>
    private const long TemplatePlaceholderTimestamp = 1188486000000L; // 2007-08-30T15:00:00Z
    
    /// <summary>
    /// TODO: 移动到新手教程结束(或其他某个正确的位置)后直接解锁，而非每次刷新
    /// </summary>
    private static readonly Dictionary<int, int[]> FixedShopActionSetsByArea = new()
    {
        [3] = [4, 384, 2002, 2005],
        [4] = [3, 838, 2001, 2006]
    };
    
    public GameUser(SuiteUser? data = null)
    {
        Data = data ?? new SuiteUser();
        NotSuite = new NotSuiteData();
    }

    public long GetUserId() =>
        Data.userRegistration?.userId ?? 0;
    
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
        Data.userRegistration?.registeredAt = (ulong)currentTime;
        Data.userBoost?.recoveryAt = (ulong)currentTime;

        if (Data.userCards != null)
            foreach (var card in Data.userCards) card.createdAt = currentTime;

        if (Data.userCostume3dStatuses != null)
            foreach (var status in Data.userCostume3dStatuses) status.obtainedAt = currentTime;

        if (Data.userReleaseConditions != null)
            foreach (var cond in Data.userReleaseConditions) cond.createdAt = currentTime;
    }
    
    public SuiteUser GetSuiteUserData()
    {
        var now = UserManager.Now;
        Data.now = now;
        NormalizeUserEventBreakTime(now);
        EnsureShopAreaActionSets();

        return Data;
    }
    
    public SuiteUser GetRefreshData(HashSet<string>? deleteRtypes = null)
    {
        var now = UserManager.Now;
        NormalizeUserEventBreakTime(now);

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
        result.now = now;

        return result;
    }

    public SuiteUser GetSuiteUserParts(IEnumerable<string>? partNames)
    {
        var now = UserManager.Now;
        NormalizeUserEventBreakTime(now);

        var result = new SuiteUser
        {
            now = now,
            refreshableTypes = []
        };

        if (partNames == null)
        {
            return GetRefreshData();
        }

        foreach (var partName in partNames)
        {
            switch (partName)
            {
                case "user_event_break_time":
                    result.userEventBreakTime = Data.userEventBreakTime;
                    break;
                case "user_friend":
                    result.userFriends = Data.userFriends;
                    break;
                default:
                    return GetRefreshData();
            }
        }
        
        return result;
    }

    private void NormalizeUserEventBreakTime(long now)
    {
        var userEventBreakTime = Data.userEventBreakTime;
        if (userEventBreakTime == null)
            return;

        if (userEventBreakTime.lastDecreaseAt > 0 &&
            userEventBreakTime.lastDecreaseAt != TemplatePlaceholderTimestamp)
        {
            return;
        }

        userEventBreakTime.lastDecreaseAt = now;
        userEventBreakTime.playTimeUsedMillis = 0;
    }
    
    public void UpdateUserName(string newName)
    {
        Data.userGamedata?.name = newName;
    }

    /// <summary>
    /// 标记需更新字段，将在获取 UpdateResource 时将对应数据段返回给客户端，TODO: 考虑使用标记位而非字段表
    /// </summary>
    /// <param name="suiteUserFieldName"></param>
    /// <exception cref="ArgumentException"></exception>
    public void UpdateRefreshableType(string suiteUserFieldName)
    {
        if (!SuiteUserFieldKeys.TryGetValue(suiteUserFieldName, out var rtype))
            throw new ArgumentException($"Unknown SuiteUser field: {suiteUserFieldName}", nameof(suiteUserFieldName));

        AddRefreshableType(rtype);
    }

    public void UpdateRefreshableTypes(IEnumerable<string> suiteUserFieldNames)
    {
        foreach (var suiteUserFieldName in suiteUserFieldNames)
        {
            UpdateRefreshableType(suiteUserFieldName);
        }
    }
    

    private void AddRefreshableType(string rtype)
    {
        Data.refreshableTypes ??= [];
        if (!Data.refreshableTypes.Contains(rtype))
            Data.refreshableTypes.Add(rtype);
    }

    public void MarkAppealsViewed(int[]? appealIds)
    {
        if (appealIds == null || appealIds.Length == 0)
            return;

        var mergedIds = (Data.userViewableAppeal?.appealIds ?? [])
            .Concat(appealIds.Where(id => id > 0))
            .Distinct()
            .OrderBy(id => id)
            .ToArray();

        Data.userViewableAppeal = new ViewableAppeal
        {
            appealIds = mergedIds
        };
        UpdateRefreshableType(nameof(SuiteUser.userViewableAppeal));
    }

    public void RefreshAreaActionSets()
    {
        EnsureShopAreaActionSets();
        UpdateRefreshableType(nameof(SuiteUser.userAreas));
    }

    public void EnsureShopAreaActionSets()
    {
        if (Data.userAreas == null)
            return;

        foreach (var (areaId, actionSetIds) in FixedShopActionSetsByArea)
        {
            var area = Data.userAreas.FirstOrDefault(a => a.areaId == areaId);
            if (area == null)
                continue;

            area.userAreaStatus ??= new UserAreaStatus
            {
                areaId = areaId
            };
            area.userAreaStatus.status = UserAreaStatus.AREA_STATUS_RELEASED;

            var actionSets = (area.actionSets ?? []).ToList();
            foreach (var actionSetId in actionSetIds)
            {
                if (actionSets.Any(a => a.id == actionSetId))
                    continue;

                actionSets.Add(new UserActionSet
                {
                    id = actionSetId,
                    status = UserActionSet.ACTION_SET_STATUS_UNREAD
                });
            }

            area.actionSets = actionSets.ToArray();
        }
    }

    /// <summary>
    /// 阅读不同团体的初始剧情后，会解锁对应的角色卡牌，现仅只实现新手教程部分，未实现阅读其他初始剧情补发卡牌的功能 (TODO)
    /// </summary>
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
            foreach (var cardId in cardIds)
                AddCard(cardId);

            UpdateRefreshableTypes(new[]
            {
                nameof(SuiteUser.userCards),
                nameof(SuiteUser.userDecks),
                nameof(SuiteUser.userUnitEpisodeStatuses),
                nameof(SuiteUser.userCharacterMissionV2s),
                nameof(SuiteUser.userCharacterMissionV2Statuses),
                nameof(SuiteUser.userBeginnerMissionV2s),
                nameof(SuiteUser.userMissionStatuses),
                nameof(SuiteUser.userHonorMissions)
            });

        }

        if (newStatus == "end")
        {
            Data.userTutorial.tutorialEndAt = UserManager.Now;
        }

        UpdateRefreshableType(nameof(SuiteUser.userTutorial));
    }

    /// <summary>
    /// cardEpisodes.json 的缓存, TODO: 使用 sqlite
    /// </summary>
    private static JsonArray? _cardEpisodesCache;
    private static JsonArray? _musicDifficultiesCache;
    private static JsonArray? _boostsCache;
    private static JsonArray? _musicAchievementsCache;
    private static JsonArray? _resourceBoxesCache;
    private static JsonArray? _shopItemsCache;
    private static JsonArray? _musicVocalsCache;
    private static JsonArray? _liveMissionPassesCache;
    private static JsonArray? _playLevelScoresCache;
    private static JsonArray? _gachasCache;
    private static JsonArray? _cardsCache;
    private static JsonArray? _cardCostume3dsCache;
    private static JsonArray? _gachaCeilItemsCache;
    private static JsonArray? _gachaCeilExchangeSummariesCache;

    private static JsonArray LoadCardEpisodes()
    {
        if (_cardEpisodesCache != null) return _cardEpisodesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "cardEpisodes.json");
        var json = File.ReadAllText(path);
        _cardEpisodesCache = JsonNode.Parse(json)!.AsArray();
        return _cardEpisodesCache;
    }

    private static JsonArray LoadMusicDifficulties()
    {
        if (_musicDifficultiesCache != null) return _musicDifficultiesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "musicDifficulties.json");
        var json = File.ReadAllText(path);
        _musicDifficultiesCache = JsonNode.Parse(json)!.AsArray();
        return _musicDifficultiesCache;
    }

    private static JsonArray LoadBoosts()
    {
        if (_boostsCache != null) return _boostsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "boosts.json");
        var json = File.ReadAllText(path);
        _boostsCache = JsonNode.Parse(json)!.AsArray();
        return _boostsCache;
    }

    private static JsonArray LoadMusicAchievements()
    {
        if (_musicAchievementsCache != null) return _musicAchievementsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "musicAchievements.json");
        var json = File.ReadAllText(path);
        _musicAchievementsCache = JsonNode.Parse(json)!.AsArray();
        return _musicAchievementsCache;
    }

    private static JsonArray LoadResourceBoxes()
    {
        if (_resourceBoxesCache != null) return _resourceBoxesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "resourceBoxes.json");
        var json = File.ReadAllText(path);
        _resourceBoxesCache = JsonNode.Parse(json)!.AsArray();
        return _resourceBoxesCache;
    }

    private static JsonArray LoadShopItems()
    {
        if (_shopItemsCache != null) return _shopItemsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "shopItems.json");
        var json = File.ReadAllText(path);
        _shopItemsCache = JsonNode.Parse(json)!.AsArray();
        return _shopItemsCache;
    }

    private static JsonArray LoadMusicVocals()
    {
        if (_musicVocalsCache != null) return _musicVocalsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "musicVocals.json");
        var json = File.ReadAllText(path);
        _musicVocalsCache = JsonNode.Parse(json)!.AsArray();
        return _musicVocalsCache;
    }

    private static JsonArray LoadLiveMissionPasses()
    {
        if (_liveMissionPassesCache != null) return _liveMissionPassesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "liveMissionPasses.json");
        var json = File.ReadAllText(path);
        _liveMissionPassesCache = JsonNode.Parse(json)!.AsArray();
        return _liveMissionPassesCache;
    }

    private static JsonArray LoadPlayLevelScores()
    {
        if (_playLevelScoresCache != null) return _playLevelScoresCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "playLevelScores.json");
        var json = File.ReadAllText(path);
        _playLevelScoresCache = JsonNode.Parse(json)!.AsArray();
        return _playLevelScoresCache;
    }

    private static JsonArray LoadGachas()
    {
        if (_gachasCache != null) return _gachasCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "gachas.json");
        var json = File.ReadAllText(path);
        _gachasCache = JsonNode.Parse(json)!.AsArray();
        return _gachasCache;
    }

    private static JsonArray LoadCards()
    {
        if (_cardsCache != null) return _cardsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "cards.json");
        var json = File.ReadAllText(path);
        _cardsCache = JsonNode.Parse(json)!.AsArray();
        return _cardsCache;
    }

    private static JsonArray LoadCardCostume3ds()
    {
        if (_cardCostume3dsCache != null) return _cardCostume3dsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "cardCostume3ds.json");
        var json = File.ReadAllText(path);
        _cardCostume3dsCache = JsonNode.Parse(json)!.AsArray();
        return _cardCostume3dsCache;
    }

    private static JsonArray LoadGachaCeilItems()
    {
        if (_gachaCeilItemsCache != null) return _gachaCeilItemsCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "gachaCeilItems.json");
        var json = File.ReadAllText(path);
        _gachaCeilItemsCache = JsonNode.Parse(json)!.AsArray();
        return _gachaCeilItemsCache;
    }

    private static JsonArray LoadGachaCeilExchangeSummaries()
    {
        if (_gachaCeilExchangeSummariesCache != null) return _gachaCeilExchangeSummariesCache;

        var path = Path.Combine(ServerConfig.SekaiMasterDbDiffPath, "gachaCeilExchangeSummaries.json");
        var json = File.ReadAllText(path);
        _gachaCeilExchangeSummariesCache = JsonNode.Parse(json)!.AsArray();
        return _gachaCeilExchangeSummariesCache;
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
        var currentTime = UserManager.Now;
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
        if (Data.userCards.All(c => c.cardId != cardId))
            Data.userCards.Add(newCard);

        UpdateRefreshableType(nameof(SuiteUser.userCards));
        return newCard;
    }

    public UserGachaResponse ExecuteGacha(int gachaId, int gachaBehaviorId, bool isPriorityUsePaidJewel)
    {
        var now = UserManager.Now;
        var gacha = FindGacha(gachaId);
        var behavior = FindGachaBehavior(gacha, gachaBehaviorId);
        var spinCount = GetGachaSpinCount(behavior, gachaBehaviorId);
        var behaviorType = behavior?["gachaBehaviorType"]?.GetValue<string>();

        var consumedCosts = ConsumeGachaCost(behavior, spinCount, isPriorityUsePaidJewel);

        var drawnCardIds = DrawGachaCards(gacha, behaviorType, spinCount);
        var obtainPrizes = new List<UserGachaSpinObtainPrize>();
        foreach (var cardId in drawnCardIds)
        {
            var isNew = GrantGachaCard(cardId);
            var costume3ds = isNew ? GrantInitialCostumes(cardId, now) : [];
            obtainPrizes.Add(new UserGachaSpinObtainPrize
            {
                card = new UserResource
                {
                    resourceId = cardId,
                    resourceType = "card",
                    resourceLevel = 1,
                    quantity = 1
                },
                newFlg = isNew,
                gachaLotteryType = "normal",
                costume3d = costume3ds,
                cardExtra = []
            });
        }

        var userGacha = UpsertUserGacha(gachaId, gachaBehaviorId, now);
        var obtainGachaCeilItems = GrantGachaCeilItem(gacha, gachaId, spinCount);

        UpdateRefreshableTypes(new []
        {
            nameof(SuiteUser.userCharacterMissionV2s),
            nameof(SuiteUser.userCharacterMissionV2Statuses),
            nameof(SuiteUser.userHonorMissions)
        });

        return new UserGachaResponse
        {
            consumedCosts = consumedCosts,
            obtainPrizes = obtainPrizes.ToArray(),
            obtainGachaCeilItems = obtainGachaCeilItems,
            obtainGachaBonusItems = [],
            obtainGachaExtras = [],
            obtainGachaFreebies = [],
            userGacha = userGacha,
            updatedResources = GetRefreshData(),
            obtainCharacterAllBonuses = [],
            obtainCharacterRepeatedBonuses = []
        };
    }

    public void SaveRateChoiceGachaWish(UserRateChoiceGachaWishRequest request)
    {
        if (request.rateChoiceGachaDetails == null)
            return;

        Data.userRateChoiceGachaWishes ??= [];
        var wishes = Data.userRateChoiceGachaWishes
            .Where(w => w.gachaId != request.gachaId)
            .ToList();

        wishes.AddRange(request.rateChoiceGachaDetails.Select(detail => new UserRateChoiceGachaWish
        {
            gachaId = request.gachaId,
            gachaDetailId = detail.gachaDetailId,
            rateChoiceGachaWishId = detail.rateChoiceGachaWishId
        }));

        Data.userRateChoiceGachaWishes = wishes
            .OrderBy(w => w.gachaId)
            .ThenBy(w => w.rateChoiceGachaWishId)
            .ThenBy(w => w.gachaDetailId)
            .ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userRateChoiceGachaWishes));
    }

    public UserGachaCeilExchangeResponse ExchangeGachaCeilItem(UserGachaCeilExchangeRequest request)
    {
        var exchangeRequest = request.gachaCeilExchangeRequest;
        if (exchangeRequest == null || exchangeRequest.gachaExchangeId <= 0 || exchangeRequest.exchangeCount <= 0)
        {
            return new UserGachaCeilExchangeResponse
            {
                obtainUserResources = [],
                updatedResources = GetRefreshData()
            };
        }

        var exchange = FindGachaCeilExchange(exchangeRequest.gachaExchangeId);
        var resourceBoxId = exchange?["resourceBoxId"]?.GetValue<int>() ?? 0;
        var obtainResources = BuildResourcesFromBox("gacha_ceil_exchange", resourceBoxId);

        var exchangeCount = exchangeRequest.exchangeCount;
        var cost = exchange?["gachaCeilExchangeCost"] as JsonObject;
        ConsumeGachaCeilExchangeCost(cost, exchangeCount);
        ConsumeGachaCeilSubstituteCost(exchange, exchangeRequest);

        var exchangeId = exchangeRequest.gachaExchangeId;
        var exchangeLimit = exchange?["exchangeLimit"]?.GetValue<int>() ?? 0;
        UpsertUserGachaCeilExchange(exchangeId, exchangeLimit, exchangeCount);

        var obtained = new Dictionary<(string? Type, int Id, int Level), UserResource>();
        for (var i = 0; i < exchangeCount; i++)
        {
            foreach (var resource in obtainResources)
            {
                ApplyResource(resource);
                AddObtainedResource(obtained, resource);
            }
        }

        return new UserGachaCeilExchangeResponse
        {
            obtainUserResources = obtained.Values.ToArray(),
            updatedResources = GetRefreshData()
        };
    }

    private static JsonObject? FindGacha(int gachaId)
    {
        foreach (var gacha in LoadGachas())
        {
            if (gacha is JsonObject obj && obj["id"]?.GetValue<int>() == gachaId)
                return obj;
        }

        return null;
    }

    private static JsonObject? FindGachaBehavior(JsonObject? gacha, int gachaBehaviorId)
    {
        if (gacha?["gachaBehaviors"] is not JsonArray behaviors)
            return null;

        foreach (var behavior in behaviors)
        {
            if (behavior is JsonObject obj && obj["id"]?.GetValue<int>() == gachaBehaviorId)
                return obj;
        }

        return null;
    }

    private static int GetGachaSpinCount(JsonObject? behavior, int gachaBehaviorId)
    {
        var spinCount = behavior?["spinCount"]?.GetValue<int>() ?? 0;
        if (spinCount > 0)
            return spinCount;

        return 1;
    }

    private UserResource[] ConsumeGachaCost(JsonObject? behavior, int spinCount, bool isPriorityUsePaidJewel)
    {
        var resourceCategory = behavior?["resourceCategory"]?.GetValue<string>();
        if (string.Equals(resourceCategory, "free_resource", StringComparison.Ordinal))
            return [];

        var costResourceType = behavior?["costResourceType"]?.GetValue<string>();
        var costResourceId = behavior?["costResourceId"]?.GetValue<int>() ?? 0;
        var costQuantity = behavior?["costResourceQuantity"]?.GetValue<int>() ?? 300 * spinCount;
        if (costQuantity <= 0 || string.IsNullOrEmpty(costResourceType))
            return [];

        return costResourceType switch
        {
            "jewel" =>
            [
                new UserResource
                {
                    resourceType = "jewel",
                    resourceLevel = 0,
                    quantity = ConsumeJewelForGacha(costQuantity, isPriorityUsePaidJewel)
                }
            ],
            "paid_jewel" =>
            [
                new UserResource
                {
                    resourceType = "paid_jewel",
                    resourceLevel = 0,
                    quantity = ConsumePaidJewelForGacha(costQuantity)
                }
            ],
            "gacha_ticket" =>
            [
                new UserResource
                {
                    resourceId = costResourceId,
                    resourceType = "gacha_ticket",
                    resourceLevel = 1,
                    quantity = ConsumeGachaTicketForGacha(costResourceId, costQuantity)
                }
            ],
            _ => []
        };
    }

    private int ConsumeJewelForGacha(int quantity, bool isPriorityUsePaidJewel)
    {
        Data.userChargedCurrency ??= new ChargedCurrency { paidUnitPrices = [] };

        if (isPriorityUsePaidJewel)
        {
            var paidCost = Math.Min(Math.Max(0, Data.userChargedCurrency.paid), quantity);
            Data.userChargedCurrency.paid -= paidCost;
            var remainingCost = quantity - paidCost;
            if (remainingCost > 0)
                Data.userChargedCurrency.free = Math.Max(0, Math.Max(0, Data.userChargedCurrency.free) - remainingCost);
        }
        else
        {
            var freeCost = Math.Min(Math.Max(0, Data.userChargedCurrency.free), quantity);
            Data.userChargedCurrency.free -= freeCost;
            var remainingCost = quantity - freeCost;
            if (remainingCost > 0)
                Data.userChargedCurrency.paid = Math.Max(0, Math.Max(0, Data.userChargedCurrency.paid) - remainingCost);
        }

        UpdateRefreshableType(nameof(SuiteUser.userChargedCurrency));
        return Math.Max(0, Data.userChargedCurrency.paid) + Math.Max(0, Data.userChargedCurrency.free);
    }

    private int ConsumePaidJewelForGacha(int quantity)
    {
        Data.userChargedCurrency ??= new ChargedCurrency { paidUnitPrices = [] };
        Data.userChargedCurrency.paid = Math.Max(0, Math.Max(0, Data.userChargedCurrency.paid) - quantity);
        UpdateRefreshableType(nameof(SuiteUser.userChargedCurrency));
        return Data.userChargedCurrency.paid;
    }

    private int ConsumeGachaTicketForGacha(int gachaTicketId, int quantity)
    {
        if (gachaTicketId <= 0 || quantity <= 0)
            return 0;

        Data.userGachaTickets ??= [];
        var tickets = Data.userGachaTickets.ToList();
        var ticket = tickets.FirstOrDefault(t => t.gachaTicketId == gachaTicketId);
        if (ticket == null)
        {
            ticket = new UserGachaTicket
            {
                userId = GetUserId(),
                gachaTicketId = gachaTicketId
            };
            tickets.Add(ticket);
        }

        ticket.quantity = Math.Max(0, ticket.quantity - quantity);
        Data.userGachaTickets = tickets.OrderBy(t => t.gachaTicketId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaTickets));
        return ticket.quantity;
    }

    private static int[] DrawGachaCards(JsonObject? gacha, string? behaviorType, int spinCount)
    {
        var cardIds = new int[spinCount];
        for (var i = 0; i < cardIds.Length; i++)
            cardIds[i] = DrawGachaCard(gacha);

        if (cardIds.Length == 0)
            return cardIds;

        if (string.Equals(behaviorType, "over_rarity_4_once", StringComparison.Ordinal) &&
            !cardIds.Any(IsRarity4OrHigher))
        {
            cardIds[^1] = DrawGachaCard(gacha, IsRarity4OrHigher);
        }
        else if (string.Equals(behaviorType, "over_rarity_3_once", StringComparison.Ordinal) &&
                 !cardIds.Any(IsRarity3OrHigher))
        {
            cardIds[^1] = DrawGachaCard(gacha, IsRarity3OrHigher);
        }

        return cardIds;
    }

    private static int DrawGachaCard(JsonObject? gacha, Func<int, bool>? cardFilter = null)
    {
        var rarityType = DrawGachaRarity(gacha, cardFilter);
        return DrawGachaCardByRarity(gacha, rarityType, cardFilter);
    }

    private static string? DrawGachaRarity(JsonObject? gacha, Func<int, bool>? cardFilter)
    {
        if (gacha?["gachaCardRarityRates"] is not JsonArray rates)
            return null;

        var candidates = rates
            .OfType<JsonObject>()
            .Where(rate => rate["lotteryType"]?.GetValue<string>() == "normal")
            .Select(rate => new
            {
                RarityType = rate["cardRarityType"]?.GetValue<string>(),
                Rate = rate["rate"]?.GetValue<double>() ?? 0
            })
            .Where(rate => !string.IsNullOrEmpty(rate.RarityType) &&
                           rate.Rate > 0 &&
                           HasGachaCardInRarity(gacha, rate.RarityType!, cardFilter))
            .ToArray();

        var totalRate = candidates.Sum(rate => rate.Rate);
        if (totalRate <= 0)
            return null;

        var selected = Random.Shared.NextDouble() * totalRate;
        double running = 0;
        foreach (var candidate in candidates)
        {
            running += candidate.Rate;
            if (selected < running)
                return candidate.RarityType;
        }

        return candidates[^1].RarityType;
    }

    private static bool HasGachaCardInRarity(JsonObject? gacha, string rarityType, Func<int, bool>? cardFilter)
    {
        if (gacha?["gachaDetails"] is not JsonArray details)
            return false;

        foreach (var detail in details)
        {
            if (detail is not JsonObject obj)
                continue;

            var cardId = obj["cardId"]?.GetValue<int>() ?? 0;
            if (cardId <= 0 || cardFilter?.Invoke(cardId) == false)
                continue;

            if (string.Equals(GetCardRarityType(cardId), rarityType, StringComparison.Ordinal))
                return true;
        }

        return false;
    }

    private static int DrawGachaCardByRarity(JsonObject? gacha, string? rarityType, Func<int, bool>? cardFilter)
    {
        if (gacha?["gachaDetails"] is not JsonArray details)
            return DrawFallbackCard(cardFilter);

        var candidates = details
            .OfType<JsonObject>()
            .Select(detail => new
            {
                CardId = detail["cardId"]?.GetValue<int>() ?? 0,
                Weight = detail["weight"]?.GetValue<int>() ?? 0
            })
            .Where(detail => detail.CardId > 0 && detail.Weight > 0)
            .Where(detail => cardFilter?.Invoke(detail.CardId) != false)
            .Where(detail => string.IsNullOrEmpty(rarityType) ||
                             string.Equals(GetCardRarityType(detail.CardId), rarityType, StringComparison.Ordinal))
            .ToArray();

        if (candidates.Length == 0)
            return DrawFallbackCard(cardFilter);

        var totalWeight = candidates.Sum(detail => (long)detail.Weight);
        if (totalWeight <= 0)
            return DrawFallbackCard(cardFilter);

        var selected = Random.Shared.NextInt64(totalWeight);
        long running = 0;
        foreach (var candidate in candidates)
        {
            running += candidate.Weight;
            if (selected < running)
                return candidate.CardId;
        }

        return DrawFallbackCard(cardFilter);
    }

    private static int DrawFallbackCard(Func<int, bool>? cardFilter)
    {
        var candidates = LoadCards()
            .OfType<JsonObject>()
            .Select(card => card["id"]?.GetValue<int>() ?? 0)
            .Where(cardId => cardId > 0 && !string.Equals(GetCardRarityType(cardId), "rarity_1", StringComparison.Ordinal))
            .Where(cardId => cardFilter?.Invoke(cardId) != false)
            .ToArray();

        return candidates.Length == 0 ? 1 : candidates[Random.Shared.Next(candidates.Length)];
    }

    private static bool IsRarity3OrHigher(int cardId) =>
        RarityRank(GetCardRarityType(cardId)) >= 3;

    private static bool IsRarity4OrHigher(int cardId) =>
        RarityRank(GetCardRarityType(cardId)) >= 4;

    private static int RarityRank(string? rarityType) =>
        rarityType switch
        {
            "rarity_birthday" => 4,
            "rarity_4" => 4,
            "rarity_3" => 3,
            "rarity_2" => 2,
            "rarity_1" => 1,
            _ => 0
        };

    private static string? GetCardRarityType(int cardId) =>
        FindCard(cardId)?["cardRarityType"]?.GetValue<string>();

    private static JsonObject? FindCard(int cardId)
    {
        foreach (var card in LoadCards())
        {
            if (card is JsonObject obj && obj["id"]?.GetValue<int>() == cardId)
                return obj;
        }

        return null;
    }

    private bool GrantGachaCard(int cardId)
    {
        Data.userCards ??= [];
        var existing = Data.userCards.FirstOrDefault(c => c.cardId == cardId);
        if (existing == null)
        {
            AddCard(cardId);
            return true;
        }

        existing.duplicateCount++;
        UpdateRefreshableType(nameof(SuiteUser.userCards));
        return false;
    }

    private UserResource[] GrantInitialCostumes(int cardId, long now)
    {
        var costumeIds = FindCardCostume3dIds(cardId);
        if (costumeIds.Length == 0)
            return [];

        Data.userCostume3dStatuses ??= [];
        var statuses = Data.userCostume3dStatuses.ToList();
        var obtained = new List<UserResource>();
        foreach (var costumeId in costumeIds)
        {
            if (statuses.Any(s => s.costume3dId == costumeId))
                continue;

            statuses.Add(new UserCostume3DStatus
            {
                costume3dId = costumeId,
                obtainedAt = now,
                status = "available"
            });
            obtained.Add(new UserResource
            {
                resourceId = costumeId,
                resourceType = "costume_3d",
                resourceLevel = 0,
                quantity = 1
            });
        }

        if (obtained.Count == 0)
            return [];

        Data.userCostume3dStatuses = statuses.OrderBy(s => s.costume3dId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userCostume3dStatuses));
        UpdateRefreshableType(nameof(SuiteUser.userCostume3dShopItems));
        return obtained.ToArray();
    }

    private void GrantCostume3d(int costume3dId)
    {
        if (costume3dId <= 0)
            return;

        Data.userCostume3dStatuses ??= [];
        var statuses = Data.userCostume3dStatuses.ToList();
        if (statuses.Any(s => s.costume3dId == costume3dId))
            return;

        statuses.Add(new UserCostume3DStatus
        {
            costume3dId = costume3dId,
            obtainedAt = UserManager.Now,
            status = "available"
        });
        Data.userCostume3dStatuses = statuses.OrderBy(s => s.costume3dId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userCostume3dStatuses));
        UpdateRefreshableType(nameof(SuiteUser.userCostume3dShopItems));
    }

    private static int[] FindCardCostume3dIds(int cardId)
    {
        var result = new List<int>();
        foreach (var costume in LoadCardCostume3ds())
        {
            if (costume is JsonObject obj && obj["cardId"]?.GetValue<int>() == cardId)
            {
                var costumeId = obj["costume3dId"]?.GetValue<int>() ?? 0;
                if (costumeId > 0)
                    result.Add(costumeId);
            }
        }

        return result.ToArray();
    }

    private UserGacha UpsertUserGacha(int gachaId, int gachaBehaviorId, long now)
    {
        Data.userGachas ??= [];
        var gachas = Data.userGachas.ToList();
        var userGacha = gachas.FirstOrDefault(g =>
            g.gachaId == gachaId &&
            g.gachaBehaviorId == gachaBehaviorId);

        if (userGacha == null)
        {
            userGacha = new UserGacha
            {
                userId = GetUserId(),
                gachaId = gachaId,
                gachaBehaviorId = gachaBehaviorId
            };
            gachas.Add(userGacha);
        }

        userGacha.count++;
        userGacha.lastSpinAt = now;
        Data.userGachas = gachas.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachas));
        return userGacha;
    }

    private UserResource[] GrantGachaCeilItem(JsonObject? gacha, int gachaId, int quantity)
    {
        var ceilItemId = ResolveGachaCeilItemId(gacha, gachaId);
        if (ceilItemId <= 0 || quantity <= 0)
            return [];

        Data.userGachaCeilItems ??= [];
        var ceilItems = Data.userGachaCeilItems.ToList();
        var item = ceilItems.FirstOrDefault(i => i.gachaCeilItemId == ceilItemId);
        if (item == null)
        {
            item = new UserGachaCeilItem
            {
                userId = GetUserId(),
                gachaCeilItemId = ceilItemId
            };
            ceilItems.Add(item);
        }

        item.quantity += quantity;
        Data.userGachaCeilItems = ceilItems.OrderBy(i => i.gachaCeilItemId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaCeilItems));

        return
        [
            new UserResource
            {
                resourceId = ceilItemId,
                resourceType = "gacha_ceil_item",
                resourceLevel = 0,
                quantity = quantity
            }
        ];
    }

    private void GrantGachaCeilItem(int gachaCeilItemId, int quantity)
    {
        if (gachaCeilItemId <= 0 || quantity <= 0)
            return;

        Data.userGachaCeilItems ??= [];
        var ceilItems = Data.userGachaCeilItems.ToList();
        var item = ceilItems.FirstOrDefault(i => i.gachaCeilItemId == gachaCeilItemId);
        if (item == null)
        {
            item = new UserGachaCeilItem
            {
                userId = GetUserId(),
                gachaCeilItemId = gachaCeilItemId
            };
            ceilItems.Add(item);
        }

        item.quantity += quantity;
        Data.userGachaCeilItems = ceilItems.OrderBy(i => i.gachaCeilItemId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaCeilItems));
    }

    private static int ResolveGachaCeilItemId(JsonObject? gacha, int gachaId)
    {
        var fromGacha = gacha?["gachaCeilItemId"]?.GetValue<int>() ?? 0;
        if (fromGacha > 0)
            return fromGacha;

        foreach (var item in LoadGachaCeilItems())
        {
            if (item is JsonObject obj && obj["gachaId"]?.GetValue<int>() == gachaId)
                return obj["id"]?.GetValue<int>() ?? 0;
        }

        return 0;
    }

    private static JsonObject? FindGachaCeilExchange(int gachaCeilExchangeId)
    {
        foreach (var summary in LoadGachaCeilExchangeSummaries())
        {
            if (summary is not JsonObject summaryObj ||
                summaryObj["gachaCeilExchanges"] is not JsonArray exchanges)
                continue;

            foreach (var exchange in exchanges)
            {
                if (exchange is JsonObject exchangeObj &&
                    exchangeObj["id"]?.GetValue<int>() == gachaCeilExchangeId)
                {
                    return exchangeObj;
                }
            }
        }

        return null;
    }

    private void ConsumeGachaCeilExchangeCost(JsonObject? cost, int exchangeCount)
    {
        if (cost == null || exchangeCount <= 0)
            return;

        var resourceType = cost["resourceType"]?.GetValue<string>();
        var resourceId = cost["resourceId"]?.GetValue<int>() ?? cost["gachaCeilItemId"]?.GetValue<int>() ?? 0;
        var quantity = (cost["quantity"]?.GetValue<int>() ?? 0) * exchangeCount;
        ConsumeResource(resourceType, resourceId, quantity);
    }

    private void ConsumeGachaCeilSubstituteCost(JsonObject? exchange, UserGachaCeilItemExchangeRequest request)
    {
        if (exchange == null ||
            request.gachaCeilExchangeSubstituteCostId <= 0 ||
            request.substituteCostCount <= 0 ||
            exchange["gachaCeilExchangeSubstituteCosts"] is not JsonArray costs)
        {
            return;
        }

        foreach (var entry in costs.OfType<JsonObject>())
        {
            if (entry["id"]?.GetValue<int>() != request.gachaCeilExchangeSubstituteCostId)
                continue;

            var resourceType = entry["resourceType"]?.GetValue<string>();
            var resourceId = entry["resourceId"]?.GetValue<int>() ?? 0;
            var quantity = (entry["substituteQuantity"]?.GetValue<int>() ?? 0) * request.substituteCostCount;
            ConsumeResource(resourceType, resourceId, quantity);
            UpsertUserGachaCeilExchangeSubstituteCost(request.gachaExchangeId, request.substituteCostCount);
            return;
        }
    }

    private void UpsertUserGachaCeilExchange(int gachaCeilExchangeId, int exchangeLimit, int exchangeCount)
    {
        Data.userGachaCeilExchanges ??= [];
        var exchanges = Data.userGachaCeilExchanges.ToList();
        var userExchange = exchanges.FirstOrDefault(e => e.gachaCeilExchangeId == gachaCeilExchangeId);
        if (userExchange == null)
        {
            userExchange = new UserGachaCeilExchange
            {
                userId = GetUserId(),
                gachaCeilExchangeId = gachaCeilExchangeId,
                exchangeStatus = "exchangeable",
                exchangeRemaining = exchangeLimit
            };
            exchanges.Add(userExchange);
        }

        if (exchangeLimit > 0)
        {
            userExchange.exchangeRemaining = Math.Max(0, userExchange.exchangeRemaining - exchangeCount);
            userExchange.exchangeStatus = userExchange.exchangeRemaining == 0 ? "not_exchangeable" : "exchangeable";
        }

        Data.userGachaCeilExchanges = exchanges.OrderBy(e => e.gachaCeilExchangeId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaCeilExchanges));
    }

    private void UpsertUserGachaCeilExchangeSubstituteCost(int gachaCeilExchangeId, int usedCount)
    {
        Data.userGachaCeilExchangeSubstituteCosts ??= [];
        var costs = Data.userGachaCeilExchangeSubstituteCosts.ToList();
        var cost = costs.FirstOrDefault(c => c.gachaCeilExchangeId == gachaCeilExchangeId);
        if (cost == null)
        {
            cost = new UserGachaCeilExchangeSubstituteCost
            {
                gachaCeilExchangeId = gachaCeilExchangeId
            };
            costs.Add(cost);
        }

        cost.substituteCostUsedCount += usedCount;
        Data.userGachaCeilExchangeSubstituteCosts = costs.OrderBy(c => c.gachaCeilExchangeId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaCeilExchangeSubstituteCosts));
    }

    private void ConsumeGachaCeilItem(int gachaCeilItemId, int quantity)
    {
        if (gachaCeilItemId <= 0 || quantity <= 0)
            return;

        Data.userGachaCeilItems ??= [];
        var ceilItems = Data.userGachaCeilItems.ToList();
        var item = ceilItems.FirstOrDefault(i => i.gachaCeilItemId == gachaCeilItemId);
        if (item == null)
        {
            item = new UserGachaCeilItem
            {
                userId = GetUserId(),
                gachaCeilItemId = gachaCeilItemId
            };
            ceilItems.Add(item);
        }

        item.quantity = Math.Max(0, item.quantity - quantity);
        Data.userGachaCeilItems = ceilItems.OrderBy(i => i.gachaCeilItemId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userGachaCeilItems));
    }

    public void ExchangeCards(UserCard[]? userCards)
    {
        if (userCards == null || userCards.Length == 0)
            return;

        Data.userCards ??= [];
        var cards = Data.userCards;
        foreach (var requestCard in userCards.Where(c => c.cardId > 0))
        {
            var current = cards.FirstOrDefault(c => c.cardId == requestCard.cardId);
            if (current == null)
            {
                requestCard.userId = GetUserId();
                cards.Add(requestCard);
                continue;
            }

            current.level = requestCard.level;
            current.exp = requestCard.exp;
            current.totalExp = requestCard.totalExp;
            current.skillLevel = requestCard.skillLevel;
            current.skillExp = requestCard.skillExp;
            current.totalSkillExp = requestCard.totalSkillExp;
            current.masterRank = requestCard.masterRank;
            current.specialTrainingStatus = requestCard.specialTrainingStatus;
            current.defaultImage = requestCard.defaultImage;
            current.duplicateCount = requestCard.duplicateCount;
            current.createdAt = requestCard.createdAt;
            current.episodes = requestCard.episodes;
        }

        Data.userCards = cards.OrderBy(c => c.cardId).ToList();
        UpdateRefreshableType(nameof(SuiteUser.userCards));
    }

    public string SetUserInherit(string password)
    {
        var inheritId = GenerateRandomString(16);

        NotSuite.InheritId = inheritId;
        NotSuite.InheritPassword = password;

        Data.userInherit = new UserInherit { inheritId = inheritId };
        UpdateRefreshableType(nameof(SuiteUser.userInherit));
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
        return !String.IsNullOrEmpty(inheritId) &&
               !String.IsNullOrEmpty(password) && 
               NotSuite.InheritId == inheritId &&
               NotSuite.InheritPassword == password;
    }

    public void RemoveTopic(int topicId)
    {
        if (Data.unreadUserTopics == null) return;
        Data.unreadUserTopics = Data.unreadUserTopics
            .Where(t => t.topicId != topicId).ToArray();
    }

    public void ReadEpisode(int specialEpisodeId) =>
        ReadStoryEpisode("special_story", specialEpisodeId);

    public void ReadStoryEpisode(string storyType, int episodeId, bool isNotSkipped = false)
    {
        switch (storyType)
        {
            case "unit_story":
                MarkEpisodeRead(Data.userUnitEpisodeStatuses, episodeId,
                    nameof(SuiteUser.userUnitEpisodeStatuses), isNotSkipped);
                break;
            case "special_story":
                MarkEpisodeRead(Data.userSpecialEpisodeStatuses, episodeId,
                    nameof(SuiteUser.userSpecialEpisodeStatuses), isNotSkipped);
                break;
            case "character_profile_story":
                MarkEpisodeRead(Data.userCharacterProfileEpisodeStatuses, episodeId,
                    nameof(SuiteUser.userCharacterProfileEpisodeStatuses), isNotSkipped);
                break;
            case "event_story":
                MarkEventEpisodeRead(Data.userEventEpisodeStatuses, episodeId,
                    nameof(SuiteUser.userEventEpisodeStatuses), isNotSkipped);
                break;
            case "archive_event_story":
                MarkArchiveEventEpisodeRead(Data.userArchiveEventEpisodeStatuses, episodeId,
                    nameof(SuiteUser.userArchiveEventEpisodeStatuses), isNotSkipped);
                break;
            case "card_story":
                MarkCardEpisodeRead(episodeId, isNotSkipped);
                break;
        }
    }

    public void ReleaseStoryEpisode(string storyType, int episodeId)
    {
        if (storyType == "card_story")
            ReleaseCardEpisode(episodeId);
    }

    private void MarkEpisodeRead(UserEpisodeStatus[]? statuses, int episodeId, string fieldName, bool isNotSkipped)
    {
        if (statuses == null) return;

        foreach (var status in statuses)
        {
            if (status.episodeId != episodeId) continue;

            status.status = "already_read";
            status.isNotSkipped = isNotSkipped;
            UpdateRefreshableType(fieldName);
            return;
        }
    }

    private void MarkEventEpisodeRead(UserEventEpisodeStatus[]? statuses, int episodeId, string fieldName, bool isNotSkipped)
    {
        if (statuses == null) return;

        foreach (var status in statuses)
        {
            if (status.episodeId != episodeId) continue;

            status.status = "already_read";
            status.isNotSkipped = isNotSkipped;
            UpdateRefreshableType(fieldName);
            return;
        }
    }

    private void MarkArchiveEventEpisodeRead(UserArchiveEventEpisodeStatus[]? statuses, int episodeId, string fieldName, bool isNotSkipped)
    {
        if (statuses == null) return;

        foreach (var status in statuses)
        {
            if (status.episodeId != episodeId) continue;

            status.status = "already_read";
            status.isNotSkipped = isNotSkipped;
            UpdateRefreshableType(fieldName);
            return;
        }
    }

    private void MarkCardEpisodeRead(int cardEpisodeId, bool isNotSkipped)
    {
        if (Data.userCards == null) return;

        foreach (var card in Data.userCards)
        {
            if (card.episodes == null) continue;

            foreach (var episode in card.episodes)
            {
                if (episode.cardEpisodeId != cardEpisodeId) continue;

                episode.scenarioStatus = "already_read";
                episode.scenarioStatusReasons = [];
                episode.isNotSkipped = isNotSkipped;
                UpdateRefreshableType(nameof(SuiteUser.userCards));
                return;
            }
        }
    }

    private void ReleaseCardEpisode(int cardEpisodeId)
    {
        if (Data.userCards == null) return;

        foreach (var card in Data.userCards)
        {
            if (card.episodes == null) continue;

            foreach (var episode in card.episodes)
            {
                if (episode.cardEpisodeId != cardEpisodeId) continue;

                episode.scenarioStatus = "released";
                episode.scenarioStatusReasons = [];
                UpdateRefreshableType(nameof(SuiteUser.userCards));
                return;
            }
        }
    }

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
            receivedAt = UserManager.Now,
            reason = present.reason
        });

        return present;
    }

    public List<UserPresentHistoryData> GetPresentHistory()
    {
        return NotSuite.PresentHistories;
    }

    public void UpdateProfile(UserProfile newProfile)
    {
        if (Data.userProfile == null) return;
        // 保留原 userId
        newProfile.userId = Data.userProfile.userId;
        Data.userProfile = newProfile;
        UpdateRefreshableType(nameof(SuiteUser.userProfile));
    }

    public void MergeUserGamedata(UserGamedata patch)
    {
        if (Data.userGamedata == null)
        {
            Data.userGamedata = patch;
            UpdateRefreshableType(nameof(SuiteUser.userGamedata));
            return;
        }

        var current = Data.userGamedata;
        if (patch.userId != 0) current.userId = patch.userId;
        if (patch.name != null) current.name = patch.name;
        if (patch.deck != 0) current.deck = patch.deck;
        if (patch.rank != 0) current.rank = patch.rank;
        if (patch.exp != 0) current.exp = patch.exp;
        if (patch.totalExp != 0) current.totalExp = patch.totalExp;
        if (patch.coin != 0) current.coin = patch.coin;
        if (patch.virtualCoin != 0) current.virtualCoin = patch.virtualCoin;
        if (patch.lastLoginAt != 0) current.lastLoginAt = patch.lastLoginAt;
        current.customProfileId = patch.customProfileId;

        UpdateRefreshableType(nameof(SuiteUser.userGamedata));
    }

    public void UpdateUserGamedata(UserGamedata newGamedata) =>
        MergeUserGamedata(newGamedata);
    

    public void SetCurrentCustomProfile(int? customProfileId)
    {
        Data.userGamedata ??= new UserGamedata { userId = GetUserId() };
        Data.userGamedata.customProfileId = customProfileId;
        UpdateRefreshableType(nameof(SuiteUser.userGamedata));
    }

    public void SaveCustomProfile(
        int customProfileId,
        string? name,
        List<UserCustomProfileCardOrder>? customProfileCardOrders)
    {
        var profiles = Data.userCustomProfiles!.ToList();
        var profile = profiles.FirstOrDefault(p => p.customProfileId == customProfileId);
        if (profile == null)
        {
            profiles.Add(new UserCustomProfile
            {
                customProfileId = customProfileId,
                name = name ?? ""
            });
        }
        else if (name != null)
        {
            profile.name = name;
        }

        var cards = Data.userCustomProfileCards!.ToList();
        if (customProfileCardOrders != null)
        {
            foreach (var order in customProfileCardOrders.Where(o => o.customProfileId == customProfileId))
            {
                var card = cards.FirstOrDefault(c =>
                    c.customProfileId == customProfileId &&
                    c.customProfileCardId == order.customProfileCardId);
                if (card != null)
                    card.seq = order.seq;
            }
        }

        Data.userCustomProfiles = profiles.ToArray();
        Data.userCustomProfileCards = cards.ToArray();
        UpdateCustomProfileResourceUsages(customProfileId);

        UpdateRefreshableType(nameof(SuiteUser.userCustomProfiles));
        UpdateRefreshableType(nameof(SuiteUser.userCustomProfileCards));
    }

    public void SaveCustomProfileCard(
        int customProfileId,
        int customProfileCardId,
        UserSaveCustomProfileCardRequest request)
    {
        EnsureCustomProfileExists(customProfileId);

        var cards = Data.userCustomProfileCards!.ToList();
        var card = cards.FirstOrDefault(c =>
            c.customProfileId == customProfileId &&
            c.customProfileCardId == customProfileCardId);

        if (card == null)
        {
            var nextSeq = cards
                .Where(c => c.customProfileId == customProfileId)
                .Select(c => c.seq)
                .DefaultIfEmpty(0)
                .Max() + 1;

            var thumbnailPath = CustomProfileThumbnailStore.SaveThumbnail(request.thumbnail);
            cards.Add(new UserCustomProfileCard
            {
                customProfileId = customProfileId,
                customProfileCardId = customProfileCardId,
                thumbnailPath = thumbnailPath,
                customProfileCard = request.customProfileCard,
                seq = nextSeq
            });
        }
        else
        {
            card.thumbnailPath = CustomProfileThumbnailStore.SaveThumbnail(request.thumbnail, card.thumbnailPath);
            card.customProfileCard = request.customProfileCard;
        }

        Data.userCustomProfileCards = cards.ToArray();
        UpdateCustomProfileResourceUsages(customProfileId);
        UpdateRefreshableType(nameof(SuiteUser.userCustomProfileCards));
    }

    public void DeleteCustomProfileCards(int customProfileId, int[] customProfileCardIds)
    {
        var deleteIds = customProfileCardIds.ToHashSet();
        var cards = Data.userCustomProfileCards!
            .Where(c => c.customProfileId != customProfileId || !deleteIds.Contains(c.customProfileCardId))
            .ToList();

        var seq = 1;
        foreach (var card in cards
            .Where(c => c.customProfileId == customProfileId)
            .OrderBy(c => c.seq)
            .ThenBy(c => c.customProfileCardId))
        {
            card.seq = seq++;
        }

        Data.userCustomProfileCards = cards.ToArray();
        UpdateCustomProfileResourceUsages(customProfileId);
        UpdateRefreshableType(nameof(SuiteUser.userCustomProfileCards));
    }

    public void UpdateCustomProfileResourceUsages(int customProfileId)
    {
        var usageCounts = new Dictionary<int, int>();
        foreach (var card in Data.userCustomProfileCards!.Where(c => c.customProfileId == customProfileId))
        {
            var collections = card.customProfileCard?.collections;
            if (collections == null) continue;

            foreach (var collection in collections)
            {
                if (collection.id <= 0) continue;
                usageCounts.TryGetValue(collection.id, out var current);
                usageCounts[collection.id] = current + 1;
            }
        }

        var usages = Data.userCustomProfileResourceUsages!
            .Where(u => u.customProfileId != customProfileId)
            .ToList();

        usages.AddRange(usageCounts
            .OrderBy(kv => kv.Key)
            .Select(kv => new UserCustomProfileResourceUsages
            {
                customProfileId = customProfileId,
                customProfileResourceId = kv.Key,
                quantity = kv.Value
            }));

        Data.userCustomProfileResourceUsages = usages.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userCustomProfileResourceUsages));
    }

    private void EnsureCustomProfileExists(int customProfileId)
    {
        var profiles = Data.userCustomProfiles!.ToList();
        if (profiles.Any(p => p.customProfileId == customProfileId))
            return;

        profiles.Add(new UserCustomProfile
        {
            customProfileId = customProfileId,
            name = ""
        });
        Data.userCustomProfiles = profiles.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userCustomProfiles));
    }

    public void PurchaseShopItem(int shopId, int shopItemId)
    {
        var shopItem = FindShopItem(shopId, shopItemId);
        var wasSoldOut = IsShopItemSoldOut(shopId, shopItemId);

        MarkShopItemSoldOut(shopId, shopItemId);

        if (!wasSoldOut && shopItem?["costs"] is JsonArray costs)
            ConsumeShopItemCosts(costs);

        var resourceBoxId = shopItem?["resourceBoxId"]?.GetValue<int>() ?? shopItemId;
        ApplyShopItemResources(resourceBoxId);
    }

    private static JsonObject? FindShopItem(int shopId, int shopItemId)
    {
        foreach (var item in LoadShopItems())
        {
            if (item is JsonObject obj &&
                obj["id"]?.GetValue<int>() == shopItemId &&
                obj["shopId"]?.GetValue<int>() == shopId)
            {
                return obj;
            }
        }

        return null;
    }

    private bool IsShopItemSoldOut(int shopId, int shopItemId) =>
        Data.userShops?
            .FirstOrDefault(s => s.shopId == shopId)?
            .userShopItems?
            .Any(i => i.shopItemId == shopItemId &&
                      string.Equals(i.status, UserShopItem.STATUS_SOLD_OUT, StringComparison.Ordinal)) == true;

    private void MarkShopItemSoldOut(int shopId, int shopItemId)
    {
        Data.userShops ??= [];
        var shops = Data.userShops.ToList();
        var shop = shops.FirstOrDefault(s => s.shopId == shopId);
        if (shop == null)
        {
            shop = new UserShop
            {
                shopId = shopId,
                userShopItems = []
            };
            shops.Add(shop);
            Data.userShops = shops.ToArray();
        }

        var items = (shop.userShopItems ?? []).ToList();
        var item = items.FirstOrDefault(i => i.shopItemId == shopItemId);
        if (item == null)
        {
            item = new UserShopItem
            {
                shopItemId = shopItemId
            };
            items.Add(item);
        }

        item.status = UserShopItem.STATUS_SOLD_OUT;
        shop.userShopItems = items.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userShops));
    }

    private void ConsumeShopItemCosts(JsonArray costs)
    {
        foreach (var entry in costs)
        {
            if (entry is not JsonObject costEntry ||
                costEntry["cost"] is not JsonObject cost)
                continue;

            var resourceType = cost["resourceType"]?.GetValue<string>();
            var resourceId = cost["resourceId"]?.GetValue<int>() ?? 0;
            var quantity = cost["quantity"]?.GetValue<int>() ?? 0;
            if (quantity <= 0)
                continue;

            switch (resourceType)
            {
                case "material":
                    ConsumeMaterial(resourceId, quantity);
                    break;
                case "coin":
                    if (Data.userGamedata != null)
                    {
                        Data.userGamedata.coin = Math.Max(0, Data.userGamedata.coin - quantity);
                        UpdateRefreshableType(nameof(SuiteUser.userGamedata));
                    }
                    break;
                case "jewel":
                    ConsumeJewel(quantity);
                    break;
            }
        }
    }

    private void ConsumeMaterial(int materialId, int quantity)
    {
        if (materialId <= 0 || quantity <= 0)
            return;

        Data.userMaterials ??= [];
        var materials = Data.userMaterials.ToList();
        var material = materials.FirstOrDefault(m => m.materialId == materialId);
        if (material == null)
        {
            material = new UserMaterial
            {
                materialId = materialId
            };
            materials.Add(material);
        }

        material.quantity = Math.Max(0, material.quantity - quantity);
        Data.userMaterials = materials.OrderBy(m => m.materialId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userMaterials));
    }

    private void ConsumeJewel(int quantity)
    {
        if (quantity <= 0)
            return;

        Data.userChargedCurrency ??= new ChargedCurrency { paidUnitPrices = [] };

        var freeCost = Math.Min(Data.userChargedCurrency.free, quantity);
        Data.userChargedCurrency.free -= freeCost;

        var remainingCost = quantity - freeCost;
        if (remainingCost > 0)
            Data.userChargedCurrency.paid = Math.Max(0, Data.userChargedCurrency.paid - remainingCost);

        UpdateRefreshableType(nameof(SuiteUser.userChargedCurrency));
    }

    private void ConsumeResource(string? resourceType, int resourceId, int quantity)
    {
        if (quantity <= 0)
            return;

        switch (resourceType)
        {
            case "material":
                ConsumeMaterial(resourceId, quantity);
                break;
            case "coin":
                if (Data.userGamedata != null)
                {
                    Data.userGamedata.coin = Math.Max(0, Data.userGamedata.coin - quantity);
                    UpdateRefreshableType(nameof(SuiteUser.userGamedata));
                }
                break;
            case "jewel":
                ConsumeJewel(quantity);
                break;
            case "paid_jewel":
                ConsumePaidJewelForGacha(quantity);
                break;
            case "gacha_ceil_item":
                ConsumeGachaCeilItem(resourceId, quantity);
                break;
            case "gacha_ticket":
                ConsumeGachaTicketForGacha(resourceId, quantity);
                break;
        }
    }

    private void ApplyResource(UserResource resource)
    {
        if (resource.quantity <= 0)
            return;

        switch (resource.resourceType)
        {
            case "card":
                for (var i = 0; i < resource.quantity; i++)
                    GrantGachaCard(resource.resourceId);
                break;
            case "costume_3d":
                GrantCostume3d(resource.resourceId);
                break;
            case "music":
                GrantMusic(resource.resourceId);
                GrantDefaultMusicVocals(resource.resourceId);
                break;
            case "music_vocal":
                GrantMusicVocal(resource.resourceId);
                break;
            case "gacha_ceil_item":
                GrantGachaCeilItem(resource.resourceId, resource.quantity);
                break;
            default:
                ApplyLiveRewards([resource]);
                break;
        }
    }

    private static void AddObtainedResource(
        IDictionary<(string? Type, int Id, int Level), UserResource> obtained,
        UserResource resource)
    {
        var key = (resource.resourceType, resource.resourceId, resource.resourceLevel);
        if (obtained.TryGetValue(key, out var current))
        {
            current.quantity += resource.quantity;
            return;
        }

        obtained[key] = new UserResource
        {
            resourceType = resource.resourceType,
            resourceId = resource.resourceId,
            resourceLevel = resource.resourceLevel,
            quantity = resource.quantity
        };
    }

    private void ApplyShopItemResources(int resourceBoxId)
    {
        foreach (var resource in BuildResourcesFromBox("shop_item", resourceBoxId))
        {
            if (resource.quantity <= 0)
                continue;

            switch (resource.resourceType)
            {
                case "music":
                    GrantMusic(resource.resourceId);
                    GrantDefaultMusicVocals(resource.resourceId);
                    break;
                case "music_vocal":
                    GrantMusicVocal(resource.resourceId);
                    break;
                default:
                    ApplyLiveRewards([resource]);
                    break;
            }
        }
    }

    private void GrantMusic(int musicId)
    {
        if (musicId <= 0)
            return;

        Data.userMusics ??= [];
        var musics = Data.userMusics.ToList();
        if (musics.Any(m => m.musicId == musicId))
            return;

        musics.Add(new UserMusic { musicId = musicId });
        Data.userMusics = musics.OrderBy(m => m.musicId).ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userMusics));
    }

    private void GrantDefaultMusicVocals(int musicId)
    {
        foreach (var vocal in LoadMusicVocals())
        {
            if (vocal is not JsonObject obj ||
                obj["musicId"]?.GetValue<int>() != musicId ||
                obj["releaseConditionId"]?.GetValue<int>() != 5)
                continue;

            GrantMusicVocal(musicId, obj["id"]?.GetValue<int>() ?? 0);
        }
    }

    private void GrantMusicVocal(int musicVocalId)
    {
        if (musicVocalId <= 0)
            return;

        foreach (var vocal in LoadMusicVocals())
        {
            if (vocal is JsonObject obj && obj["id"]?.GetValue<int>() == musicVocalId)
            {
                GrantMusicVocal(obj["musicId"]?.GetValue<int>() ?? 0, musicVocalId);
                return;
            }
        }
    }

    private void GrantMusicVocal(int musicId, int musicVocalId)
    {
        if (musicId <= 0 || musicVocalId <= 0)
            return;

        Data.userMusicVocals ??= [];
        if (Data.userMusicVocals.Any(v => v.musicVocalId == musicVocalId))
            return;

        Data.userMusicVocals.Add(new UserMusicVocal
        {
            musicId = musicId,
            musicVocalId = musicVocalId
        });
        Data.userMusicVocals = Data.userMusicVocals
            .OrderBy(v => v.musicVocalId)
            .ToList();
        UpdateRefreshableType(nameof(SuiteUser.userMusicVocals));
    }

    // ===================== Live Mixin =====================

    public UserLive StartUserLive(UserLiveRequest request)
    {
        var userLiveId = Guid.NewGuid().ToString();
        NotSuite.UserLiveSessions[userLiveId] = new UserLiveSessionData
        {
            UserLiveId = userLiveId,
            MusicId = request.musicId,
            MusicDifficultyId = request.musicDifficultyId,
            MusicVocalId = request.musicVocalId,
            DeckId = request.deckId,
            BoostCount = request.boostCount,
            IsAuto = request.isAuto,
            MusicCategoryName = request.musicCategoryName,
            CustomMusicScoreId = request.customMusicScoreId,
            CreatedAt = UserManager.Now
        };

        UpdateRefreshableType(nameof(SuiteUser.userEventBreakTime));
        return new UserLive
        {
            userLiveId = userLiveId,
            updatedResources = GetRefreshData(),
            skills = BuildIngameLotterySkills(request.deckId),
            comboCutins = [],
            isInBreakTime = false
        };
    }

    public UserLiveClearResponse ClearUserLive(string userLiveId, UserLiveClearRequest request)
    {
        NotSuite.UserLiveSessions.Remove(userLiveId, out var session);

        var fullCombo = request.badCount == 0 && request.missCount == 0;
        var fullPerfect = request.greatCount == 0 &&
                          request.goodCount == 0 &&
                          request.badCount == 0 &&
                          request.missCount == 0;

        var scoreRank = session != null ? BuildScoreRank(session.MusicDifficultyId, request.score) : BuildScoreRank(request.score);
        var boost = BuildMasterBoost(session?.BoostCount ?? 0);
        var userLivePoint = BuildUserLivePoint(boost);
        var highScoreFlg = false;
        DeckCardUpdateExpResult[] deckCardExpResults = [];
        UserMusicAchievement[] grantedMusicAchievements = [];
        UserResource[] scoreRankRewards = [];
        UserResource[] musicAchievementRewards = [];
        if (session != null)
        {
            highScoreFlg = UpdateUserMusicResult(session, request, fullCombo, fullPerfect);
            deckCardExpResults = BuildDeckCardExpResults(session.DeckId);
            grantedMusicAchievements = GrantUserMusicAchievements(session, request, scoreRank);
            scoreRankRewards = BuildScoreRankRewards(session.MusicDifficultyId, scoreRank, boost);
            musicAchievementRewards = BuildMusicAchievementRewards(grantedMusicAchievements);
            ApplyLiveRewards(scoreRankRewards);
            ApplyLiveRewards(musicAchievementRewards);
            UpdateLiveMissionProgress(userLivePoint);
            ConsumeBoost(session.BoostCount);
        }

        MergeLiveCharacterArchiveVoiceGroups(request.ingameCutinCharacterArchiveVoiceGroupIds);

        return new UserLiveClearResponse
        {
            updatedResources = GetRefreshData(),
            scoreRank = scoreRank,
            score = request.score,
            perfectCount = request.perfectCount,
            greatCount = request.greatCount,
            goodCount = request.goodCount,
            badCount = request.badCount,
            missCount = request.missCount,
            maxCombo = request.maxCombo,
            highScoreFlg = highScoreFlg,
            fullComboFlg = fullCombo,
            fullPerfectFlg = fullPerfect,
            userExpResult = BuildNoopExpResult(),
            deckCardExpResults = deckCardExpResults,
            unitExpResults = [],
            userDeck = GetUserDeck(session?.DeckId),
            userMusicAchievements = grantedMusicAchievements,
            scoreRankRewards = scoreRankRewards,
            playerRankRewards = [],
            limitedTermScoreRankRewards = [],
            musicAchievementRewards = musicAchievementRewards,
            boost = boost,
            beforeEventPoint = 0,
            afterEventPoint = 0,
            beforeEventItemQuantity = 0,
            afterEventItemQuantity = 0,
            beforeWorldBloomChapterPoint = null,
            afterWorldBloomChapterPoint = null,
            worldBloomChapterNo = null,
            isPreliminaryTournament = false,
            bondsUpdateExpResults = [],
            userEventDeviceTransferRestrict = new UserRestrictInfo(),
            userLivePoint = userLivePoint,
            isEventMaintenance = false,
            isInBreakTime = false
        };
    }

    public void ReceiveLiveCharacterArchiveVoiceResult(int liveResultCharacterArchiveVoiceGroupId)
    {
        if (liveResultCharacterArchiveVoiceGroupId <= 0)
            return;

        MergeLiveCharacterArchiveVoiceGroups([liveResultCharacterArchiveVoiceGroupId]);
    }

    private bool UpdateUserMusicResult(
        UserLiveSessionData session,
        UserLiveClearRequest request,
        bool fullCombo,
        bool fullPerfect)
    {
        Data.userMusicResults ??= [];
        var results = Data.userMusicResults.ToList();
        var difficultyType = ResolveMusicDifficultyType(session.MusicDifficultyId);
        var result = results.FirstOrDefault(r =>
            r.musicId == session.MusicId &&
            string.Equals(r.musicDifficultyType, difficultyType, StringComparison.Ordinal));

        var previousHighScore = result?.highScore ?? 0;
        var highScoreFlg = request.score > previousHighScore;

        if (result == null)
        {
            result = new UserMusicResult
            {
                musicId = session.MusicId,
                musicDifficultyType = difficultyType,
                playType = "solo",
                playResult = "clear"
            };
            results.Add(result);
        }

        result.playType = "solo";
        result.playResult = BuildPlayResult(fullCombo, fullPerfect, request.life);
        result.highScore = Math.Max(result.highScore, request.score);
        result.fullComboFlg = result.fullComboFlg || fullCombo;
        result.fullPerfectFlg = result.fullPerfectFlg || fullPerfect;

        Data.userMusicResults = results.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userMusicResults));
        return highScoreFlg;
    }

    private UserMusicAchievement[] GrantUserMusicAchievements(
        UserLiveSessionData session,
        UserLiveClearRequest request,
        string scoreRank)
    {
        var achievementIds = ResolveMusicAchievementIds(session.MusicDifficultyId, request.maxCombo, scoreRank);

        Data.userMusicAchievements ??= [];
        var achievements = Data.userMusicAchievements.ToList();
        var granted = new List<UserMusicAchievement>();

        foreach (var achievementId in achievementIds.Distinct())
        {
            if (achievements.Any(a => a.musicId == session.MusicId && a.musicAchievementId == achievementId))
                continue;

            var achievement = new UserMusicAchievement
            {
                musicId = session.MusicId,
                musicAchievementId = achievementId
            };
            achievements.Add(achievement);
            granted.Add(achievement);
        }

        if (granted.Count > 0)
        {
            Data.userMusicAchievements = achievements.ToArray();
            UpdateRefreshableType(nameof(SuiteUser.userMusicAchievements));
        }

        return granted.ToArray();
    }

    private static UserResource[] BuildMusicAchievementRewards(UserMusicAchievement[] achievements)
    {
        var rewards = new List<UserResource>();
        foreach (var achievement in achievements)
        {
            var resourceBoxId = GetMusicAchievementResourceBoxId(achievement.musicAchievementId);
            rewards.AddRange(BuildResourcesFromBox("music_achievement", resourceBoxId));
        }

        return rewards.ToArray();
    }

    private static UserResource[] BuildScoreRankRewards(int musicDifficultyId, string scoreRank, MasterBoost boost)
    {
        var playLevel = ResolveMusicPlayLevel(musicDifficultyId);
        var resourceBoxIds = GetScoreRankRewardResourceBoxIds(playLevel, scoreRank);
        if (resourceBoxIds.Length == 0)
            return [];

        var rewardRate = Math.Max(1, boost.rewardRate);
        return resourceBoxIds
            .SelectMany(resourceBoxId => BuildResourcesFromBox("score_rank_reward_detail", resourceBoxId))
            .Select(reward => new UserResource
            {
                resourceType = reward.resourceType,
                resourceId = reward.resourceId,
                resourceLevel = reward.resourceLevel,
                quantity = reward.quantity * rewardRate
            })
            .Where(reward => reward.quantity > 0)
            .ToArray();
    }

    private static int[] GetScoreRankRewardResourceBoxIds(int playLevel, string scoreRank) =>
        (playLevel, scoreRank) switch
        {
            // 6.5.5 capture 0054: musicDifficultyId 406, playLevel 6, rank_c.
            (6, "rank_c") => [62, 12, 19, 15, 47, 56],

            // 6.5.5 capture 0061: musicDifficultyId 313, playLevel 17, rank_d.
            (17, "rank_d") => [61, 20],

            _ => []
        };

    private void ApplyLiveRewards(IEnumerable<UserResource> rewards)
    {
        foreach (var reward in rewards)
        {
            if (reward.quantity <= 0)
                continue;

            switch (reward.resourceType)
            {
                case "jewel":
                    Data.userChargedCurrency ??= new ChargedCurrency { paidUnitPrices = [] };
                    Data.userChargedCurrency.free += reward.quantity;
                    UpdateRefreshableType(nameof(SuiteUser.userChargedCurrency));
                    break;
                case "coin":
                    if (Data.userGamedata != null)
                    {
                        Data.userGamedata.coin += reward.quantity;
                        UpdateRefreshableType(nameof(SuiteUser.userGamedata));
                    }
                    break;
                case "material":
                    AddMaterial(reward.resourceId, reward.quantity);
                    break;
                case "practice_ticket":
                    AddPracticeTicket(reward.resourceId, reward.quantity);
                    break;
            }
        }
    }

    private void AddMaterial(int materialId, int quantity)
    {
        if (materialId <= 0 || quantity <= 0)
            return;

        Data.userMaterials ??= [];
        var materials = Data.userMaterials.ToList();
        var material = materials.FirstOrDefault(m => m.materialId == materialId);
        if (material == null)
        {
            material = new UserMaterial { materialId = materialId };
            materials.Add(material);
        }

        material.quantity += quantity;
        Data.userMaterials = materials.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userMaterials));
    }

    private void AddPracticeTicket(int practiceTicketId, int quantity)
    {
        if (practiceTicketId <= 0 || quantity <= 0)
            return;

        Data.userPracticeTickets ??= [];
        var tickets = Data.userPracticeTickets.ToList();
        var ticket = tickets.FirstOrDefault(t => t.practiceTicketId == practiceTicketId);
        if (ticket == null)
        {
            ticket = new UserPracticeTicket
            {
                userId = GetUserId(),
                practiceTicketId = practiceTicketId
            };
            tickets.Add(ticket);
        }

        ticket.quantity += quantity;
        Data.userPracticeTickets = tickets.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userPracticeTickets));
    }

    private void ConsumeBoost(int boostCount)
    {
        if (Data.userBoost == null || boostCount <= 0)
            return;

        Data.userBoost.current = Math.Max(0, Data.userBoost.current - boostCount);
        Data.userBoost.recoveryAt = (ulong)UserManager.Now;
        UpdateRefreshableType(nameof(SuiteUser.userBoost));
    }

    private void MergeLiveCharacterArchiveVoiceGroups(IEnumerable<int>? groupIds)
    {
        if (groupIds == null)
            return;

        Data.userLiveCharacterArchiveVoice ??= new UserLiveCharacterArchiveVoice
        {
            characterArchiveVoiceGroupIds = []
        };
        Data.userLiveCharacterArchiveVoice.characterArchiveVoiceGroupIds ??= [];

        var changed = false;
        var current = Data.userLiveCharacterArchiveVoice.characterArchiveVoiceGroupIds;
        foreach (var groupId in groupIds.Where(id => id > 0))
        {
            if (current.Contains(groupId))
                continue;

            current.Add(groupId);
            changed = true;
        }

        if (changed)
            UpdateRefreshableType(nameof(SuiteUser.userLiveCharacterArchiveVoice));
    }

    private UserDeck? GetUserDeck(int? deckId)
    {
        if (deckId == null || Data.userDecks == null)
            return null;

        return Data.userDecks.FirstOrDefault(d => d.deckId == deckId.Value);
    }

    private IngameLotterySkill[] BuildIngameLotterySkills(int deckId)
    {
        var deck = GetUserDeck(deckId);
        if (deck == null)
            return [];

        var cardIds = new[] { deck.leader, deck.member1, deck.member2, deck.member3, deck.member4, deck.member5 };
        return cardIds
            .Where(cardId => cardId > 0)
            .Select((cardId, index) => new IngameLotterySkill
            {
                seq = index + 1,
                cardId = cardId,
                relationCardId = null,
                ingameCutinCharacterId = null
            })
            .ToArray();
    }

    private DeckCardUpdateExpResult[] BuildDeckCardExpResults(int deckId)
    {
        var deck = GetUserDeck(deckId);
        if (deck == null || Data.userCards == null)
            return [];

        var cardIds = new[] { deck.member1, deck.member2, deck.member3, deck.member4, deck.member5 };
        return cardIds
            .Select((cardId, index) => new { cardId, index })
            .Where(slot => slot.cardId > 0 && Data.userCards.Any(card => card.cardId == slot.cardId))
            .Select(slot =>
            {
                var card = Data.userCards!.First(card => card.cardId == slot.cardId);
                return new DeckCardUpdateExpResult
                {
                    index = slot.index + 1,
                    expResult = new UpdateExpResult
                    {
                        beforeTotalExp = card.totalExp,
                        afterTotalExp = card.totalExp,
                        beforeExp = card.exp,
                        afterExp = card.exp,
                        beforeLevel = card.level,
                        afterLevel = card.level
                    }
                };
            })
            .ToArray();
    }

    private UpdateExpResult BuildNoopExpResult()
    {
        var gd = Data.userGamedata;
        return new UpdateExpResult
        {
            beforeTotalExp = gd?.totalExp ?? 0,
            afterTotalExp = gd?.totalExp ?? 0,
            beforeExp = gd?.exp ?? 0,
            afterExp = gd?.exp ?? 0,
            beforeLevel = gd?.rank ?? 0,
            afterLevel = gd?.rank ?? 0
        };
    }

    private static MasterBoost BuildMasterBoost(int boostCount)
    {
        foreach (var boost in LoadBoosts())
        {
            if (boost is JsonObject obj && obj["costBoost"]?.GetValue<int>() == boostCount)
            {
                return new MasterBoost
                {
                    id = obj["id"]?.GetValue<int>() ?? boostCount + 1,
                    costBoost = boostCount,
                    isEventOnly = obj["isEventOnly"]?.GetValue<bool>() ?? false,
                    expRate = obj["expRate"]?.GetValue<int>() ?? 1,
                    rewardRate = obj["rewardRate"]?.GetValue<int>() ?? 1,
                    livePointRate = obj["livePointRate"]?.GetValue<int>() ?? 1,
                    eventPointRate = obj["eventPointRate"]?.GetValue<int>() ?? 1,
                    bondsExpRate = obj["bondsExpRate"]?.GetValue<int>() ?? 1
                };
            }
        }

        var rate = boostCount <= 0 ? 1 : boostCount * 5;
        return new MasterBoost
        {
            id = boostCount + 1,
            costBoost = boostCount,
            isEventOnly = false,
            expRate = rate,
            rewardRate = rate,
            livePointRate = rate,
            eventPointRate = rate,
            bondsExpRate = rate
        };
    }

    private static UserLivePoint BuildUserLivePoint(MasterBoost boost) =>
        new()
        {
            addNormalProgress = boost.livePointRate,
            addDailyBonusProgress = 0,
            livePointBonusRemaining = boost.costBoost,
            liveMissionPeriodId = GetCurrentLiveMissionPeriodId()
        };

    private void UpdateLiveMissionProgress(UserLivePoint livePoint)
    {
        if (livePoint.liveMissionPeriodId <= 0 || livePoint.addNormalProgress <= 0)
            return;

        Data.userLiveMissions ??= [];
        var missions = Data.userLiveMissions.ToList();
        var mission = missions.FirstOrDefault(m =>
            m.liveMissionPeriodId == livePoint.liveMissionPeriodId &&
            string.Equals(m.liveMissionStatus, "free", StringComparison.Ordinal));

        if (mission == null)
        {
            mission = new UserLiveMission
            {
                userId = GetUserId(),
                liveMissionPeriodId = livePoint.liveMissionPeriodId,
                liveMissionStatus = "free",
                achievedMissionIds = []
            };
            missions.Add(mission);
        }

        mission.progress += livePoint.addNormalProgress;
        mission.achievedMissionIds ??= [];
        Data.userLiveMissions = missions.ToArray();
        UpdateRefreshableType(nameof(SuiteUser.userLiveMissions));
    }

    private static string BuildScoreRank(int musicDifficultyId, int score)
    {
        var playLevel = ResolveMusicPlayLevel(musicDifficultyId);
        if (playLevel > 0)
        {
            foreach (var scoreThreshold in LoadPlayLevelScores())
            {
                if (scoreThreshold is not JsonObject obj ||
                    !string.Equals(obj["liveType"]?.GetValue<string>(), "solo", StringComparison.Ordinal) ||
                    obj["playLevel"]?.GetValue<int>() != playLevel)
                    continue;

                if (score >= (obj["s"]?.GetValue<int>() ?? int.MaxValue))
                    return "rank_s";
                if (score >= (obj["a"]?.GetValue<int>() ?? int.MaxValue))
                    return "rank_a";
                if (score >= (obj["b"]?.GetValue<int>() ?? int.MaxValue))
                    return "rank_b";
                if (score >= (obj["c"]?.GetValue<int>() ?? int.MaxValue))
                    return "rank_c";
                return "rank_d";
            }
        }

        return BuildScoreRank(score);
    }

    private static string BuildScoreRank(int score) =>
        score switch
        {
            >= 600_000 => "rank_s",
            >= 300_000 => "rank_a",
            >= 150_000 => "rank_b",
            >= 50_000 => "rank_c",
            _ => "rank_d"
        };

    private static string BuildPlayResult(bool fullCombo, bool fullPerfect, int life)
    {
        if (life <= 0)
            return "not_clear";
        if (fullPerfect)
            return "full_perfect";
        if (fullCombo)
            return "full_combo";
        return "clear";
    }

    private static int[] ResolveMusicAchievementIds(int musicDifficultyId, int maxCombo, string scoreRank)
    {
        var difficultyType = ResolveMusicDifficultyType(musicDifficultyId);
        var totalNoteCount = ResolveMusicTotalNoteCount(musicDifficultyId);
        var achievementIds = new List<int>();

        foreach (var achievement in LoadMusicAchievements())
        {
            if (achievement is not JsonObject obj)
                continue;

            var type = obj["musicAchievementType"]?.GetValue<string>();
            var value = obj["musicAchievementTypeValue"]?.GetValue<string>();
            if (type == "score_rank" && IsScoreRankReached(scoreRank, value))
            {
                achievementIds.Add(obj["id"]!.GetValue<int>());
                continue;
            }

            if (type != "combo" ||
                !string.Equals(obj["musicDifficultyType"]?.GetValue<string>(), difficultyType, StringComparison.Ordinal) ||
                totalNoteCount <= 0 ||
                value == null ||
                !double.TryParse(value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var ratio))
                continue;

            if (maxCombo >= (int)Math.Ceiling(totalNoteCount * ratio))
                achievementIds.Add(obj["id"]!.GetValue<int>());
        }

        return achievementIds.OrderBy(id => id).ToArray();
    }

    private static bool IsScoreRankReached(string scoreRank, string? achievementRank)
    {
        var actual = ScoreRankOrder(scoreRank);
        var required = ScoreRankOrder(achievementRank);
        return required > 0 && actual >= required;
    }

    private static int ScoreRankOrder(string? rank)
    {
        var normalized = rank?.ToUpperInvariant();
        return normalized switch
        {
            "RANK_SS" or "RANK_S" or "RANK_S_PLUS" => 4,
            "RANK_A" => 3,
            "RANK_B" => 2,
            "RANK_C" => 1,
            _ => 0
        };
    }

    private static int GetMusicAchievementResourceBoxId(int musicAchievementId)
    {
        foreach (var achievement in LoadMusicAchievements())
        {
            if (achievement is JsonObject obj && obj["id"]?.GetValue<int>() == musicAchievementId)
                return obj["resourceBoxId"]?.GetValue<int>() ?? 0;
        }

        return 0;
    }

    private static UserResource[] BuildResourcesFromBox(string purpose, int resourceBoxId)
    {
        if (resourceBoxId <= 0)
            return [];

        foreach (var box in LoadResourceBoxes())
        {
            if (box is not JsonObject obj ||
                !string.Equals(obj["resourceBoxPurpose"]?.GetValue<string>(), purpose, StringComparison.Ordinal) ||
                obj["id"]?.GetValue<int>() != resourceBoxId ||
                obj["details"] is not JsonArray details)
                continue;

            return details
                .OfType<JsonObject>()
                .Select(detail => new UserResource
                {
                    resourceType = detail["resourceType"]?.GetValue<string>(),
                    resourceId = detail["resourceId"]?.GetValue<int>() ?? 0,
                    resourceLevel = detail["resourceLevel"]?.GetValue<int>() ?? 0,
                    quantity = detail["resourceQuantity"]?.GetValue<int>() ?? 0
                })
                .ToArray();
        }

        return [];
    }

    private static int GetCurrentLiveMissionPeriodId()
    {
        var current = 0;
        foreach (var pass in LoadLiveMissionPasses())
        {
            if (pass is JsonObject obj)
                current = Math.Max(current, obj["liveMissionPeriodId"]?.GetValue<int>() ?? 0);
        }

        return current;
    }

    private static string ResolveMusicDifficultyType(int musicDifficultyId)
    {
        var difficulty = FindMusicDifficulty(musicDifficultyId);
        if (difficulty != null)
            return difficulty["musicDifficulty"]?.GetValue<string>() ?? musicDifficultyId.ToString();

        return musicDifficultyId.ToString();
    }

    private static int ResolveMusicTotalNoteCount(int musicDifficultyId)
    {
        var difficulty = FindMusicDifficulty(musicDifficultyId);
        return difficulty?["totalNoteCount"]?.GetValue<int>() ?? 0;
    }

    private static int ResolveMusicPlayLevel(int musicDifficultyId)
    {
        var difficulty = FindMusicDifficulty(musicDifficultyId);
        return difficulty?["playLevel"]?.GetValue<int>() ?? 0;
    }

    private static JsonObject? FindMusicDifficulty(int musicDifficultyId)
    {
        foreach (var difficulty in LoadMusicDifficulties())
        {
            if (difficulty is JsonObject obj && obj["id"]?.GetValue<int>() == musicDifficultyId)
                return obj;
        }

        return null;
    }

    private static readonly Random Rng = new();

    private static string GenerateRandomString(int length)
    {
        const string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        var result = new char[length];
        for (int i = 0; i < length; i++)
            result[i] = chars[Rng.Next(chars.Length)];
        return new string(result);
    }

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
                PresentHistories = [.. NotSuite.PresentHistories],
                UserLiveSessions = NotSuite.UserLiveSessions.ToDictionary(
                    kv => kv.Key,
                    kv => new UserLiveSessionData
                    {
                        UserLiveId = kv.Value.UserLiveId,
                        MusicId = kv.Value.MusicId,
                        MusicDifficultyId = kv.Value.MusicDifficultyId,
                        MusicVocalId = kv.Value.MusicVocalId,
                        DeckId = kv.Value.DeckId,
                        BoostCount = kv.Value.BoostCount,
                        IsAuto = kv.Value.IsAuto,
                        MusicCategoryName = kv.Value.MusicCategoryName,
                        CustomMusicScoreId = kv.Value.CustomMusicScoreId,
                        CreatedAt = kv.Value.CreatedAt
                    })
            }
        };
        return user;
    }
}
