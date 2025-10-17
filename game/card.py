import os
import json
import time

class UserCardMixin:
    def add_card(self, card_id: int) -> dict:
        current_time = int(time.time() * 1000)
        card_episode_ids = get_card_episode_ids(card_id)
        
        # 获取用户ID，提供默认值
        user_id = getattr(self, 'userGamedata', {}).get('userId', 0) if hasattr(self, 'userGamedata') else 0
        
        new_card = {
            "userId": user_id,
            "cardId": card_id,
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
            "createdAt": current_time,
            "episodes": [
                {
                    "cardEpisodeId": card_episode_ids[0],
                    "scenarioStatus": "unread_before_scenario",
                    "scenarioStatusReasons": [],
                    "isNotSkipped": False
                },
                {
                    "cardEpisodeId": card_episode_ids[1],
                    "scenarioStatus": "can_not_read",
                    "scenarioStatusReasons": [
                        "unread_before_scenario",
                        "not_enough_release_condition"
                    ],
                    "isNotSkipped": False
                }
            ]
        }
        
        # 添加到用户卡片列表中
        if not hasattr(self, 'userCards'):
            self.userCards = []
        if not any(card['cardId'] == card_id for card in self.userCards):
            self.userCards.append(new_card)
        
        update_refreshable_types = getattr(self, 'update_refreshable_types', None)
        if update_refreshable_types:
            update_refreshable_types('userCards')
            
        return new_card
    

# SELECT id FROM cardEpisodes WHERE cardId=? ORDER BY seq ASC; BUT IN JSON
def get_card_episode_ids(card_id: int) -> list[int]:
    db_path = 'sekai-master-db-diff/cardEpisodes.json'
    if not os.path.exists(db_path):
        raise FileNotFoundError("Card episodes database not found.")
    with open(db_path, 'r', encoding='utf-8') as f:
        card_episodes = json.load(f)
    card_episode_ids = [entry['id'] for entry in card_episodes if entry['cardId'] == card_id]
    # 确保返回至少两个剧情ID
    if len(card_episode_ids) < 2:
        # 如果没有足够的剧情，创建默认值
        while len(card_episode_ids) < 2:
            card_episode_ids.append(0)
    return card_episode_ids


