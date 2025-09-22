-- 用户注册信息表
CREATE TABLE user_registration (
    user_id            INTEGER PRIMARY KEY,
    signature          TEXT,
    platform           TEXT,
    device_model       TEXT,
    operating_system   TEXT,
    registered_at      INTEGER DEFAULT (strftime('%s', 'now') * 1000)
);

-- 用户游戏数据表
CREATE TABLE user_gamedata (
    user_id        INTEGER PRIMARY KEY,
    name           TEXT NOT NULL DEFAULT "セカイの住人",
    deck           INTEGER NOT NULL DEFAULT 1,
    rank           INTEGER NOT NULL DEFAULT 1,
    exp            INTEGER NOT NULL DEFAULT 0,
    total_exp      INTEGER NOT NULL DEFAULT 0,
    coin           INTEGER NOT NULL DEFAULT 0,
    virtual_coin   INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户付费货币表
CREATE TABLE user_charged_currency (
    user_id           INTEGER PRIMARY KEY,
    paid              INTEGER NOT NULL DEFAULT 0,
    free              INTEGER NOT NULL DEFAULT 0,
    -- TODO: paid_unit_prices
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户体力表
CREATE TABLE user_boost (
    user_id        INTEGER PRIMARY KEY,
    current        INTEGER NOT NULL DEFAULT 25,
    recovery_at    INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户配置表
CREATE TABLE user_config (
    user_id                  INTEGER PRIMARY KEY,
    default_music_type       TEXT NOT NULL DEFAULT "sekai",
    is_display_login_status  BOOLEAN NOT NULL DEFAULT 1,
    friend_request_scope     TEXT NOT NULL DEFAULT "all",
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户新手引导状态表
CREATE TABLE user_tutorial (
    user_id         INTEGER PRIMARY KEY,
    tutorial_status TEXT DEFAULT "start",
    tutorial_end_at INTEGER DEFAULT (strftime('%s', 'now') * 1000),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);


-- 用户区域状态表
CREATE TABLE user_area_status (
    user_id      INTEGER NOT NULL,
    area_id      INTEGER NOT NULL,
    -- TODO: "actionSets": []
    -- TODO: "areaItems": [],
    status       TEXT NOT NULL,
    PRIMARY KEY (user_id, area_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户区域播放列表状态表（仅部分区域有）
CREATE TABLE user_area_playlist_status (
    user_id         INTEGER NOT NULL,
    area_id         INTEGER NOT NULL,
    area_playlist_id INTEGER NOT NULL,
    status          TEXT NOT NULL,
    PRIMARY KEY (user_id, area_id, area_playlist_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id),
    FOREIGN KEY (user_id, area_id) REFERENCES user_area_status(user_id, area_id)
);

-- 用户卡牌表
CREATE TABLE user_cards (
    user_id                  INTEGER NOT NULL,
    card_id                  INTEGER NOT NULL,
    level                    INTEGER NOT NULL DEFAULT 1,
    exp                      INTEGER NOT NULL DEFAULT 0,
    total_exp                INTEGER NOT NULL DEFAULT 0,
    skill_level              INTEGER NOT NULL DEFAULT 1,
    skill_exp                INTEGER NOT NULL DEFAULT 0,
    total_skill_exp          INTEGER NOT NULL DEFAULT 0,
    master_rank              INTEGER NOT NULL DEFAULT 0,
    special_training_status  TEXT NOT NULL DEFAULT 'not_doing',
    default_image            TEXT NOT NULL DEFAULT 'original',
    duplicate_count          INTEGER NOT NULL DEFAULT 0,
    created_at               INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    PRIMARY KEY (user_id, card_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户卡片剧情表
CREATE TABLE user_card_episodes (
    user_id                  INTEGER NOT NULL,
    card_id                  INTEGER NOT NULL,
    card_episode_id          INTEGER NOT NULL,
    scenario_status          TEXT NOT NULL DEFAULT 'unreleased',
    scenario_status_reasons  TEXT DEFAULT '[]',  -- JSON字符串格式
    is_not_skipped           BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, card_id, card_episode_id),
    FOREIGN KEY (user_id, card_id) REFERENCES user_cards(user_id, card_id)
);

-- 用户卡组表
CREATE TABLE user_decks (
    user_id      INTEGER NOT NULL,
    deck_id      INTEGER NOT NULL,
    name         TEXT NOT NULL DEFAULT 'ユニット01',
    leader       INTEGER NOT NULL,
    sub_leader   INTEGER NOT NULL,
    member1      INTEGER NOT NULL,
    member2      INTEGER NOT NULL,
    member3      INTEGER NOT NULL,
    member4      INTEGER NOT NULL,
    member5      INTEGER NOT NULL,
    PRIMARY KEY (user_id, deck_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户音乐表
CREATE TABLE user_musics (
    user_id      INTEGER NOT NULL,
    music_id     INTEGER NOT NULL,
    PRIMARY KEY (user_id, music_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户音乐声乐表
CREATE TABLE user_music_vocals (
    user_id        INTEGER NOT NULL,
    music_id       INTEGER NOT NULL,
    music_vocal_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, music_id, music_vocal_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id),
    FOREIGN KEY (user_id, music_id) REFERENCES user_musics(user_id, music_id)
);

-- 用户商店表
CREATE TABLE user_shops (
    user_id    INTEGER NOT NULL,
    shop_id    INTEGER NOT NULL,
    PRIMARY KEY (user_id, shop_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户商店物品表
CREATE TABLE user_shop_items (
    user_id       INTEGER NOT NULL,
    shop_id       INTEGER NOT NULL,
    shop_item_id  INTEGER NOT NULL,
    level         INTEGER DEFAULT NULL,  -- 某些商店物品有等级，某些没有
    status        TEXT NOT NULL DEFAULT 'sale',
    PRIMARY KEY (user_id, shop_id, shop_item_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id),
    FOREIGN KEY (user_id, shop_id) REFERENCES user_shops(user_id, shop_id)
);

-- 用户计费商店物品表
CREATE TABLE user_billing_shop_items (
    user_id                INTEGER NOT NULL,
    billing_shop_item_id   INTEGER NOT NULL,
    count                  INTEGER NOT NULL DEFAULT 0,
    total_count            INTEGER NOT NULL DEFAULT 0,
    status                 TEXT NOT NULL DEFAULT 'sale',
    PRIMARY KEY (user_id, billing_shop_item_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户单元剧集状态表
CREATE TABLE user_unit_episode_statuses (
    user_id         INTEGER NOT NULL,
    story_type      TEXT NOT NULL DEFAULT 'unit_story',
    episode_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'unreleased',
    is_not_skipped  BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, story_type, episode_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户特殊剧集状态表
CREATE TABLE user_special_episode_statuses (
    user_id         INTEGER NOT NULL,
    story_type      TEXT NOT NULL DEFAULT 'special_story',
    episode_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'unreleased',
    is_not_skipped  BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, story_type, episode_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户活动剧集状态表
CREATE TABLE user_event_episode_statuses (
    user_id         INTEGER NOT NULL,
    story_type      TEXT NOT NULL DEFAULT 'event_story',
    episode_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'unreleased',
    is_not_skipped  BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, story_type, episode_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户归档活动剧集状态表 (可能是回响剧情)
CREATE TABLE user_archive_event_episode_statuses (
    user_id         INTEGER NOT NULL,
    story_type      TEXT NOT NULL DEFAULT 'archive_event_story',
    episode_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'unreleased',
    is_not_skipped  BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, story_type, episode_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);


-- 用户角色档案剧集状态表
CREATE TABLE user_character_profile_episode_statuses (
    user_id         INTEGER NOT NULL,
    story_type      TEXT NOT NULL DEFAULT 'character_profile_story',
    episode_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'unreleased',
    is_not_skipped  BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, story_type, episode_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户活动归档全读奖励表
CREATE TABLE user_event_archive_complete_read_rewards (
    user_id      INTEGER NOT NULL,
    event_story_id INTEGER NOT NULL,
    is_display_event_archive_complete_read_progress BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, event_story_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户组合信息表
CREATE TABLE user_units (
    user_id      INTEGER NOT NULL,
    unit         TEXT NOT NULL,
    rank         INTEGER NOT NULL DEFAULT 1,
    exp          INTEGER NOT NULL DEFAULT 0,
    total_exp    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, unit),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户礼物邮箱表
CREATE TABLE user_presents (
    user_id             INTEGER NOT NULL,
    present_id          TEXT NOT NULL,
    seq                 BIGINT NOT NULL DEFAULT (9223372036854775807 - strftime('%s', 'now') * 1000),
    resource_type       TEXT NOT NULL,
    resource_id         INTEGER,
    resource_quantity   INTEGER NOT NULL DEFAULT 1,
    reason              TEXT NOT NULL,
    granted_at          INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    PRIMARY KEY (user_id, present_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户3D服装状态表
CREATE TABLE user_costume_3d_statuses (
    user_id       INTEGER NOT NULL,
    costume_3d_id INTEGER NOT NULL,
    obtained_at   INTEGER DEFAULT NULL,  -- 某些状态下没有获得时间
    status        TEXT NOT NULL,         -- available, forbidden, sale等状态
    PRIMARY KEY (user_id, costume_3d_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户3D服装商店物品表
CREATE TABLE user_costume_3d_shop_items (
    user_id                   INTEGER NOT NULL,
    costume_3d_shop_item_id   INTEGER NOT NULL,
    status                    TEXT NOT NULL,  -- sale， forbidden 等状态
    PRIMARY KEY (user_id, costume_3d_shop_item_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户角色3D服装配置表
CREATE TABLE user_character_costume_3ds (
    user_id              INTEGER NOT NULL,
    character_id         INTEGER NOT NULL,
    unit                 TEXT NOT NULL,
    head_costume_3d_id   INTEGER NOT NULL,
    hair_costume_3d_id   INTEGER NOT NULL,
    body_costume_3d_id   INTEGER NOT NULL,
    PRIMARY KEY (user_id, character_id, unit),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户解锁条件表
CREATE TABLE user_release_conditions (
    user_id               INTEGER NOT NULL,
    release_condition_id  INTEGER NOT NULL,
    created_at            BIGINT NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    PRIMARY KEY (user_id, release_condition_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户未读话题表
CREATE TABLE unread_user_topics (
    user_id       INTEGER NOT NULL,
    topic_id      INTEGER NOT NULL,
    topic_status  TEXT NOT NULL DEFAULT 'unread',
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 首页横幅表（全局信息，与用户无关）
CREATE TABLE home_banners (
    home_banner_id                INTEGER PRIMARY KEY,
    seq                          INTEGER NOT NULL,
    home_banner_type             TEXT NOT NULL,
    name                         TEXT NOT NULL,
    assetbundle_name             TEXT NOT NULL,
    transition_destination_type  TEXT NOT NULL,
    transition_destination_id    INTEGER DEFAULT NULL,
    start_at                     BIGINT NOT NULL,
    end_at                       BIGINT NOT NULL,
    url                          TEXT DEFAULT NULL
);

-- 用户印章表
CREATE TABLE user_stamps (
    user_id      INTEGER NOT NULL,
    stamp_id     INTEGER NOT NULL,
    obtained_at  INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    PRIMARY KEY (user_id, stamp_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户材料兑换表
CREATE TABLE user_material_exchanges (
    user_id                  INTEGER NOT NULL,
    material_exchange_id     INTEGER NOT NULL,
    exchange_count           INTEGER NOT NULL DEFAULT 0,
    total_exchange_count     INTEGER NOT NULL DEFAULT 0,
    exchange_status          TEXT NOT NULL DEFAULT 'exchangeable',
    exchange_remaining       INTEGER DEFAULT NULL, -- 剩余兑换次数（可选字段）
    refreshed_at             BIGINT DEFAULT NULL, -- 刷新时间（可选字段）
    PRIMARY KEY (user_id, material_exchange_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户扭蛋保底兑换表
CREATE TABLE user_gacha_ceil_exchanges (
    user_id                  INTEGER NOT NULL,
    gacha_ceil_exchange_id   INTEGER NOT NULL,
    exchange_status          TEXT NOT NULL DEFAULT 'exchangeable',
    exchange_remaining       INTEGER DEFAULT NULL,  -- 剩余兑换次数（可选字段）
    PRIMARY KEY (user_id, gacha_ceil_exchange_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户角色表
CREATE TABLE user_characters (
    user_id          INTEGER NOT NULL,
    character_id     INTEGER NOT NULL,
    character_rank   INTEGER NOT NULL DEFAULT 1,
    exp              INTEGER NOT NULL DEFAULT 0,
    total_exp        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户角色任务V2表
CREATE TABLE user_character_mission_v2s (
    user_id                   INTEGER NOT NULL,
    character_mission_type    TEXT NOT NULL,
    character_id              INTEGER NOT NULL,
    progress                  INTEGER NOT NULL DEFAULT 0,
    achieved_missions         TEXT NOT NULL DEFAULT '[]',  -- JSON字符串格式存储任务ID数组
    PRIMARY KEY (user_id, character_mission_type, character_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户角色任务V2状态表
CREATE TABLE user_character_mission_v2_statuses (
    user_id               INTEGER NOT NULL,
    mission_id            INTEGER NOT NULL,
    parameter_group_id    INTEGER NOT NULL,
    seq                   INTEGER NOT NULL,
    character_id          INTEGER NOT NULL,
    mission_status        TEXT NOT NULL DEFAULT 'not_achieved',
    PRIMARY KEY (user_id, mission_id, parameter_group_id, seq, character_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户虚拟商店表
CREATE TABLE user_virtual_shops (
    user_id          INTEGER NOT NULL,
    virtual_shop_id  INTEGER NOT NULL,
    PRIMARY KEY (user_id, virtual_shop_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户虚拟商店物品表
CREATE TABLE user_virtual_shop_items (
    user_id                 INTEGER NOT NULL,
    virtual_shop_id         INTEGER NOT NULL,
    virtual_shop_item_id    INTEGER NOT NULL,
    status                  TEXT NOT NULL DEFAULT 'sale',
    PRIMARY KEY (user_id, virtual_shop_id, virtual_shop_item_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id),
    FOREIGN KEY (user_id, virtual_shop_id) REFERENCES user_virtual_shops(user_id, virtual_shop_id)
);

-- 用户活动兑换表
CREATE TABLE user_event_exchanges (
    user_id              INTEGER NOT NULL,
    event_id             INTEGER NOT NULL,
    event_exchange_id    INTEGER NOT NULL,
    exchange_remaining   INTEGER DEFAULT NULL,  -- 剩余兑换次数（可选字段）
    exchange_status      TEXT NOT NULL DEFAULT 'exchangeable',
    PRIMARY KEY (user_id, event_id, event_exchange_id),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户信息表（全局信息，与用户无关）
CREATE TABLE user_informations (
    id                      INTEGER PRIMARY KEY,
    seq                     INTEGER NOT NULL,
    display_order          INTEGER NOT NULL,
    information_type       TEXT NOT NULL,
    information_tag        TEXT NOT NULL,
    browse_type            TEXT NOT NULL,
    platform               TEXT NOT NULL,
    title                  TEXT NOT NULL,
    path                   TEXT NOT NULL,
    start_at               BIGINT NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    end_at                 BIGINT DEFAULT NULL,
    banner_assetbundle_name TEXT DEFAULT NULL
);

-- 用户 credential 表
CREATE TABLE user_credentials (
    user_id        INTEGER PRIMARY KEY, -- NOTICE: 事实上，原服务器这里可能是 TEXT 类型，但为了简化实现，改为 INTEGER 类型
    credential    TEXT NOT NULL,    -- uuid
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);


CREATE TABLE user_tokens (
    user_id        INTEGER PRIMARY KEY, -- NOTICE: 事实上，原服务器这里可能是 TEXT 类型，但为了简化实现，改为 INTEGER 类型
    session_token  TEXT NOT NULL,   -- uuid
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);

-- 用户引继码表
CREATE TABLE user_inherit (
    user_id        INTEGER PRIMARY KEY,
    inherit_id   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    created_at     BIGINT NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    FOREIGN KEY (user_id) REFERENCES user_registration(user_id)
);