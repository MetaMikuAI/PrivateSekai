import os
import json
import time
from typing import Optional, Any
from random import choices
from string import ascii_letters

from config import logger
from database import SekaiDatabase
from cards import give_new_card


# 服务端会在接收到 summary 状态时根据旧状态给出初始卡牌，然后置summary
# 服务端在收到 end 状态时置 end 并添加 tutorialEndAt 键
# start -> opening_1(Sekai Miku) -> gameplay(tell your world) -> opening_2(第二段剧情) -> unit_select -> idol_opening -> summary -> end

def update_tutorial_status(user_id: int, new_status: str) -> set[str]:
    with SekaiDatabase() as db:
        data = db.get_user_tutorial(user_id)
        if data is None:
            raise ValueError(f"User tutorial data for user ID {user_id} not found.")

    valid_statuses = ['start', 'opening_1', 'gameplay', 'opening_2', 'unit_select', 'summary', 'end']

    tutorial_cards_by_unit = {
        'light_sound_opening': [1, 5, 9, 13, 81, 82, 89, 93, 97, 98, 101, 105],
        'idol_opening': [17, 21, 25, 29, 81, 83, 89, 90, 93, 97, 101, 105],
        'street_opening': [33, 37, 41, 45, 81, 84, 89, 93, 94, 97, 102, 105],
        'theme_park_opening': [49, 53, 57, 61, 81, 85, 89, 93, 97, 101, 105, 106],
        'school_refusal_opening': [65, 69, 73, 77, 81, 86, 89, 93, 97, 101, 105]
    }

    if new_status not in valid_statuses and new_status not in tutorial_cards_by_unit:
        raise ValueError(f"Invalid tutorial status: {new_status}")

    # 对于阅读完初始剧情的需要做一些初始化任务
    # 0. 修改 tutorialStatus （这是废话，已完成）
    # 1. 发放初始卡牌，一般为 12 张 （已完成）
    # 2. 设定 userDecks （TODO）
    # 3. 设定 userUnitEpisodeStatuses （TODO）
    with SekaiDatabase() as db:
        current_status = data['tutorialStatus']
        data['tutorialStatus'] = new_status
        if current_status in tutorial_cards_by_unit:
            card_ids = tutorial_cards_by_unit[current_status]
            [give_new_card(db, user_id, cid) for cid in card_ids]
        db.set_user_tutorial(user_id, data)

    rtypes = {"userTutorial", "userCards"} # TODO 设定 userDecks userUnitEpisodeStatuses 时别忘了这里
    return rtypes

def update_user_gamedata(user_id: int, new_gamedata: dict) -> set[str]:
    with SekaiDatabase() as db:
        gamedata = db.get_user_gamedata(user_id)
        if gamedata is None:
            raise ValueError(f"User gamedata for user ID {user_id} not found.")

        gamedata["name"] = new_gamedata.get("name", gamedata.get("name", ""))
        db.set_user_gamedata(user_id, gamedata)
    
    rtypes = {"userGamedata"}
    return rtypes



def create_new_user(user_id: Optional[int], device_info: Optional[dict[str, Any]]) -> int:
    with open('data/users/0.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with SekaiDatabase() as db:
        if user_id is None:
            user_id = db.get_new_user_id()
        db.set_user_registration(user_id, data["userRegistration"])
        db.set_user_gamedata(user_id, data["userGamedata"])
        db.set_user_charged_currency(user_id, data["userChargedCurrency"])
        db.set_user_boost(user_id, data["userBoost"])
        db.set_user_config(user_id, data["userConfig"])
        db.set_user_tutorial(user_id, data["userTutorial"])
        db.set_user_areas(user_id, data["userAreas"])
        db.set_user_action_sets(user_id, data["userActionSets"])
        db.set_user_cards(user_id, data["userCards"])
        db.set_user_decks(user_id, data["userDecks"])
        db.set_user_musics(user_id, data["userMusics"])
        db.set_user_music_vocals(user_id, data["userMusicVocals"])
        db.set_user_music_results(user_id, data["userMusicResults"])
        db.set_user_music_achievements(user_id, data["userMusicAchievements"])
        db.set_user_shops(user_id, data["userShops"])
        db.set_user_billing_shop_items(user_id, data["userBillingShopItems"])
        db.set_user_colorful_pass(user_id, data["userColorfulPass"])
        db.set_user_colorful_pass_v2(user_id, data["userColorfulPassV2"])
        db.set_user_practice_tickets(user_id, data["userPracticeTickets"])
        db.set_user_skill_practice_tickets(user_id, data["userSkillPracticeTickets"])
        db.set_user_materials(user_id, data["userMaterials"])
        db.set_user_gachas(user_id, data["userGachas"])
        db.set_user_gacha_bonus_points(user_id, data["userGachaBonusPoints"])
        db.set_user_unit_episode_statuses(user_id, data["userUnitEpisodeStatuses"])
        db.set_user_special_episode_statuses(user_id, data["userSpecialEpisodeStatuses"])
        db.set_user_event_episode_statuses(user_id, data["userEventEpisodeStatuses"])
        db.set_user_archive_event_episode_statuses(user_id, data["userArchiveEventEpisodeStatuses"])
        db.set_user_character_profile_episode_statuses(user_id, data["userCharacterProfileEpisodeStatuses"])
        db.set_user_story_mission(user_id, data["userStoryMission"])
        db.set_user_event_archive_complete_read_rewards(user_id, data["userEventArchiveCompleteReadRewards"])
        db.set_user_units(user_id, data["userUnits"])
        db.set_user_presents(user_id, data["userPresents"])
        db.set_user_costume_3d_statuses(user_id, data["userCostume3dStatuses"])
        db.set_user_costume_3d_shop_items(user_id, data["userCostume3dShopItems"])
        db.set_user_character_costume_3ds(user_id, data["userCharacterCostume3ds"])
        db.set_user_release_conditions(user_id, data["userReleaseConditions"])
        db.set_unread_user_topics(user_id, data["unreadUserTopics"])
        db.set_user_home_banners(data["userHomeBanners"])
        db.set_user_stamps(user_id, data["userStamps"])
        db.set_user_stamp_favorites(user_id, data["userStampFavorites"])
        db.set_user_stamp_favorite_tabs(user_id, data["userStampFavoriteTabs"])
        db.set_user_material_exchanges(user_id, data["userMaterialExchanges"])
        db.set_user_gacha_ceil_exchanges(user_id, data["userGachaCeilExchanges"])
        db.set_user_gacha_ceil_items(user_id, data["userGachaCeilItems"])
        db.set_user_gacha_tickets(user_id, data["userGachaTickets"])
        db.set_user_boost_items(user_id, data["userBoostItems"])
        db.set_user_characters(user_id, data["userCharacters"])
        db.set_user_character_mission_v2s(user_id, data["userCharacterMissionV2s"])
        db.set_user_character_mission_v2_statuses(user_id, data["userCharacterMissionV2Statuses"])
        db.set_user_bonds(user_id, data["userBonds"])
        db.set_user_bonds_rewards(user_id, data["userBondsRewards"])
        db.set_user_normal_missions(user_id, data["userNormalMissions"])
        db.set_user_beginner_missions(user_id, data["userBeginnerMissions"])
        db.set_user_beginner_mission_v2s(user_id, data["userBeginnerMissionV2s"])
        db.set_user_beginner_mission_behavior(user_id, data["userBeginnerMissionBehavior"])
        db.set_user_mission_statuses(user_id, data["userMissionStatuses"])
        db.set_user_live_missions(user_id, data["userLiveMissions"])
        db.set_user_fix_costumes(user_id, data["userFixCostumes"])
        db.set_user_profile(user_id, data["userProfile"])
        db.set_user_honors(user_id, data["userHonors"])
        db.set_user_honor_missions(user_id, data["userHonorMissions"])
        db.set_user_profile_honors(user_id, data["userProfileHonors"])
        db.set_user_bonds_honors(user_id, data["userBondsHonors"])
        db.set_user_bonds_honor_words(user_id, data["userBondsHonorWords"])
        db.set_user_player_frames(user_id, data["userPlayerFrames"])
        db.set_user_challenge_live_play_statuses(user_id, data["userChallengeLivePlayStatuses"])
        db.set_user_challenge_live_solo_decks(user_id, data["userChallengeLiveSoloDecks"])
        db.set_user_challenge_live_solo_results(user_id, data["userChallengeLiveSoloResults"])
        db.set_user_challenge_live_solo_stages(user_id, data["userChallengeLiveSoloStages"])
        db.set_user_challenge_live_solo_high_score_rewards(user_id, data["userChallengeLiveSoloHighScoreRewards"])
        db.set_user_virtual_live_beginner_schedule_statuses(user_id, data["userVirtualLiveBeginnerScheduleStatuses"])
        db.set_user_virtual_live_schedule_statuses(user_id, data["userVirtualLiveScheduleStatuses"])
        db.set_user_archive_virtual_live_statuses(user_id, data["userArchiveVirtualLiveStatuses"])
        db.set_user_virtual_live_rewards(user_id, data["userVirtualLiveRewards"])
        db.set_user_virtual_shops(user_id, data["userVirtualShops"])
        db.set_user_virtual_live_tickets(user_id, data["userVirtualLiveTickets"])
        db.set_user_virtual_live_pamphlets(user_id, data["userVirtualLivePamphlets"])
        db.set_user_used_virtual_live_tickets(user_id, data["userUsedVirtualLiveTickets"])
        db.set_user_avatar(user_id, data["userAvatar"])
        db.set_user_avatar_accessories(user_id, data["userAvatarAccessories"])
        db.set_user_avatar_costumes(user_id, data["userAvatarCostumes"])
        db.set_user_avatar_motions(user_id, data["userAvatarMotions"])
        db.set_user_avatar_motion_favorites(user_id, data["userAvatarMotionFavorites"])
        db.set_user_avatar_skin_colors(user_id, data["userAvatarSkinColors"])
        db.set_user_avatar_coordinates(user_id, data["userAvatarCoordinates"])
        db.set_user_penlights(user_id, data["userPenlights"])
        db.set_user_login_bonuses(user_id, data["userLoginBonuses"])
        db.set_user_platform_inherit_ios(user_id, data["userPlatformInheritIos"])
        db.set_user_platform_inherit_android(user_id, data["userPlatformInheritAndroid"])
        db.set_user_inherit(user_id, data["userInherit"])
        db.set_user_character_live_usage_counts(user_id, data["userCharacterLiveUsageCounts"])
        db.set_user_one_time_behaviors(user_id, data["userOneTimeBehaviors"])
        db.set_user_events(user_id, data["userEvents"])
        db.set_user_event_items(user_id, data["userEventItems"])
        db.set_user_event_exchanges(user_id, data["userEventExchanges"])
        db.set_user_cheerful_carnivals(user_id, data["userCheerfulCarnivals"])
        db.set_user_cheerful_carnival_behaviors(user_id, data["userCheerfulCarnivalBehaviors"])
        db.set_user_multi_live_penalty(user_id, data["userMultiLivePenalty"])
        db.set_user_auto_live(user_id, data["userAutoLive"])
        db.set_user_friends(user_id, data["userFriends"])
        db.set_user_blocks(user_id, data["userBlocks"])
        db.set_user_gacha_wishes(user_id, data["userGachaWishes"])
        db.set_user_gift_gacha_wishes(user_id, data["userGiftGachaWishes"])
        db.set_user_categorized_gacha_wishes(user_id, data["userCategorizedGachaWishes"])
        db.set_user_boost_granteds(user_id, data["userBoostGranteds"])
        db.set_user_boost_receivables(user_id, data["userBoostReceivables"])
        db.set_user_boost_received(user_id, data["userBoostReceived"])
        db.set_user_cheerful_carnival_result_rewards(user_id, data["userCheerfulCarnivalResultRewards"])
        db.set_user_gacha_ceil_exchange_substitute_costs(user_id, data["userGachaCeilExchangeSubstituteCosts"])
        db.set_user_custom_profiles(user_id, data["userCustomProfiles"])
        db.set_user_custom_profile_cards(user_id, data["userCustomProfileCards"])
        db.set_user_custom_profile_resources(user_id, data["userCustomProfileResources"])
        db.set_user_custom_profile_resource_usages(user_id, data["userCustomProfileResourceUsages"])
        db.set_user_custom_profile_gachas(user_id, data["userCustomProfileGachas"])
        db.set_user_rank_match_result(user_id, data["userRankMatchResult"])
        db.set_user_rank_match_seasons(user_id, data["userRankMatchSeasons"])
        db.set_user_panel_missions(user_id, data["userPanelMissions"])
        db.set_user_panel_mission_sheets(user_id, data["userPanelMissionSheets"])
        db.set_user_panel_mission_achieved_elements(user_id, data["userPanelMissionAchievedElements"])
        db.set_user_event_missions(user_id, data["userEventMissions"])
        db.set_user_my_lists(user_id, data["userMyLists"])
        db.set_user_paid_virtual_lives(user_id, data["userPaidVirtualLives"])
        db.set_user_paid_virtual_live_statuses(user_id, data["userPaidVirtualLiveStatuses"])
        db.set_user_paid_virtual_live_shop_items(user_id, data["userPaidVirtualLiveShopItems"])
        db.set_user_gacha_free_resources(user_id, data["userGachaFreeResources"])
        db.set_user_story_favorites(user_id, data["userStoryFavorites"])
        db.set_user_bookmarked_stories(user_id, data["userBookmarkedStories"])
        db.set_user_friend_invitation_campaigns(user_id, data["userFriendInvitationCampaigns"])
        db.set_user_friend_invitation_campaign_mission_reward_counts(user_id, data["userFriendInvitationCampaignMissionRewardCounts"])
        db.set_user_world_blooms(user_id, data["userWorldBlooms"])
        db.set_user_world_bloom_support_decks(user_id, data["userWorldBloomSupportDecks"])
        db.set_user_live_character_archive_voice(user_id, data["userLiveCharacterArchiveVoice"])
        db.set_user_ad_rewards(user_id, data["userAdRewards"])
        db.set_user_serial_code_items(user_id, data["userSerialCodeItems"])
        db.set_user_appeals(user_id, data["userAppeals"])
        db.set_user_viewable_appeal(user_id, data["userViewableAppeal"])
        db.set_user_billing_refund_penalty(user_id, data["userBillingRefundPenalty"])
        db.set_user_billing_refunds(user_id, data["userBillingRefunds"])
        db.set_user_unprocessed_orders(user_id, data["userUnprocessedOrders"])
        db.set_user_omikujis(user_id, data["userOmikujis"])
        db.set_user_preliminary_tournament_live_results(user_id, data["userPreliminaryTournamentLiveResults"])
        db.set_user_platforms(user_id, data["userPlatforms"])
        db.set_user_mysekai_materials(user_id, data["userMysekaiMaterials"])
        db.set_user_mysekai_canvases(user_id, data["userMysekaiCanvases"])
        db.set_user_mysekai_gates(user_id, data["userMysekaiGates"])
        db.set_user_mysekai_character_talks(user_id, data["userMysekaiCharacterTalks"])
        db.set_user_mysekai_colorful_pass(user_id, data["userMysekaiColorfulPass"])
        db.set_user_mysekai_fixture_game_character_performance_bonuses(user_id, data["userMysekaiFixtureGameCharacterPerformanceBonuses"])
        db.set_user_informations(data["userInformations"])
        if device_info:
            db.update_user_device_info(user_id, device_info)

    # init_credential(user_id)
    return user_id


def get_suite_user_data(user_id: int) -> dict:
    with SekaiDatabase() as db:
        data = {
            "now": int(time.time() * 1000),
            "refreshableTypes": [],
            "userRegistration": db.get_user_registration(user_id),
            "userGamedata": db.get_user_gamedata(user_id),
            "userChargedCurrency": db.get_user_charged_currency(user_id),
            "userBoost": db.get_user_boost(user_id),
            "userConfig": db.get_user_config(user_id),
            "userTutorial": db.get_user_tutorial(user_id),
            "userAreas": db.get_user_areas(user_id),
            "userActionSets": db.get_user_action_sets(user_id),
            "userCards": db.get_user_cards(user_id),
            "userDecks": db.get_user_decks(user_id),
            "userMusics": db.get_user_musics(user_id),
            "userMusicVocals": db.get_user_music_vocals(user_id),
            "userMusicResults": db.get_user_music_results(user_id),
            "userMusicAchievements": db.get_user_music_achievements(user_id),
            "userShops": db.get_user_shops(user_id),
            "userBillingShopItems": db.get_user_billing_shop_items(user_id),
            "userColorfulPass": db.get_user_colorful_pass(user_id),
            "userColorfulPassV2": db.get_user_colorful_pass_v2(user_id),
            "userPracticeTickets": db.get_user_practice_tickets(user_id),
            "userSkillPracticeTickets": db.get_user_skill_practice_tickets(user_id),
            "userMaterials": db.get_user_materials(user_id),
            "userGachas": db.get_user_gachas(user_id),
            "userGachaBonusPoints": db.get_user_gacha_bonus_points(user_id),
            "userUnitEpisodeStatuses": db.get_user_unit_episode_statuses(user_id),
            "userSpecialEpisodeStatuses": db.get_user_special_episode_statuses(user_id),
            "userEventEpisodeStatuses": db.get_user_event_episode_statuses(user_id),
            "userArchiveEventEpisodeStatuses": db.get_user_archive_event_episode_statuses(user_id),
            "userCharacterProfileEpisodeStatuses": db.get_user_character_profile_episode_statuses(user_id),
            "userStoryMission": db.get_user_story_mission(user_id),
            "userEventArchiveCompleteReadRewards": db.get_user_event_archive_complete_read_rewards(user_id),
            "userUnits": db.get_user_units(user_id),
            "userPresents": db.get_user_presents(user_id),
            "userCostume3dStatuses": db.get_user_costume_3d_statuses(user_id),
            "userCostume3dShopItems": db.get_user_costume_3d_shop_items(user_id),
            "userCharacterCostume3ds": db.get_user_character_costume_3ds(user_id),
            "userReleaseConditions": db.get_user_release_conditions(user_id),
            "unreadUserTopics": db.get_unread_user_topics(user_id),
            "userHomeBanners": db.get_user_home_banners(user_id),
            "userStamps": db.get_user_stamps(user_id),
            "userStampFavorites": db.get_user_stamp_favorites(user_id),
            "userStampFavoriteTabs": db.get_user_stamp_favorite_tabs(user_id),
            "userMaterialExchanges": db.get_user_material_exchanges(user_id),
            "userGachaCeilExchanges": db.get_user_gacha_ceil_exchanges(user_id),
            "userGachaCeilItems": db.get_user_gacha_ceil_items(user_id),
            "userGachaTickets": db.get_user_gacha_tickets(user_id),
            "userBoostItems": db.get_user_boost_items(user_id),
            "userCharacters": db.get_user_characters(user_id),
            "userCharacterMissionV2s": db.get_user_character_mission_v2s(user_id),
            "userCharacterMissionV2Statuses": db.get_user_character_mission_v2_statuses(user_id),
            "userBonds": db.get_user_bonds(user_id),
            "userBondsRewards": db.get_user_bonds_rewards(user_id),
            "userNormalMissions": db.get_user_normal_missions(user_id),
            "userBeginnerMissions": db.get_user_beginner_missions(user_id),
            "userBeginnerMissionV2s": db.get_user_beginner_mission_v2s(user_id),
            "userBeginnerMissionBehavior": db.get_user_beginner_mission_behavior(user_id),
            "userMissionStatuses": db.get_user_mission_statuses(user_id),
            "userLiveMissions": db.get_user_live_missions(user_id),
            "userFixCostumes": db.get_user_fix_costumes(user_id),
            "userProfile": db.get_user_profile(user_id),
            "userHonors": db.get_user_honors(user_id),
            "userHonorMissions": db.get_user_honor_missions(user_id),
            "userProfileHonors": db.get_user_profile_honors(user_id),
            "userBondsHonors": db.get_user_bonds_honors(user_id),
            "userBondsHonorWords": db.get_user_bonds_honor_words(user_id),
            "userPlayerFrames": db.get_user_player_frames(user_id),
            "userChallengeLivePlayStatuses": db.get_user_challenge_live_play_statuses(user_id),
            "userChallengeLiveSoloDecks": db.get_user_challenge_live_solo_decks(user_id),
            "userChallengeLiveSoloResults": db.get_user_challenge_live_solo_results(user_id),
            "userChallengeLiveSoloStages": db.get_user_challenge_live_solo_stages(user_id),
            "userChallengeLiveSoloHighScoreRewards": db.get_user_challenge_live_solo_high_score_rewards(user_id),
            "userVirtualLiveBeginnerScheduleStatuses": db.get_user_virtual_live_beginner_schedule_statuses(user_id),
            "userVirtualLiveScheduleStatuses": db.get_user_virtual_live_schedule_statuses(user_id),
            "userArchiveVirtualLiveStatuses": db.get_user_archive_virtual_live_statuses(user_id),
            "userVirtualLiveRewards": db.get_user_virtual_live_rewards(user_id),
            "userVirtualShops": db.get_user_virtual_shops(user_id),
            "userVirtualLiveTickets": db.get_user_virtual_live_tickets(user_id),
            "userVirtualLivePamphlets": db.get_user_virtual_live_pamphlets(user_id),
            "userUsedVirtualLiveTickets": db.get_user_used_virtual_live_tickets(user_id),
            "userAvatar": db.get_user_avatar(user_id),
            "userAvatarAccessories": db.get_user_avatar_accessories(user_id),
            "userAvatarCostumes": db.get_user_avatar_costumes(user_id),
            "userAvatarMotions": db.get_user_avatar_motions(user_id),
            "userAvatarMotionFavorites": db.get_user_avatar_motion_favorites(user_id),
            "userAvatarSkinColors": db.get_user_avatar_skin_colors(user_id),
            "userAvatarCoordinates": db.get_user_avatar_coordinates(user_id),
            "userPenlights": db.get_user_penlights(user_id),
            "userLoginBonuses": db.get_user_login_bonuses(user_id),
            "userPlatformInheritIos": db.get_user_platform_inherit_ios(user_id),
            "userPlatformInheritAndroid": db.get_user_platform_inherit_android(user_id),
            "userInherit": db.get_user_inherit(user_id),
            "userCharacterLiveUsageCounts": db.get_user_character_live_usage_counts(user_id),
            "userOneTimeBehaviors": db.get_user_one_time_behaviors(user_id),
            "userEvents": db.get_user_events(user_id),
            "userEventItems": db.get_user_event_items(user_id),
            "userEventExchanges": db.get_user_event_exchanges(user_id),
            "userCheerfulCarnivals": db.get_user_cheerful_carnivals(user_id),
            "userCheerfulCarnivalBehaviors": db.get_user_cheerful_carnival_behaviors(user_id),
            "userMultiLivePenalty": db.get_user_multi_live_penalty(user_id),
            "userAutoLive": db.get_user_auto_live(user_id),
            "userFriends": db.get_user_friends(user_id),
            "userBlocks": db.get_user_blocks(user_id),
            "userGachaWishes": db.get_user_gacha_wishes(user_id),
            "userGiftGachaWishes": db.get_user_gift_gacha_wishes(user_id),
            "userCategorizedGachaWishes": db.get_user_categorized_gacha_wishes(user_id),
            "userBoostGranteds": db.get_user_boost_granteds(user_id),
            "userBoostReceivables": db.get_user_boost_receivables(user_id),
            "userBoostReceived": db.get_user_boost_received(user_id),
            "userCheerfulCarnivalResultRewards": db.get_user_cheerful_carnival_result_rewards(user_id),
            "userGachaCeilExchangeSubstituteCosts": db.get_user_gacha_ceil_exchange_substitute_costs(user_id),
            "userCustomProfiles": db.get_user_custom_profiles(user_id),
            "userCustomProfileCards": db.get_user_custom_profile_cards(user_id),
            "userCustomProfileResources": db.get_user_custom_profile_resources(user_id),
            "userCustomProfileResourceUsages": db.get_user_custom_profile_resource_usages(user_id),
            "userCustomProfileGachas": db.get_user_custom_profile_gachas(user_id),
            "userRankMatchResult": db.get_user_rank_match_result(user_id),
            "userRankMatchSeasons": db.get_user_rank_match_seasons(user_id),
            "userPanelMissions": db.get_user_panel_missions(user_id),
            "userPanelMissionSheets": db.get_user_panel_mission_sheets(user_id),
            "userPanelMissionAchievedElements": db.get_user_panel_mission_achieved_elements(user_id),
            "userEventMissions": db.get_user_event_missions(user_id),
            "userMyLists": db.get_user_my_lists(user_id),
            "userPaidVirtualLives": db.get_user_paid_virtual_lives(user_id),
            "userPaidVirtualLiveStatuses": db.get_user_paid_virtual_live_statuses(user_id),
            "userPaidVirtualLiveShopItems": db.get_user_paid_virtual_live_shop_items(user_id),
            "userGachaFreeResources": db.get_user_gacha_free_resources(user_id),
            "userStoryFavorites": db.get_user_story_favorites(user_id),
            "userBookmarkedStories": db.get_user_bookmarked_stories(user_id),
            "userFriendInvitationCampaigns": db.get_user_friend_invitation_campaigns(user_id),
            "userFriendInvitationCampaignMissionRewardCounts": db.get_user_friend_invitation_campaign_mission_reward_counts(user_id),
            "userWorldBlooms": db.get_user_world_blooms(user_id),
            "userWorldBloomSupportDecks": db.get_user_world_bloom_support_decks(user_id),
            "userLiveCharacterArchiveVoice": db.get_user_live_character_archive_voice(user_id),
            "userAdRewards": db.get_user_ad_rewards(user_id),
            "userSerialCodeItems": db.get_user_serial_code_items(user_id),
            "userAppeals": db.get_user_appeals(user_id),
            "userViewableAppeal": db.get_user_viewable_appeal(user_id),
            "userBillingRefundPenalty": db.get_user_billing_refund_penalty(user_id),
            "userBillingRefunds": db.get_user_billing_refunds(user_id),
            "userUnprocessedOrders": db.get_user_unprocessed_orders(user_id),
            "userOmikujis": db.get_user_omikujis(user_id),
            "userPreliminaryTournamentLiveResults": db.get_user_preliminary_tournament_live_results(user_id),
            "userPlatforms": db.get_user_platforms(user_id),
            "userMysekaiMaterials": db.get_user_mysekai_materials(user_id),
            "userMysekaiCanvases": db.get_user_mysekai_canvases(user_id),
            "userMysekaiGates": db.get_user_mysekai_gates(user_id),
            "userMysekaiCharacterTalks": db.get_user_mysekai_character_talks(user_id),
            "userMysekaiColorfulPass": db.get_user_mysekai_colorful_pass(user_id),
            "userMysekaiFixtureGameCharacterPerformanceBonuses": db.get_user_mysekai_fixture_game_character_performance_bonuses(user_id),
            "userInformations": db.get_user_informations(user_id)
        }
    return data

def get_user_refresh(user_id: int, refresh_types_additional: Optional[set] = None) -> dict:
    refresh_types = {
        "now", 
        "refreshableTypes", 
        "userPresents", 
        "unreadUserTopics", 
        "userHomeBanners", 
        "userMaterialExchanges", 
        "userGachaCeilExchanges", 
        "userBeginnerMissionBehavior",
        "userRankMatchResult", 
        "userViewableAppeal",
        "userBillingRefunds",
        "userUnprocessedOrders",
        "userInformations"
    }
    refresh_types.update(refresh_types_additional) if refresh_types_additional else refresh_types

    refresh_data = {}
    with SekaiDatabase() as db:
        for rtype in refresh_types:
            if rtype in db.getters:
                refresh_data[rtype] = db.getters[rtype](db, user_id)
            else:
                logger.warning(f"Refresh type {rtype} not found in database getters.")
        
    return {"updatedResources": refresh_data}

def get_user_registration(user_id: int) -> Optional[dict[str, Any]]:
    with SekaiDatabase() as db:
        return db.get_user_registration(user_id)

def set_user_inherit(user_id: int, password: str) -> str:
    with SekaiDatabase() as db:
        inherit_data = db.get_user_inherit(user_id)
        if inherit_data is not None:
            raise ValueError(f"User ID {user_id} already has inherit data.")
        
        rand_inherit_id = ''.join(choices(ascii_letters, k=16))
        while db.get_user_inherit_by_inherit_id(rand_inherit_id):
            rand_inherit_id = ''.join(choices(ascii_letters, k=16))

        inherit_data = {
            "inheritId": rand_inherit_id,
            "password": password
        }
        db.set_user_inherit(user_id, inherit_data)
        return rand_inherit_id

def verify_user_inherit(inherit_id: str, password: str) -> Optional[int]:
    with SekaiDatabase() as db:
        inherit_data = db.get_user_inherit_by_inherit_id(inherit_id)
        if inherit_data is None:
            return None
        if inherit_data["password"] != password:
            return None
        return inherit_data["userId"]


def get_after_user_gamedata(user_id: int) -> Optional[dict[str, Any]]:
    with SekaiDatabase() as db:
        full_user_gamedata = db.get_user_gamedata(user_id)
        if full_user_gamedata is None:
            return None
        after_user_gamedata = {
            "userId": full_user_gamedata["userId"],
            "name": full_user_gamedata["name"],
            "deck": full_user_gamedata["deck"],
            "rank": full_user_gamedata["rank"]
        }
        return after_user_gamedata

def create_default_user() -> None:
    create_new_user(0, None)

if __name__ == "__main__":
    # for test
    import os
    if os.path.exists('sekai.db'):
        os.remove('sekai.db')
    user_id = create_new_user(0, None)
    print(f"Created user with ID: {user_id}")

    suite_user_data = get_suite_user_data(user_id)
    with open('user_data_dump.json', 'w', encoding='utf-8') as f:
        json.dump(suite_user_data, f, ensure_ascii=False, indent=4)
