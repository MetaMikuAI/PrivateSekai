using MessagePack;

namespace PrivateSekai.Models;

[MessagePackObject]
public class ModuleMaintenanceResponse
{
    [Key("moduleMaintenanceType")] public string? moduleMaintenanceType;
    [Key("isOngoing")] public bool isOngoing;
}

[MessagePackObject]
public class UserGachaResponse
{
    [Key("consumedCosts")] public UserResource[]? consumedCosts;
    [Key("obtainPrizes")] public UserGachaSpinObtainPrize[]? obtainPrizes;
    [Key("obtainGachaCeilItems")] public UserResource[]? obtainGachaCeilItems;
    [Key("obtainGachaBonusItems")] public UserResource[]? obtainGachaBonusItems;
    [Key("obtainGachaExtras")] public UserResource[]? obtainGachaExtras;
    [Key("obtainGachaFreebies")] public UserGachaFreebie[]? obtainGachaFreebies;
    [Key("userGacha")] public UserGacha? userGacha;
    [Key("updatedResources")] public SuiteUser? updatedResources;
    [Key("obtainCharacterAllBonuses")] public GachaCharacterAllBonusObtain[]? obtainCharacterAllBonuses;
    [Key("obtainCharacterRepeatedBonuses")] public GachaCharacterRepeatedBonusObtain[]? obtainCharacterRepeatedBonuses;
}

[MessagePackObject]
public class UserGachaSpinObtainPrize
{
    [Key("card")] public UserResource? card;
    [Key("newFlg")] public bool newFlg;
    [Key("gachaLotteryType")] public string? gachaLotteryType;
    [Key("costume3d")] public UserResource[]? costume3d;
    [Key("cardExtra")] public UserResource[]? cardExtra;
}

[MessagePackObject]
public class UserGachaFreebie
{
    [Key("rarity")] public int rarity;
    [Key("obtainedResources")] public UserResource[]? obtainedResources;
}

[MessagePackObject]
public class GachaCharacterAllBonusObtain
{
    [Key("obtainedResources")] public List<UserResource>? obtainedResources;
}

[MessagePackObject]
public class GachaCharacterRepeatedBonusObtain
{
    [Key("cardId")] public int cardId;
    [Key("obtainedResources")] public List<UserResource>? obtainedResources;
}
