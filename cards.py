import os
import json
import time
from database import SekaiDatabase

def give_new_card(db: SekaiDatabase, user_id: int, card_id: int) -> set[str]:
    card_episode_ids = get_card_episode_ids(card_id)
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
        "createdAt": int(time.time() * 1000),
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
    db.set_user_cards(user_id, [new_card])
    return {"userCards"}

# SELECT id FROM cardEpisodes WHERE cardId=? ORDER BY seq ASC; BUT IN JSON
def get_card_episode_ids(card_id: int) -> list[int]:
    db_path = 'sekai-master-db-diff/cardEpisodes.json'
    if not os.path.exists(db_path):
        raise FileNotFoundError("Card episodes database not found.")
    with open(db_path, 'r', encoding='utf-8') as f:
        card_episodes = json.load(f)
    card_episode_ids = [entry['id'] for entry in card_episodes if entry['cardId'] == card_id]
    assert isinstance(card_episode_ids, list) and len(card_episode_ids) == 2 and all(isinstance(i, int) for i in card_episode_ids) # TODO: better error handling
    return card_episode_ids
