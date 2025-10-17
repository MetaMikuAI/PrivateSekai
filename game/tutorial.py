import time
from typing import Optional, Callable

class UserTutorialMixin:
    def update_tutorial_progress(self, new_status: str):
        if not hasattr(self, 'userTutorial'):
            return 

        user_tutorial = getattr(self, 'userTutorial', None)
        if not user_tutorial:
            return

        old_status = getattr(user_tutorial, 'tutorialStatus', None)
        user_tutorial.tutorialStatus = new_status

        # 对于阅读完初始剧情的需要做一些初始化任务
        # 0. 修改 tutorialStatus （这是废话，已完成）
        # 1. 发放初始卡牌，一般为 12 张 （已完成）
        # 2. 设定 userDecks （TODO）
        # 3. 设定 userUnitEpisodeStatuses （TODO）

        tutorial_cards_by_unit = {
            'light_sound_opening': [1, 5, 9, 13, 81, 82, 89, 93, 97, 98, 101, 105],
            'idol_opening': [17, 21, 25, 29, 81, 83, 89, 90, 93, 97, 101, 105],
            'street_opening': [33, 37, 41, 45, 81, 84, 89, 93, 94, 97, 102, 105],
            'theme_park_opening': [49, 53, 57, 61, 81, 85, 89, 93, 97, 101, 105, 106],
            'school_refusal_opening': [65, 69, 73, 77, 81, 86, 89, 93, 97, 101, 105]
        }

        update_refreshable_types: Optional[Callable] = getattr(self, 'update_refreshable_types', None)
        assert update_refreshable_types
        

        if old_status in tutorial_cards_by_unit:
            update_refreshable_types('userCards')
            update_refreshable_types('userDecks')
            update_refreshable_types('userUnitEpisodeStatuses')
            card_ids = tutorial_cards_by_unit[old_status]
            for card_id in card_ids:
                add_card = getattr(self, 'add_card', None)
                assert add_card
                add_card(card_id)
            update_refreshable_types('userCharacterMissionV2s')
            update_refreshable_types('userCharacterMissionV2Statuses')
            update_refreshable_types('userBeginnerMissionV2s')
            update_refreshable_types('userMissionStatuses')
            update_refreshable_types('userHonorMissions')

        if new_status == 'end':
            user_tutorial.tutorialEndAt = int(time.time() * 1000)

        user_tutorial = getattr(self, 'userTutorial', None)
        assert user_tutorial

        update_refreshable_types('userTutorial')
