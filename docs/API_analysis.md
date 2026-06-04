# Private Sekai 分析

## 注册、登录与登出

### `POST /api/user`

#### 作用

请求注册新用户

#### Request：

```json
{
    "platform": "Android",
    "deviceModel": "Samsung SM-S9210",
    "operatingSystem": "Android OS 12 / API-32 (V417IR/1974)"
}
```

#### Response：

```json
{
    "userRegistration": {
        "userId": 600000000000904800,
        "signature": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0.5XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX4",
        "platform": "Android",
        "deviceModel": "Samsung SM-S9210",
        "operatingSystem": "Android OS 12 / API-32 (V417IR/1974)",
        "registeredAt": 1700000000057
    },
    "credential": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0.ZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXk",
    "updatedResources": {
        // 略，只是常规的 updateResources 数据
    }
}
```

signature 的 payload 示例（目前感觉似乎是没什么用）：

```json
{
  "userId": 600000000000904800
}
```

credential 的 payload 示例（用于后续登录验证）：

```json
{
  "credential": "bXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXb",
  "userId": "600000000000904771"
}
```

#### IMPORTANT

二者的 userId 并不一致(而且类型也不一样)，目前观察似乎在继承引继码后有细微变化，可能用于控制引继频率（？）

### `PUT /api/user/<userId>/auth?refreshUpdatedResources=False`

#### 作用

鉴权（验证 credential） 并返回 X-SESSION-TOKEN

#### Request

```json

{
    "credential": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0.ZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXk",
    "deviceId": null,
    "authTriggerType": "normal"
}
```

注意：credential 应与上一条完全一样

#### Response

```json
{
    "sessionToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXQ.AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXA",
    "appVersion": "5.6.0",
    "multiPlayVersion": "miku",
    "dataVersion": "5.6.0.50",
    "assetVersion": "5.6.0.50",
    "removeAssetVersion": "1.13.0.30",
    "assetHash": "2f4808f3-92c7-3d64-4773-30865d2444a5",
    "appVersionStatus": "available",
    "isStreamingVirtualLiveForceOpenUser": false,
    "deviceId": "527e7a18-52cd-4faa-bc32-19f212455714",
    "updatedResources": {},
    "suiteMasterSplitPath": [
        "suitemasterfile/5.6.0.50/00_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/01_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/02_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/03_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/04_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/05_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d",
        "suitemasterfile/5.6.0.50/06_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d"
    ],
    "obtainedBondsRewardIds": []
}
```

其中 `sessionsToken` 解码为

```json
{
  "sessionToken": "e0000000-0000-0000-0000-00000000000f",
  "userId": "600000000000000001"
}
```

`suiteMasterSplitPath` 应该是资源元数据，大小约 100M ~ 200M

### `GET /api/system`

#### 作用

获取当前系统状态信息

#### 鉴权

客户端会携带 `X-Session-Token`，**即使服务端一般似乎不会鉴权和分发新 token**

#### 示例返回

```json
{
    "serverDate": 1700000000001,
    "timezone": "Asia/Tokyo",
    "profile": "production",
    "maintenanceStatus": "maintenance_out",
    "appVersions": [
        {
            "systemProfile": "production",
            "appVersion": "1.0",
            "multiPlayVersion": "0.1",
            "assetVersion": "1.0.3",
            "appVersionStatus": "not_available"
        },
        // 中间若干内容省略，一般只有版本号如 5.6.X 前两项相同为 available
        {
            "systemProfile": "production",
            "appVersion": "5.6.0",
            "multiPlayVersion": "miku",
            "assetVersion": "5.6.0.50",
            "appVersionStatus": "available"
        },
        {
            "systemProfile": "production",
            "appVersion": "5.6.1",
            "multiPlayVersion": "miku",
            "assetVersion": "5.6.0.50",
            "appVersionStatus": "available"
        }
    ]
}
```

### `GET /api/suite/user/<userId>`

#### 作用

获取完整用户数据 (应该是完整的吧)

#### 鉴权

客户端携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

#### Response

```json
{
    "now": 1700000000007,
    "refreshableTypes": [],
    "userRegistration": {
        "userId": 600000000000000000,
        "signature": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0.5XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX4",
        "platform": "Android",
        "deviceModel": "Samsung SM-S9210",
        "operatingSystem": "Android OS 12 / API-32 (V417IR/1974)",
        "registeredAt": 1700000000007
    },
    "userGamedata": {
        "userId": 600000000000000000,
        "name": "セカイの住人",
        "deck": 1,
        "rank": 1,
        "exp": 0,
        "totalExp": 0,
        "coin": 0,
        "virtualCoin": 0
    },
    "userChargedCurrency": {
        "paid": 0,
        "free": 0,
        "paidUnitPrices": []
    },
    "userBoost": {
        "current": 25,
        "recoveryAt": 1700000000007
    }
    // 其余略
}
```

### `PATCH /api/user/<userId>/tutorial`

#### 作用

新手引导状态更新。Miku 引导玩家进行一系列教程，先后包括

0. `start` （此为新玩家的初始状态）
1. `opening_1` （此为玩家进入新手引导的第一阶段）
2. `gameplay` （此为玩家进入游玩教学，即 《Tell Your World》的 short live）
3. `opening_2` （此为另一端引导，**在此 Miku 会请求玩家修改昵称**）
4. `unit_select` （玩家进入组合选择阶段，包括初始剧情的阅读）
5. `light_sound_opening`, `idol_opening`, `street_opening`, `theme_park_opening`, `school_refusal_opening` （玩家确定选择某一组合并进入初始剧情）
6. `summary` （玩家新手引导基本结束，进入最后的简要 UI 介绍）
7. `end` （玩家新手引导完全结束，此后不再进行新手引导）


#### 鉴权

客户端携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

#### Request

```json
{
    "tutorialStatus": "theme_park_opening"
}
```

#### Response

由于涉及到 `userTutorial` 字段的更新，每次响应会在基础的用户 `refresh` 数据中添加 `userTutorial` 字段

而且如果用户是跳到了 `summary`，则应根据先前所选择的组合给予对应的打牌，并添加到 Response 中

```json
{
    "updatedResources": {
        "now": 1700000000009,
        "refreshableTypes": [],
        "userTutorial": {
            "tutorialStatus": "summary"
        },
        "userCards": [
            {
                "userId": 600000000000000000,
                "cardId": 49,
                "level": 1,
                "exp": 0,
                "totalExp": 0,
                "skillLevel": 1,
                "skillExp": 0,
                "totalSkillExp": 0,
                "masterRank": 0,
                "specialTrainingStatus": "not_doing",
                "defaultImage": "original",
                "duplicateCount": 0,
                "createdAt": 1700000000009,
                "episodes": [
                    {
                        "cardEpisodeId": 97,
                        "scenarioStatus": "unreleased",
                        "scenarioStatusReasons": [],
                        "isNotSkipped": false
                    },
                    {
                        "cardEpisodeId": 98,
                        "scenarioStatus": "can_not_read",
                        "scenarioStatusReasons": [
                            "unread_before_scenario",
                            "not_enough_release_condition"
                        ],
                        "isNotSkipped": false
                    }
                ]
            },
            // 其余卡牌略
        ],
        "userDecks": [
            {
                "userId": 600000000000000000,
                "deckId": 1,
                "name": "ユニット01",
                "leader": 85,
                "subLeader": 49,
                "member1": 85,
                "member2": 49,
                "member3": 53,
                "member4": 57,
                "member5": 61
            }
        ],
        "userUnitEpisodeStatuses": [
            {
                "storyType": "unit_story",
                "episodeId": 4,
                "status": "can_not_read",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 8,
                "status": "can_not_read",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 12,
                "status": "can_not_read",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 16,
                "status": "can_not_read",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 20,
                "status": "can_not_read",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 20000,
                "status": "already_read",
                "isNotSkipped": true
            },
            {
                "storyType": "unit_story",
                "episodeId": 20001,
                "status": "unreleased",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 30000,
                "status": "unreleased",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 40000,
                "status": "unreleased",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 50000,
                "status": "unreleased",
                "isNotSkipped": false
            },
            {
                "storyType": "unit_story",
                "episodeId": 60000,
                "status": "unreleased",
                "isNotSkipped": false
            }
        ]
        // 其余更新字段总是存在，略
    }
}
```

### `PATCH /api/user/<userId>`

#### 作用

修改玩家信息，目前只在**新手引导**中玩家修改昵称时使用到

#### 鉴权

客户端携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

#### Request

```json
{
    "userGamedata": {
        "name": "セカイの住人"
    }
}
```

### `GET /api/suite/user/<userId>?isForceAllReload=false&name=user`

#### 作用

拉取当前用户的基本信息，将其中 userId, 昵称, 等级 显示给用户以等待用户确认登出

#### 鉴权

客户端会携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

而且此时客户端一般应该尚未获取此次会话的 `X-Session-Token`，因此一般在此之前会先请求一次 `PUT /api/user/<userId>/auth?refreshUpdatedResources=False`，该请求与我们先前讨论的 `PUT /api/user/<userId>/auth` 别无二样

#### Request

**注意！此请求非加密数据**
**注意！此请求非加密数据**

```
isForceAllReload: 'false'
name: user
```

#### Response

返回的是常规的 refresh 数据

```json
{
    "now": 1700000000008,
    "refreshableTypes": [],
    "userRegistration": {
        "userId": 600000000000000000,
        "signature": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0.5XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX4",
        "platform": "Android",
        "deviceModel": "Samsung SM-S9210",
        "operatingSystem": "Android OS 12 / API-32 (V417IR/1974)",
        "registeredAt": 1700000000007
    },
    "userGamedata": {
        "userId": 600000000000000000,
        "name": "セカイの住人",
        "deck": 1,
        "rank": 1,
        "exp": 0,
        "totalExp": 0,
        "coin": 0,
        "virtualCoin": 0,
        "lastLoginAt": 1700000000003
    },
    "userPresents": [
      // 略
    ]
    // 略
}
```

### `GET /api/user/<userId>/deactivate`

### 作用

注销（登出），其实最主要的应该还是清除本地 credential

下次登录时检测不到 credential 会先请求注册

#### 鉴权

客户端会携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

#### Request

一串 16 字节的未知含义 hex 序列，例如


```
ff a3 45 21  56 f3 75 35  68 bf 3f 2e  2a b2 ee db
```

（该数据亦有脱敏）

该序列总是出现，命名为 EmptyRequestCiphertext；它是 AES-CBC/PKCS7 加密空请求体 `byte[0]` 的固定密文。


#### Response

200 No content

### `GET /api/suitemasterfile/<assetVersion>/<filename>`

例如 `GET /api/suitemasterfile/5.6.0.50/00_b7e16d3efd7f6512fb5774b2700eda46c5ea15a27e0931b0dcd3d4d682587b5d`

#### 作用

请求资源元数据，`filename` 来自 `PUT /api/user/<userId>/auth?refreshUpdatedResources=False`，客户端会逐一请求

#### 鉴权

客户端会携带 `X-Session-Token`，**即使服务端一般似乎不会鉴权和分发新 token**

**但客户端有资源校验**，下载的资源包只得缓存重放，不得修改。校验方法尚未知

### `GET /api/user/<userId>/restrict-info`

#### 作用

没什么用（也不能这么说，看字段名就好了）

#### 鉴权

客户端会携带 `X-Session-Token`，服务端分发新 `X-Session-Token`

#### Response

```json
{
    "isRestrictDeviceTransfer": false
}
```

## 引继

### `PUT /api/user/<userId>/inherit`

#### 作用

设定引继码

#### Request

```json
{
    "password": "12345678"
}
```

#### Response

```json
{
    "userInherit": {
        "inheritId": "GXXXXXXXXXXXXXXz"
    },
    "updatedResources": {
        "now": 1700000000005,
        "refreshableTypes": [],
        "userPresents": [
            {
                "presentId": "01234567-89ab-cdef-fedc-ba9876543210",
                "seq": 9200000000000000000,
                "resourceType": "music",
                "resourceId": 331,
                "resourceQuantity": 1,
                "reason": "楽曲「39」のプレゼントです。",
                "grantedAt": 1700000000000
            }
            // 略
        ],
        "userInherit": {
            "inheritId": "GXXXXXXXXXXXXXXz"
        },
        // 略
    }
}
```

*不是我就设定一个引继码，你为什么要加上 `updatedResources` ？*

### `POST /api/inherit/user/inheritId?isExecuteInherit=False`

#### 作用

获取基本信息提示玩家等待引继确认

#### 鉴权

header 中 `X-Inherit-Id-Verify-Token` 字段以 jwt 形式储存引继信息，如

`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX9.lXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXY`

`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXQ.tXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX0`

`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX9.tXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX4`

解码信息：

```json
{
  "inheritId": "GXXXXXXXXXXXXXXz",
  "password": "12345678"
}
```


#### Response

```json
{
    "afterUserGamedata": {
        "userId": 600000000000000000,
        "name": "Miku",
        "deck": 1,
        "rank": 1
    },
    "userEventDeviceTransferRestrict": {
        "isRestrictDeviceTransfer": false
    }
}
```

错误的会返回
```json
{
    "httpStatus": 403,
    "errorCode": "session_error",
    "errorMessage": ""
}
```

### `POST /api/inherit/user/inheritId?isExecuteInherit=True`

#### 作用

确认引继，获取基本信息

response 比 `isExecuteInherit=False` 多一个 `credential`，其余不变，故略


## 故事

### `GET /api/user/<int:user_id>/story/recommend`

#### 作用

从 home 进入 story 页面时，获取推荐故事列表

#### Response

example:

```json
{
    "userStoryRecommends": [
        {
            "storyType": "unit_story",
            "storyId": 10,
            "reason": "continuously",
            "category": "continuously",
            "seq": 1
        },
        {
            "storyType": "unit_story",
            "storyId": 9,
            "reason": "main_story",
            "category": "random",
            "seq": 2
        },
        {
            "storyType": "event_story",
            "storyId": 27,
            "reason": "recommend",
            "category": "random",
            "seq": 3
        }
    ]
}
```


### `POST /api/user/<int:user_id>/story/archive_event_story/episode/<int:episode_id>/log`

#### 作用

阅读完毕后，上传阅读数据

#### Request

```json
{
    "noSkip": false,
    "useSkip": true,
    "autoFinish": false,
    "useAuto": false,
    "fastForward": false,
    "voice": false,
    "numPages": 0,
    "continuousPlayStart": false,
    "playMusicVideo": false,
    "musicVocalId": 0,
    "musicCategoryName": "mv",
    "musicVideoNoSkip": false,
    "userStoryMusicPlays": []
}
```

```json
{
    "noSkip": false,
    "useSkip": true,
    "autoFinish": false,
    "useAuto": false,
    "fastForward": false,
    "voice": true,
    "numPages": 0,
    "continuousPlayStart": false,
    "playMusicVideo": false,
    "musicVocalId": 0,
    "musicCategoryName": "mv",
    "musicVideoNoSkip": false,
    "userStoryMusicPlays": []
}
```


#### Response

```python
response_data: dict[str, Any] = {
    'updatedResources': user.get_refresh_data(delete_rtypes={'userBeginnerMissionBehavior'}),
    'userObtainResourceResults': []
}
```


### `GET /api/user/<int:user_id>/present/history`

#### 作用

获取礼物领取历史

#### Response

```json
{
    "userPresentHistories": [
        {
            "presentId": "6f8aba08-d2ff-4bd0-b792-28839704c77c",
            "seq": 9223370276153127000,
            "resourceType": "jewel",
            "resourceQuantity": 300,
            "expiredAt": 1763293649286,
            "reason": "初心者応援ログインキャンペーン1日目の報酬です。",
            "receivedAt": 1760701649286
        },
        {
            "presentId": "bccfe9aa-13f2-4f8f-a09d-d1c9a240a59e",
            "seq": 9223370276152812000,
            "resourceType": "gacha_ticket",
            "resourceId": 21,
            "resourceQuantity": 1,
            "expiredAt": 1763293964524,
            "reason": "初心者応援ログインキャンペーン1日目の報酬です。",
            "receivedAt": 1760701964524
        }
    ]
}
```

这个不在 suite 表内，需要新开一个

### `POST /api/user/<int:user_id>/present`

#### 作用

领礼物

#### Resquest

```json
{
    "presentIds": [
        "bccfe9aa-13f2-4f8f-a09d-d1c9a240a59e"
    ]
}
```

```json
{
    "presentIds": [
        "00798615-0d71-4de7-af22-d157a141e24b",
        "02fcdea9-e17c-4e6c-828e-516950981ac4",
        "030910a4-6963-4b8f-8b4b-e860186443c8",
        "077d5b8c-2aae-48f8-9bb2-1784e086ddb2",
        "088061b8-b767-4f19-b364-16174d612e20",
        "0d3da7a0-c316-4c34-90cd-b794afad91c2",
        "0ef35c72-4d8a-4638-a00c-c1c326c5fcae",
        "115ea4b3-b858-4b74-9f4b-8bf2f61dbe06",
        "128b4524-540a-4369-879c-77030c6306e2"
    ]
}
```

#### Response

```json
{
    "updatedResources": {
        "now": 1760767936309,
        "refreshableTypes": [],
        // ...
    },
    "receivedUserPresents": [
        {
            "presentId": "4565daff-1131-4ed1-838d-47b82ea7a295",
            "seq": 9223370276086839000,
            "resourceType": "jewel",
            "resourceQuantity": 300,
            "expiredAt": 1763359936309,
            "reason": "初心者応援ログインキャンペーン1日目の報酬です。",
            "receivedAt": 1760767936309
        }
    ]
}
```

### `GET /api/user/{int:user_id}/story-favorite/friend/status/unit_story`

response(stub)

```json
{
    "friendStoryFavoriteStatuses": []
}
```

### `GET /api/user/{int:user_id}/story-favorite/friend/status/event_story`

response(stub)

```json
{
    "friendStoryFavoriteStatuses": []
}
```

### `GET /api/user/{int:user_id}/story-episode-bookmark/event_story/story/{int:story_id}`

response(stub)

```json
{
    "userStoryEpisodeBookmarks": []
}
```


## 提示

### `PUT /api/user/{int:user_id}/topic/{int:topic_id}`

携带 EmptyRequestCiphertext，服务端 `DELETE FROM unreadUserTopics WHERE userId = {user_id} AND topicId = {topic_id}`，返回 `updatedResources` 包含 `unreadUserTopics`，客户端据此更新未读提示

## 临时分析

### POST /api/user/<userId:int>/story/special_story/episode/<specialEpisodeId:int>

updatedResources 携带如下字段

```
. now
. refreshableTypes
+ userSpecialEpisodeStatuses
. userPresents
. unreadUserTopics
. userHomeBanners
. userMaterialExchanges
. userGachaCeilExchanges
+ userVirtualShops
+ userVirtualLiveTickets
. userRankMatchResult
. userViewableAppeal
. userBillingRefunds
. userUnprocessedOrders
. userInformations
- userBeginnerMissionBehavior
```


story status:
unreleased
already_read
