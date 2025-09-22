import sqlite3
from typing import Optional, Any, Dict
import os
import json
import time
from config import logger

class SekaiDatabase:
    def __init__(self, db_path="sekai.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()
        self.connect()

    def init_db(self):
        if os.path.exists(self.db_path):
            return
        sql_path = os.path.join(os.path.dirname(__file__), "init.sql")
        if not os.path.exists(sql_path):
            logger.error(f"init.sql not found: {sql_path}")
            raise FileNotFoundError("init.sql not found")
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(sql_script)
            logger.info(f"Database initialized from {sql_path}")
        finally:
            conn.close()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def get_user_registration(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, signature, platform, device_model, operating_system, registered_at 
            FROM 
                user_registration 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "userId": row["user_id"],
                "signature": row["signature"],
                "platform": row["platform"],
                "deviceModel": row["device_model"],
                "operatingSystem": row["operating_system"],
                "registeredAt": row["registered_at"]
            }
        return None

    def set_user_registration(self, user_id: int, data: Dict[str, Any]) -> None:
        """设置用户注册信息"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_registration 
            (user_id, signature, platform, device_model, operating_system) 
            VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql, (
            user_id, 
            data["signature"], 
            data["platform"], 
            data["deviceModel"], 
            data["operatingSystem"]
        ))
        self.conn.commit()
    
    def update_user_device_info(self, user_id: int, device_info: Dict[str, Any]) -> None:
        """更新用户设备信息"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            UPDATE user_registration 
            SET platform=?, device_model=?, operating_system=? 
            WHERE user_id=?
        """
        cur.execute(sql, (
            device_info.get("platform", ""),
            device_info.get("deviceModel", ""),
            device_info.get("operatingSystem", ""),
            user_id
        ))
        self.conn.commit()

    def get_user_gamedata(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, name, deck, rank, exp, total_exp, coin, virtual_coin 
            FROM 
                user_gamedata 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "userId": row["user_id"],
                "name": row["name"],
                "deck": row["deck"],
                "rank": row["rank"],
                "exp": row["exp"],
                "totalExp": row["total_exp"],
                "coin": row["coin"],
                "virtualCoin": row["virtual_coin"]
            }
        return None

    def set_user_gamedata(self, user_id: int, data: Dict[str, Any]) -> None:
        """设置用户游戏数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_gamedata 
            (user_id, name, deck, rank, exp, total_exp, coin, virtual_coin) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (
            user_id, 
            data["name"], 
            data["deck"], 
            data["rank"], 
            data["exp"], 
            data["totalExp"], 
            data["coin"], 
            data["virtualCoin"]
        ))
        self.conn.commit()

    def get_user_charged_currency(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                paid, free 
            FROM 
                user_charged_currency 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "paid": row["paid"],
                "free": row["free"],
                "paidUnitPrices": []  # TODO: 可能需要扩展
            }
        return None

    def set_user_charged_currency(self, user_id: int, data: Dict[str, Any]) -> None:
        """设置用户付费货币数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_charged_currency 
            (user_id, paid, free) 
            VALUES (?, ?, ?)
        """
        cur.execute(sql, (user_id, data["paid"], data["free"]))
        self.conn.commit()

    def get_user_boost(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                current, recovery_at 
            FROM 
                user_boost 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "current": row["current"],
                "recoveryAt": row["recovery_at"]
            }
        return None

    def set_user_boost(self, user_id: int, data: Dict[str, Any]) -> None:
        """设置用户体力数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_boost 
            (user_id, current) 
            VALUES (?, ?)
        """
        cur.execute(sql, (user_id, data["current"], ))
        self.conn.commit()

    def get_user_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                default_music_type, is_display_login_status, friend_request_scope 
            FROM 
                user_config 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "defaultMusicType": row["default_music_type"],
                "isDisplayLoginStatus": bool(row["is_display_login_status"]),
                "friendRequestScope": row["friend_request_scope"]
            }
        return None

    def set_user_config(self, user_id: int, data: Dict[str, Any]) -> None:
        """设置用户配置"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 使用REPLACE来插入或更新记录
        sql = """
            REPLACE INTO user_config 
            (user_id, default_music_type, is_display_login_status, friend_request_scope) 
            VALUES (?, ?, ?, ?)
        """
        cur.execute(sql, (
            user_id, 
            data["defaultMusicType"], 
            int(data["isDisplayLoginStatus"]), 
            data["friendRequestScope"]
        ))
        self.conn.commit()

    def get_user_tutorial(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        sql = """
            SELECT 
                tutorial_status 
            FROM 
                user_tutorial 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "tutorialStatus": row["tutorial_status"]
            }
        return None

    def set_user_tutorial(self, user_id: int, data: Dict[str, Any]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_tutorial 
            (user_id, tutorial_status) 
            VALUES (?, ?)
        """
        cur.execute(sql, (user_id, data["tutorialStatus"]))
        self.conn.commit()

    def get_user_areas(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户所有区域数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        # 获取用户所有区域状态
        sql = """
            SELECT 
                area_id, status 
            FROM 
                user_area_status 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        area_statuses = cur.fetchall()

        # 获取用户所有区域播放列表状态
        sql = """
            SELECT 
                area_id, area_playlist_id, status 
            FROM 
                user_area_playlist_status 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        playlist_statuses = cur.fetchall()
        
        # 构建播放列表状态字典
        playlist_dict = {}
        for row in playlist_statuses:
            area_id = row["area_id"]
            playlist_dict[area_id] = {
                "areaPlaylistId": row["area_playlist_id"],
                "status": row["status"]
            }
        
        # 构建最终结果
        user_areas = []
        for row in area_statuses:
            area_id = row["area_id"]
            area_data = {
                "areaId": area_id,
                "actionSets": [],
                "areaItems": [],
                "userAreaStatus": {
                    "areaId": area_id,
                    "status": row["status"]
                }
            }
            
            # 如果有播放列表状态，添加到 userAreaStatus 中
            if area_id in playlist_dict:
                area_data["userAreaStatus"]["userAreaPlaylistStatus"] = playlist_dict[area_id]
            
            user_areas.append(area_data)
        
        return user_areas

    def set_user_areas(self, user_id: int, areas_data: list[Dict[str, Any]]) -> None:
        """设置用户区域数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 清除现有数据
        sql = "DELETE FROM user_area_status WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        sql = "DELETE FROM user_area_playlist_status WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for area in areas_data:
            area_id = area["areaId"]
            area_status = area["userAreaStatus"]
            
            sql = "REPLACE INTO user_area_status (user_id, area_id, status) VALUES (?, ?, ?)"
            cur.execute(sql, (user_id, area_id, area_status["status"]))
            
            # 如果有播放列表状态，插入播放列表状态
            if "userAreaPlaylistStatus" in area_status:
                playlist_status = area_status["userAreaPlaylistStatus"]
                sql = """
                    REPLACE INTO user_area_playlist_status 
                    (user_id, area_id, area_playlist_id, status) 
                    VALUES (?, ?, ?, ?)
                """
                cur.execute(sql, (user_id, area_id, playlist_status["areaPlaylistId"], playlist_status["status"]))
        
        self.conn.commit()

    def get_user_action_sets(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_action_sets(self, user_id: int, action_sets: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_cards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户所有卡片数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        # 获取用户所有卡片数据
        sql = """
            SELECT 
                user_id, card_id, level, exp, total_exp, skill_level, skill_exp, 
                total_skill_exp, master_rank, special_training_status, default_image, 
                duplicate_count, created_at
            FROM 
                user_cards 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        cards = cur.fetchall()

        # 获取用户所有卡片剧情数据
        sql = """
            SELECT 
                card_id, card_episode_id, scenario_status, scenario_status_reasons, is_not_skipped
            FROM 
                user_card_episodes 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        episodes = cur.fetchall()
        
        # 按card_id分组剧情数据
        episodes_dict = {}
        for episode in episodes:
            card_id = episode["card_id"]
            if card_id not in episodes_dict:
                episodes_dict[card_id] = []
            
            # 解析scenario_status_reasons JSON字符串
            import json
            try:
                reasons = json.loads(episode["scenario_status_reasons"])
            except (json.JSONDecodeError, TypeError):
                reasons = []
            
            episodes_dict[card_id].append({
                "cardEpisodeId": episode["card_episode_id"],
                "scenarioStatus": episode["scenario_status"],
                "scenarioStatusReasons": reasons,
                "isNotSkipped": bool(episode["is_not_skipped"])
            })
        
        # 构建最终结果
        user_cards = []
        for card in cards:
            card_id = card["card_id"]
            card_data = {
                "userId": card["user_id"],
                "cardId": card_id,
                "level": card["level"],
                "exp": card["exp"],
                "totalExp": card["total_exp"],
                "skillLevel": card["skill_level"],
                "skillExp": card["skill_exp"],
                "totalSkillExp": card["total_skill_exp"],
                "masterRank": card["master_rank"],
                "specialTrainingStatus": card["special_training_status"],
                "defaultImage": card["default_image"],
                "duplicateCount": card["duplicate_count"],
                "createdAt": card["created_at"],
                "episodes": episodes_dict.get(card_id, [])
            }
            user_cards.append(card_data)
        
        return user_cards

    def set_user_cards(self, user_id: int, cards_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_card_episodes WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        sql = "DELETE FROM user_cards WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for card in cards_data:
            # 插入卡片主数据
            sql = """
                REPLACE INTO user_cards 
                (user_id, card_id, level, exp, total_exp, skill_level, skill_exp, 
                 total_skill_exp, master_rank, special_training_status, default_image, 
                 duplicate_count) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                card["cardId"],
                card["level"],
                card["exp"],
                card["totalExp"],
                card["skillLevel"],
                card["skillExp"],
                card["totalSkillExp"],
                card["masterRank"],
                card["specialTrainingStatus"],
                card["defaultImage"],
                card["duplicateCount"]
            ))
            
            for episode in card.get("episodes", []):
                sql = """
                    REPLACE INTO user_card_episodes 
                    (user_id, card_id, card_episode_id, scenario_status, scenario_status_reasons, is_not_skipped) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cur.execute(sql, (
                    user_id,
                    card["cardId"],
                    episode["cardEpisodeId"],
                    episode["scenarioStatus"],
                    json.dumps(episode.get("scenarioStatusReasons", [])),
                    int(episode["isNotSkipped"])
                ))
        
        self.conn.commit()

    def get_user_decks(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        sql = """
            SELECT 
                user_id, deck_id, name, leader, sub_leader, member1, member2, member3, member4, member5
            FROM 
                user_decks 
            WHERE 
                user_id=?
        """
        cur.execute(sql, (user_id,))
        decks = cur.fetchall()
        
        user_decks = []
        for deck in decks:
            deck_data = {
                "userId": deck["user_id"],
                "deckId": deck["deck_id"],
                "name": deck["name"],
                "leader": deck["leader"],
                "subLeader": deck["sub_leader"],
                "member1": deck["member1"],
                "member2": deck["member2"],
                "member3": deck["member3"],
                "member4": deck["member4"],
                "member5": deck["member5"]
            }
            user_decks.append(deck_data)
        
        return user_decks

    def set_user_decks(self, user_id: int, decks_data: list[Dict[str, Any]]) -> None:
        """设置用户卡组数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_decks WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for deck in decks_data:
            sql = """
                REPLACE INTO user_decks 
                (user_id, deck_id, name, leader, sub_leader, member1, member2, member3, member4, member5) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                deck["deckId"],
                deck["name"],
                deck["leader"],
                deck["subLeader"],
                deck["member1"],
                deck["member2"],
                deck["member3"],
                deck["member4"],
                deck["member5"]
            ))
        
        self.conn.commit()

    def get_user_musics(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        sql = """
            SELECT 
                music_id
            FROM 
                user_musics 
            WHERE 
                user_id=?
            ORDER BY 
                music_id
        """
        cur.execute(sql, (user_id,))
        musics = cur.fetchall()
        
        user_musics = []
        for music in musics:
            music_data = {
                "musicId": music["music_id"]
            }
            user_musics.append(music_data)
        
        return user_musics

    def set_user_musics(self, user_id: int, musics_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_musics WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for music in musics_data:
            sql = """
                REPLACE INTO user_musics 
                (user_id, music_id) 
                VALUES (?, ?)
            """
            cur.execute(sql, (user_id, music["musicId"]))
        
        self.conn.commit()

    def get_user_music_vocals(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        sql = """
            SELECT 
                music_id, music_vocal_id
            FROM 
                user_music_vocals 
            WHERE 
                user_id=?
            ORDER BY 
                music_vocal_id
        """
        cur.execute(sql, (user_id,))
        vocals = cur.fetchall()
        
        user_music_vocals = []
        for vocal in vocals:
            vocal_data = {
                "musicId": vocal["music_id"],
                "musicVocalId": vocal["music_vocal_id"]
            }
            user_music_vocals.append(vocal_data)
        
        return user_music_vocals

    def set_user_music_vocals(self, user_id: int, vocals_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_music_vocals WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for vocal in vocals_data:
            sql = """
                REPLACE INTO user_music_vocals 
                (user_id, music_id, music_vocal_id) 
                VALUES (?, ?, ?)
            """
            cur.execute(sql, (user_id, vocal["musicId"], vocal["musicVocalId"]))
        
        self.conn.commit()

    def get_user_music_results(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO

    def set_user_music_results(self, user_id: int, results_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_music_achievements(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO

    def set_user_music_achievements(self, user_id: int, achievements_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_shops(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        sql = """
            SELECT 
                shop_id
            FROM 
                user_shops 
            WHERE 
                user_id=?
            ORDER BY 
                shop_id
        """
        cur.execute(sql, (user_id,))
        shops = cur.fetchall()

        sql = """
            SELECT 
                shop_id, shop_item_id, level, status
            FROM 
                user_shop_items 
            WHERE 
                user_id=?
            ORDER BY 
                shop_id, shop_item_id
        """
        cur.execute(sql, (user_id,))
        shop_items = cur.fetchall()
        
        items_dict = {}
        for item in shop_items:
            shop_id = item["shop_id"]
            if shop_id not in items_dict:
                items_dict[shop_id] = []
            
            item_data: dict[str, Any] = {} # 这里不用 {} 直接构造是为了与原 json 形式一样，当然作用没有实际差别
            item_data["shopItemId"] = item["shop_item_id"]
            if item["level"] is not None:
                item_data["level"] = item["level"]
            item_data["status"] = item["status"]
            
            
            items_dict[shop_id].append(item_data)
        
        user_shops = []
        for shop in shops:
            shop_id = shop["shop_id"]
            shop_data = {
                "shopId": shop_id,
                "userShopItems": items_dict.get(shop_id, [])
            }
            user_shops.append(shop_data)
        
        return user_shops

    def set_user_shops(self, user_id: int, shops_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_shop_items WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        sql = "DELETE FROM user_shops WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for shop in shops_data:
            shop_id = shop["shopId"]
            
            sql = """
                REPLACE INTO user_shops 
                (user_id, shop_id) 
                VALUES (?, ?)
            """
            cur.execute(sql, (user_id, shop_id))
            
            for item in shop.get("userShopItems", []):
                sql = """
                    REPLACE INTO user_shop_items 
                    (user_id, shop_id, shop_item_id, level, status) 
                    VALUES (?, ?, ?, ?, ?)
                """
                level = item.get("level")
                cur.execute(sql, (
                    user_id,
                    shop_id,
                    item["shopItemId"],
                    level,
                    item["status"]
                ))
        
        self.conn.commit()

    def get_user_billing_shop_items(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                billing_shop_item_id, count, total_count, status
            FROM 
                user_billing_shop_items 
            WHERE 
                user_id=? 
            ORDER BY 
                billing_shop_item_id
        """
        cur.execute(sql, (user_id,))
        items = cur.fetchall()
        
        return [
            {
                "billingShopItemId": item["billing_shop_item_id"],
                "count": item["count"],
                "totalCount": item["total_count"],
                "status": item["status"]
            }
            for item in items
        ]

    def set_user_billing_shop_items(self, user_id: int, items_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_billing_shop_items WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for item in items_data:
            sql = """
                REPLACE INTO user_billing_shop_items 
                (user_id, billing_shop_item_id, count, total_count, status) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                item["billingShopItemId"],
                item["count"],
                item["totalCount"],
                item["status"]
            ))
        
        self.conn.commit()
    
    def get_user_colorful_pass(self, user_id: int) -> Optional[Dict[str, Any]]:
        return {} # TODO
    
    def set_user_colorful_pass(self, user_id: int, colorful_pass_data: Dict[str, Any]) -> None:
        pass # TODO

    def get_user_colorful_pass_v2(self, user_id: int) -> Optional[Dict[str, Any]]:
        return {} # TODO
    
    def set_user_colorful_pass_v2(self, user_id: int, colorful_pass_v2_data: Dict[str, Any]) -> None:
        pass # TODO
    
    def get_user_practice_tickets(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_practice_tickets(self, user_id: int, tickets_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_skill_practice_tickets(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_skill_practice_tickets(self, user_id: int, tickets_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_materials(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_materials(self, user_id: int, materials_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_gachas(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_gachas(self, user_id: int, gachas_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_gacha_bonus_points(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_gacha_bonus_points(self, user_id: int, points_data: list[Dict[str, Any]]) -> None:
        pass # TODO



    def get_user_unit_episode_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                story_type, episode_id, status, is_not_skipped
            FROM 
                user_unit_episode_statuses 
            WHERE 
                user_id=? 
            ORDER BY 
                story_type, episode_id
        """
        cur.execute(sql, (user_id,))
        episodes = cur.fetchall()
        
        return [
            {
                "storyType": episode["story_type"],
                "episodeId": episode["episode_id"],
                "status": episode["status"],
                "isNotSkipped": bool(episode["is_not_skipped"])
            }
            for episode in episodes
        ]

    def set_user_unit_episode_statuses(self, user_id: int, episodes_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_unit_episode_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for episode in episodes_data:
            sql = """
                REPLACE INTO user_unit_episode_statuses 
                (user_id, story_type, episode_id, status, is_not_skipped) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                episode["storyType"],
                episode["episodeId"],
                episode["status"],
                int(episode["isNotSkipped"])
            ))
        
        self.conn.commit()


    def get_user_special_episode_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                story_type, episode_id, status, is_not_skipped
            FROM 
                user_special_episode_statuses 
            WHERE 
                user_id=? 
            ORDER BY 
                story_type, episode_id
        """
        cur.execute(sql, (user_id,))
        episodes = cur.fetchall()
        
        return [
            {
                "storyType": episode["story_type"],
                "episodeId": episode["episode_id"],
                "status": episode["status"],
                "isNotSkipped": bool(episode["is_not_skipped"])
            }
            for episode in episodes
        ]
    
    def set_user_special_episode_statuses(self, user_id: int, episodes_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_special_episode_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for episode in episodes_data:
            sql = """
                REPLACE INTO user_special_episode_statuses 
                (user_id, story_type, episode_id, status, is_not_skipped) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                episode["storyType"],
                episode["episodeId"],
                episode["status"],
                int(episode["isNotSkipped"])
            ))
        
        self.conn.commit()
    
    def get_user_event_episode_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户活动剧集状态"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                story_type, episode_id, status, is_not_skipped
            FROM 
                user_event_episode_statuses 
            WHERE 
                user_id=? 
            ORDER BY 
                story_type, episode_id
        """
        cur.execute(sql, (user_id,))
        episodes = cur.fetchall()
        
        return [
            {
                "storyType": episode["story_type"],
                "episodeId": episode["episode_id"],
                "status": episode["status"],
                "isNotSkipped": bool(episode["is_not_skipped"])
            }
            for episode in episodes
        ]

    def set_user_event_episode_statuses(self, user_id: int, episodes_data: list[Dict[str, Any]]) -> None:
        """设置用户活动剧集状态"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_event_episode_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for episode in episodes_data:
            sql = """
                REPLACE INTO user_event_episode_statuses 
                (user_id, story_type, episode_id, status, is_not_skipped) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                episode["storyType"],
                episode["episodeId"],
                episode["status"],
                int(episode["isNotSkipped"])
            ))
        
        self.conn.commit()

    def get_user_archive_event_episode_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户归档活动剧集状态"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                story_type, episode_id, status, is_not_skipped
            FROM 
                user_archive_event_episode_statuses 
            WHERE 
                user_id=? 
            ORDER BY 
                story_type, episode_id
        """
        cur.execute(sql, (user_id,))
        episodes = cur.fetchall()
        
        return [
            {
                "storyType": episode["story_type"],
                "episodeId": episode["episode_id"],
                "status": episode["status"],
                "isNotSkipped": bool(episode["is_not_skipped"])
            }
            for episode in episodes
        ]

    def set_user_archive_event_episode_statuses(self, user_id: int, episodes_data: list[Dict[str, Any]]) -> None:
        """设置用户归档活动剧集状态"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_archive_event_episode_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for episode in episodes_data:
            sql = """
                REPLACE INTO user_archive_event_episode_statuses 
                (user_id, story_type, episode_id, status, is_not_skipped) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                episode["storyType"],
                episode["episodeId"],
                episode["status"],
                int(episode["isNotSkipped"])
            ))
        
        self.conn.commit()
    
    def get_user_character_profile_episode_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户角色档案剧集状态"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        cur.execute("""
            SELECT story_type, episode_id, status, is_not_skipped
            FROM user_character_profile_episode_statuses
            WHERE user_id = ?
            ORDER BY episode_id
        """, (user_id,))
        
        episodes = []
        for episode in cur.fetchall():
            episodes.append({
                "storyType": episode["story_type"],
                "episodeId": episode["episode_id"],
                "status": episode["status"],
                "isNotSkipped": bool(episode["is_not_skipped"])
            })
        
        return episodes

    def set_user_character_profile_episode_statuses(self, user_id: int, episodes_data: list[Dict[str, Any]]) -> None:
        """设置用户角色档案剧集状态"""
        if self.conn is None:
            return
            
        cur = self.conn.cursor()
        
        # 先删除现有数据
        cur.execute("DELETE FROM user_character_profile_episode_statuses WHERE user_id = ?", (user_id,))
        
        # 插入新数据
        for episode in episodes_data:
            cur.execute("""
                REPLACE INTO user_character_profile_episode_statuses 
                (user_id, story_type, episode_id, status, is_not_skipped)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                episode.get("storyType", "character_profile_story"),
                episode["episodeId"],
                episode.get("status", "unreleased"),
                episode.get("isNotSkipped", False)
            ))
        
        self.conn.commit()

    def get_user_story_mission(self, user_id: int) -> Optional[Dict[str, Any]]:
        return {"progress": 0} # TODO
    
    def set_user_story_mission(self, user_id: int, story_mission_data: Dict[str, Any]) -> None:
        pass # TODO
    
    def get_user_event_archive_complete_read_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                event_story_id, is_display_event_archive_complete_read_progress
            FROM 
                user_event_archive_complete_read_rewards 
            WHERE 
                user_id=? 
            ORDER BY 
                event_story_id
        """
        cur.execute(sql, (user_id,))
        rewards = cur.fetchall()
        
        return [
            {
                "eventStoryId": reward["event_story_id"],
                "isDisplayEventArchiveCompleteReadProgress": bool(reward["is_display_event_archive_complete_read_progress"])
            }
            for reward in rewards
        ]
    
    def set_user_event_archive_complete_read_rewards(self, user_id: int, rewards_data: list[Dict[str, Any]]) -> None:
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        sql = "DELETE FROM user_event_archive_complete_read_rewards WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        for reward in rewards_data:
            sql = """
                REPLACE INTO user_event_archive_complete_read_rewards 
                (user_id, event_story_id, is_display_event_archive_complete_read_progress) 
                VALUES (?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                reward["eventStoryId"],
                int(reward["isDisplayEventArchiveCompleteReadProgress"])
            ))
        
        self.conn.commit()

    def get_user_units(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户单元数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, unit, rank, exp, total_exp
            FROM 
                user_units 
            WHERE 
                user_id=? 
            ORDER BY 
                unit
        """
        cur.execute(sql, (user_id,))
        units = cur.fetchall()
        
        return [
            {
                "userId": unit["user_id"],
                "unit": unit["unit"],
                "rank": unit["rank"],
                "exp": unit["exp"],
                "totalExp": unit["total_exp"]
            }
            for unit in units
        ]

    def set_user_units(self, user_id: int, units_data: list[Dict[str, Any]]) -> None:
        """设置用户单元数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_units WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for unit in units_data:
            sql = """
                REPLACE INTO user_units 
                (user_id, unit, rank, exp, total_exp) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                unit["unit"],
                unit["rank"],
                unit["exp"],
                unit["totalExp"]
            ))
        
        self.conn.commit()

    def get_user_presents(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户礼品数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                present_id, seq, resource_type, resource_id, resource_quantity, reason, granted_at
            FROM 
                user_presents 
            WHERE 
                user_id=? 
            ORDER BY 
                seq DESC, granted_at DESC
        """
        cur.execute(sql, (user_id,))
        presents = cur.fetchall()

        return [
            {
                "presentId": present["present_id"],
                "seq": present["seq"],
                "resourceType": present["resource_type"],
                **({"resourceId": present["resource_id"]} if present["resource_id"] is not None else {}), # 可选字段
                "resourceQuantity": present["resource_quantity"],
                "reason": present["reason"],
                "grantedAt": present["granted_at"]
            }
            for present in presents
        ]

    def set_user_presents(self, user_id: int, presents_data: list[Dict[str, Any]]) -> None:
        """设置用户礼品数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_presents WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for present in presents_data:
            sql = """
                REPLACE INTO user_presents 
                (user_id, present_id, seq, resource_type, resource_id, resource_quantity, reason) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                present["presentId"],
                present["seq"],
                present["resourceType"],
                present.get("resourceId"),
                present["resourceQuantity"],
                present["reason"]
            ))
        
        self.conn.commit()

    def get_user_costume_3d_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户3D服装状态数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                costume_3d_id, obtained_at, status
            FROM 
                user_costume_3d_statuses 
            WHERE 
                user_id=? 
            ORDER BY 
                costume_3d_id
        """
        cur.execute(sql, (user_id,))
        costumes = cur.fetchall()
        
        result = []
        for costume in costumes:
            costume_data = {
                "costume3dId": costume["costume_3d_id"],
                **({"obtainedAt": costume["obtained_at"]} if costume["obtained_at"] is not None else {}), # 可选字段
                "status": costume["status"]
            }
            result.append(costume_data)
        
        return result

    def set_user_costume_3d_statuses(self, user_id: int, costumes_data: list[Dict[str, Any]]) -> None:
        """设置用户3D服装状态数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_costume_3d_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for costume in costumes_data:
            sql = """
                REPLACE INTO user_costume_3d_statuses 
                (user_id, costume_3d_id, obtained_at, status) 
                VALUES (?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                costume["costume3dId"],
                int(time.time() * 1000) if costume.get("obtainedAt") else None,
                costume["status"]
            ))
        
        self.conn.commit()

    def get_user_costume_3d_shop_items(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户3D服装商店物品数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                costume_3d_shop_item_id, status
            FROM 
                user_costume_3d_shop_items 
            WHERE 
                user_id=? 
            ORDER BY 
                costume_3d_shop_item_id
        """
        cur.execute(sql, (user_id,))
        shop_items = cur.fetchall()
        
        return [
            {
                "costume3dShopItemId": item["costume_3d_shop_item_id"],
                "status": item["status"]
            }
            for item in shop_items
        ]

    def set_user_costume_3d_shop_items(self, user_id: int, shop_items_data: list[Dict[str, Any]]) -> None:
        """设置用户3D服装商店物品数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_costume_3d_shop_items WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for item in shop_items_data:
            sql = """
                REPLACE INTO user_costume_3d_shop_items 
                (user_id, costume_3d_shop_item_id, status) 
                VALUES (?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                item["costume3dShopItemId"],
                item["status"]
            ))
        
        self.conn.commit()

    def get_user_character_costume_3ds(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户角色3D服装配置数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                character_id, unit, head_costume_3d_id, hair_costume_3d_id, body_costume_3d_id
            FROM 
                user_character_costume_3ds 
            WHERE 
                user_id=? 
            ORDER BY 
                character_id
        """
        cur.execute(sql, (user_id,))
        costumes = cur.fetchall()
        
        return [
            {
                "characterId": costume["character_id"],
                "unit": costume["unit"],
                "headCostume3dId": costume["head_costume_3d_id"],
                "hairCostume3dId": costume["hair_costume_3d_id"],
                "bodyCostume3dId": costume["body_costume_3d_id"]
            }
            for costume in costumes
        ]

    def set_user_character_costume_3ds(self, user_id: int, costumes_data: list[Dict[str, Any]]) -> None:
        """设置用户角色3D服装配置数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_character_costume_3ds WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for costume in costumes_data:
            sql = """
                REPLACE INTO user_character_costume_3ds 
                (user_id, character_id, unit, head_costume_3d_id, hair_costume_3d_id, body_costume_3d_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                costume["characterId"],
                costume["unit"],
                costume["headCostume3dId"],
                costume["hairCostume3dId"],
                costume["bodyCostume3dId"]
            ))
        
        self.conn.commit()

    def get_user_release_conditions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户解锁条件数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                release_condition_id, created_at
            FROM 
                user_release_conditions 
            WHERE 
                user_id=? 
            ORDER BY 
                release_condition_id
        """
        cur.execute(sql, (user_id,))
        conditions = cur.fetchall()
        
        return [
            {
                "releaseConditionId": condition["release_condition_id"],
                "createdAt": condition["created_at"]
            }
            for condition in conditions
        ]

    def set_user_release_conditions(self, user_id: int, conditions_data: list[Dict[str, Any]]) -> None:
        """设置用户解锁条件数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_release_conditions WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for condition in conditions_data:
            sql = """
                REPLACE INTO user_release_conditions 
                (user_id, release_condition_id) 
                VALUES (?, ?)
            """
            cur.execute(sql, (
                user_id,
                condition["releaseConditionId"]
            ))
        
        self.conn.commit()

    def get_unread_user_topics(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户未读话题数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, topic_id, topic_status
            FROM 
                unread_user_topics 
            WHERE 
                user_id=? 
            ORDER BY 
                topic_id
        """
        cur.execute(sql, (user_id,))
        topics = cur.fetchall()
        
        return [
            {
                "userId": topic["user_id"],
                "topicId": topic["topic_id"],
                "topicStatus": topic["topic_status"]
            }
            for topic in topics
        ]

    def set_unread_user_topics(self, user_id: int, topics_data: list[Dict[str, Any]]) -> None:
        """设置用户未读话题数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM unread_user_topics WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for topic in topics_data:
            sql = """
                REPLACE INTO unread_user_topics 
                (user_id, topic_id, topic_status) 
                VALUES (?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                topic["topicId"],
                topic["topicStatus"]
            ))
        
        self.conn.commit()

    def get_user_home_banners(self, user_id: int) -> list[Dict[str, Any]]:
        """获取首页横幅数据（全局信息）"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                home_banner_id, seq, home_banner_type, name, assetbundle_name,
                transition_destination_type, transition_destination_id, 
                start_at, end_at, url
            FROM 
                home_banners 
            ORDER BY 
                home_banner_id
        """
        cur.execute(sql)
        banners = cur.fetchall()
        
        result = []
        for banner in banners:
            banner_data = {
                "homeBannerId": banner["home_banner_id"],
                "seq": banner["seq"],
                "homeBannerType": banner["home_banner_type"],
                "name": banner["name"],
                "assetbundleName": banner["assetbundle_name"],
                "transitionDestinationType": banner["transition_destination_type"],
                **({"transitionDestinationId": banner["transition_destination_id"]} if banner["transition_destination_id"] is not None else {}), # 可选字段
                "startAt": banner["start_at"],
                "endAt": banner["end_at"],
                **({"url": banner["url"]} if banner["url"] is not None else {})  # 可选字段
            }
            
            result.append(banner_data)
        
        return result

    def set_user_home_banners(self, banners_data: list[Dict[str, Any]]) -> None:
        """设置首页横幅数据（全局信息）"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM home_banners"
        cur.execute(sql)
        
        # 插入新数据
        for banner in banners_data:
            sql = """
                REPLACE INTO home_banners 
                (home_banner_id, seq, home_banner_type, name, assetbundle_name,
                 transition_destination_type, transition_destination_id, 
                 start_at, end_at, url) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                banner["homeBannerId"],
                banner["seq"],
                banner["homeBannerType"],
                banner["name"],
                banner["assetbundleName"],
                banner["transitionDestinationType"],
                banner.get("transitionDestinationId"),  # 可选字段
                banner["startAt"],
                banner["endAt"],
                banner.get("url")  # 可选字段
            ))
        
        self.conn.commit()

    def get_user_stamps(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户印章数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                stamp_id, obtained_at
            FROM 
                user_stamps 
            WHERE 
                user_id=? 
            ORDER BY 
                stamp_id
        """
        cur.execute(sql, (user_id,))
        stamps = cur.fetchall()
        
        return [
            {
                "stampId": stamp["stamp_id"],
                "obtainedAt": stamp["obtained_at"]
            }
            for stamp in stamps
        ]

    def set_user_stamps(self, user_id: int, stamps_data: list[Dict[str, Any]]) -> None:
        """设置用户印章数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_stamps WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for stamp in stamps_data:
            sql = """
                REPLACE INTO user_stamps 
                (user_id, stamp_id) 
                VALUES (?, ?)
            """
            cur.execute(sql, (
                user_id,
                stamp["stampId"]
            ))
        
        self.conn.commit()

    def get_user_stamp_favorites(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_stamp_favorites(self, user_id: int, favorites_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_stamp_favorite_tabs(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_stamp_favorite_tabs(self, user_id: int, tabs_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_material_exchanges(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户材料兑换数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, material_exchange_id, exchange_count, total_exchange_count, exchange_status, exchange_remaining, refreshed_at
            FROM 
                user_material_exchanges 
            WHERE 
                user_id=? 
            ORDER BY 
                material_exchange_id
        """
        cur.execute(sql, (user_id,))
        exchanges = cur.fetchall()
        
        return [
            {
                "userId": exchange["user_id"],
                "materialExchangeId": exchange["material_exchange_id"],
                "exchangeCount": exchange["exchange_count"],
                "totalExchangeCount": exchange["total_exchange_count"],
                "exchangeStatus": exchange["exchange_status"],
                **({"exchangeRemaining": exchange["exchange_remaining"]} if exchange["exchange_remaining"] is not None else {}), # 可选字段
                **({"refreshedAt": exchange["refreshed_at"]} if exchange["refreshed_at"] is not None else {})  # 可选字段
            }
            for exchange in exchanges
        ]

    def set_user_material_exchanges(self, user_id: int, exchanges_data: list[Dict[str, Any]]) -> None:
        """设置用户材料兑换数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_material_exchanges WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for exchange in exchanges_data:
            sql = """
                REPLACE INTO user_material_exchanges 
                (user_id, material_exchange_id, exchange_count, total_exchange_count, exchange_status, exchange_remaining, refreshed_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                exchange["materialExchangeId"],
                exchange["exchangeCount"],
                exchange["totalExchangeCount"],
                exchange["exchangeStatus"],
                exchange.get("exchangeRemaining"),  # 可选字段
                exchange.get("refreshedAt")  # 可选字段
            ))
        
        self.conn.commit()

    def get_user_gacha_ceil_exchanges(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户扭蛋保底兑换数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                user_id, gacha_ceil_exchange_id, exchange_status, exchange_remaining
            FROM 
                user_gacha_ceil_exchanges 
            WHERE 
                user_id=? 
            ORDER BY 
                gacha_ceil_exchange_id
        """
        cur.execute(sql, (user_id,))
        exchanges = cur.fetchall()
        
        result = []
        for exchange in exchanges:
            exchange_data = {
                "userId": exchange["user_id"],
                "gachaCeilExchangeId": exchange["gacha_ceil_exchange_id"],
                "exchangeStatus": exchange["exchange_status"]
            }
            
            # 可选字段
            if exchange["exchange_remaining"] is not None:
                exchange_data["exchangeRemaining"] = exchange["exchange_remaining"]
                
            result.append(exchange_data)
        
        return result

    def set_user_gacha_ceil_exchanges(self, user_id: int, exchanges_data: list[Dict[str, Any]]) -> None:
        """设置用户扭蛋保底兑换数据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_gacha_ceil_exchanges WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for exchange in exchanges_data:
            sql = """
                REPLACE INTO user_gacha_ceil_exchanges 
                (user_id, gacha_ceil_exchange_id, exchange_status, exchange_remaining) 
                VALUES (?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                exchange["gachaCeilExchangeId"],
                exchange["exchangeStatus"],
                exchange.get("exchangeRemaining")  # 可选字段
            ))
        
        self.conn.commit()

    def get_user_gacha_ceil_items(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO

    def set_user_gacha_ceil_items(self, user_id: int, items_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_gacha_tickets(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_gacha_tickets(self, user_id: int, tickets_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_boost_items(self, user_id: int) -> list[Dict[str, Any]]:
        return [] # TODO
    
    def set_user_boost_items(self, user_id: int, items_data: list[Dict[str, Any]]) -> None:
        pass # TODO

    def get_user_characters(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户所有角色数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                character_id, character_rank, exp, total_exp
            FROM 
                user_characters 
            WHERE 
                user_id=?
            ORDER BY 
                character_id
        """
        cur.execute(sql, (user_id,))
        characters = cur.fetchall()
        
        return [
            {
                "characterId": character["character_id"],
                "characterRank": character["character_rank"],
                "exp": character["exp"],
                "totalExp": character["total_exp"]
            }
            for character in characters
        ]

    def set_user_characters(self, user_id: int, characters_data: list[Dict[str, Any]]) -> None:
        """设置用户角色数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return
        
        cur = self.conn.cursor()
        
        # 清除现有数据
        sql = "DELETE FROM user_characters WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for character in characters_data:
            sql = """
                REPLACE INTO user_characters 
                (user_id, character_id, character_rank, exp, total_exp) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                character["characterId"],
                character["characterRank"],
                character["exp"],
                character["totalExp"]
            ))
        
        self.conn.commit()

    def get_user_character_mission_v2s(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户所有角色任务V2数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                character_mission_type, character_id, progress, achieved_missions
            FROM 
                user_character_mission_v2s 
            WHERE 
                user_id=?
            ORDER BY 
                character_mission_type, character_id
        """
        cur.execute(sql, (user_id,))
        missions = cur.fetchall()
        
        return [
            {
                "characterMissionType": mission["character_mission_type"],
                "characterId": mission["character_id"],
                "progress": mission["progress"],
                "achievedMissions": json.loads(mission["achieved_missions"])
            }
            for mission in missions
        ]

    def set_user_character_mission_v2s(self, user_id: int, missions_data: list[Dict[str, Any]]) -> None:
        """设置用户角色任务V2数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return
        
        cur = self.conn.cursor()
        
        # 清除现有数据
        sql = "DELETE FROM user_character_mission_v2s WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for mission in missions_data:
            sql = """
                REPLACE INTO user_character_mission_v2s 
                (user_id, character_mission_type, character_id, progress, achieved_missions) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                mission["characterMissionType"],
                mission["characterId"],
                mission["progress"],
                json.dumps(mission["achievedMissions"])
            ))
        
        self.conn.commit()

    def get_user_character_mission_v2_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户所有角色任务V2状态数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                mission_id, parameter_group_id, seq, character_id, mission_status
            FROM 
                user_character_mission_v2_statuses 
            WHERE 
                user_id=?
            ORDER BY 
                mission_id, parameter_group_id, seq, character_id
        """
        cur.execute(sql, (user_id,))
        statuses = cur.fetchall()
        
        return [
            {
                "userId": user_id,
                "missionId": status["mission_id"],
                "parameterGroupId": status["parameter_group_id"],
                "seq": status["seq"],
                "characterId": status["character_id"],
                "missionStatus": status["mission_status"]
            }
            for status in statuses
        ]

    def set_user_character_mission_v2_statuses(self, user_id: int, statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户角色任务V2状态数据"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return
        
        cur = self.conn.cursor()
        
        # 清除现有数据
        sql = "DELETE FROM user_character_mission_v2_statuses WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for status in statuses_data:
            sql = """
                REPLACE INTO user_character_mission_v2_statuses 
                (user_id, mission_id, parameter_group_id, seq, character_id, mission_status) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                status["missionId"],
                status["parameterGroupId"],
                status["seq"],
                status["characterId"],
                status["missionStatus"]
            ))
        
        self.conn.commit()

    def get_user_bonds(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户羁绊数据"""
        return []
    
    def set_user_bonds(self, user_id: int, bonds_data: list[Dict[str, Any]]) -> None:
        """设置用户羁绊数据"""
        pass

    def get_user_bonds_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户羁绊奖励数据"""
        return []
    
    def set_user_bonds_rewards(self, user_id: int, bonds_rewards_data: list[Dict[str, Any]]) -> None:
        """设置用户羁绊奖励数据"""
        pass

    def get_user_normal_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户普通任务数据"""
        return []
    
    def set_user_normal_missions(self, user_id: int, normal_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户普通任务数据"""
        pass

    def get_user_beginner_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户新手任务数据"""
        return []
    
    def set_user_beginner_missions(self, user_id: int, beginner_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户新手任务数据"""
        pass

    def get_user_beginner_mission_v2s(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户新手任务V2数据"""
        return []
    
    def set_user_beginner_mission_v2s(self, user_id: int, beginner_mission_v2s_data: list[Dict[str, Any]]) -> None:
        """设置用户新手任务V2数据"""
        pass

    def get_user_beginner_mission_behavior(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户新手任务行为数据"""
        return {"userBeginnerMissionBehaviorType": "beginner_mission_v2"}
    
    def set_user_beginner_mission_behavior(self, user_id: int, behavior_data: Dict[str, Any]) -> None:
        """设置用户新手任务行为数据"""
        pass

    def get_user_mission_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户任务状态数据"""
        return []
    
    def set_user_mission_statuses(self, user_id: int, mission_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户任务状态数据"""
        pass

    def get_user_live_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户Live任务数据"""
        return []
    
    def set_user_live_missions(self, user_id: int, live_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户Live任务数据"""
        pass

    def get_user_fix_costumes(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户固定服装数据"""
        return []
    
    def set_user_fix_costumes(self, user_id: int, fix_costumes_data: list[Dict[str, Any]]) -> None:
        """设置用户固定服装数据"""
        pass

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户资料数据"""
        return {
            "userId": user_id,
            "profileImageType": "leader"
        }
    
    def set_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> None:
        """设置用户资料数据"""
        pass

    def get_user_honors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户荣誉数据"""
        return []
    
    def set_user_honors(self, user_id: int, honors_data: list[Dict[str, Any]]) -> None:
        """设置用户荣誉数据"""
        pass

    def get_user_honor_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户荣誉任务数据"""
        return [
            {
                "honorMissionType": "collect_stamp",
                "progress": 11,
                "achievedMissionIds": []
            },
            {
                "honorMissionType": "read_unit_story_no_skip",
                "progress": 0,
                "achievedMissionIds": []
            }
        ]
    
    def set_user_honor_missions(self, user_id: int, honor_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户荣誉任务数据"""
        pass

    def get_user_profile_honors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户资料荣誉数据"""
        return []
    
    def set_user_profile_honors(self, user_id: int, profile_honors_data: list[Dict[str, Any]]) -> None:
        """设置用户资料荣誉数据"""
        pass

    def get_user_bonds_honors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户羁绊荣誉数据"""
        return []
    
    def set_user_bonds_honors(self, user_id: int, bonds_honors_data: list[Dict[str, Any]]) -> None:
        """设置用户羁绊荣誉数据"""
        pass

    def get_user_bonds_honor_words(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户羁绊荣誉词汇数据"""
        return []
    
    def set_user_bonds_honor_words(self, user_id: int, bonds_honor_words_data: list[Dict[str, Any]]) -> None:
        """设置用户羁绊荣誉词汇数据"""
        pass

    def get_user_player_frames(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户玩家框架数据"""
        return []
    
    def set_user_player_frames(self, user_id: int, player_frames_data: list[Dict[str, Any]]) -> None:
        """设置用户玩家框架数据"""
        pass

    def get_user_challenge_live_play_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户挑战Live游玩状态数据"""
        return []
    
    def set_user_challenge_live_play_statuses(self, user_id: int, play_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户挑战Live游玩状态数据"""
        pass

    def get_user_challenge_live_solo_decks(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户挑战Live单人卡组数据"""
        return []
    
    def set_user_challenge_live_solo_decks(self, user_id: int, solo_decks_data: list[Dict[str, Any]]) -> None:
        """设置用户挑战Live单人卡组数据"""
        pass

    def get_user_challenge_live_solo_results(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户挑战Live单人结果数据"""
        return []
    
    def set_user_challenge_live_solo_results(self, user_id: int, solo_results_data: list[Dict[str, Any]]) -> None:
        """设置用户挑战Live单人结果数据"""
        pass

    def get_user_challenge_live_solo_stages(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户挑战Live单人关卡数据"""
        return []
    
    def set_user_challenge_live_solo_stages(self, user_id: int, solo_stages_data: list[Dict[str, Any]]) -> None:
        """设置用户挑战Live单人关卡数据"""
        pass

    def get_user_challenge_live_solo_high_score_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户挑战Live单人高分奖励数据"""
        return []
    
    def set_user_challenge_live_solo_high_score_rewards(self, user_id: int, high_score_rewards_data: list[Dict[str, Any]]) -> None:
        """设置用户挑战Live单人高分奖励数据"""
        pass

    def get_user_virtual_live_beginner_schedule_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟Live新手日程状态数据"""
        return []
    
    def set_user_virtual_live_beginner_schedule_statuses(self, user_id: int, beginner_schedule_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟Live新手日程状态数据"""
        pass

    def get_user_virtual_live_schedule_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟Live日程状态数据"""
        return []
    
    def set_user_virtual_live_schedule_statuses(self, user_id: int, schedule_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟Live日程状态数据"""
        pass

    def get_user_archive_virtual_live_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户归档虚拟Live状态数据"""
        return []
    
    def set_user_archive_virtual_live_statuses(self, user_id: int, archive_virtual_live_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户归档虚拟Live状态数据"""
        pass

    def get_user_virtual_live_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟Live奖励数据"""
        return []
    
    def set_user_virtual_live_rewards(self, user_id: int, virtual_live_rewards_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟Live奖励数据"""
        pass

    def get_user_virtual_shops(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟商店数据"""
        if self.conn is None:
            return []
        
        cur = self.conn.cursor()
        
        cur.execute("""
            SELECT virtual_shop_id
            FROM user_virtual_shops
            WHERE user_id = ?
            ORDER BY virtual_shop_id
        """, (user_id,))
        
        shops = []
        for shop_row in cur.fetchall():
            virtual_shop_id = shop_row[0]
            
            cur.execute("""
                SELECT virtual_shop_id, virtual_shop_item_id, status
                FROM user_virtual_shop_items
                WHERE user_id = ? AND virtual_shop_id = ?
                ORDER BY virtual_shop_item_id
            """, (user_id, virtual_shop_id))
            
            shop_items = []
            for item_row in cur.fetchall():
                shop_items.append({
                    "virtualShopId": item_row["virtual_shop_id"],
                    "virtualShopItemId": item_row["virtual_shop_item_id"],
                    "status": item_row["status"]
                })
            
            shops.append({
                "virtualShopId": virtual_shop_id,
                "userVirtualShopItems": shop_items
            })
        
        return shops
    
    def set_user_virtual_shops(self, user_id: int, virtual_shops_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟商店数据"""
        if self.conn is None:
            return
            
        cur = self.conn.cursor()
        
        cur.execute("DELETE FROM user_virtual_shops WHERE user_id = ?", (user_id,))
        
        for shop in virtual_shops_data:
            virtual_shop_id = shop["virtualShopId"]
            
            cur.execute("""
                REPLACE INTO user_virtual_shops (user_id, virtual_shop_id)
                VALUES (?, ?)
            """, (user_id, virtual_shop_id))

            for item in shop.get("userVirtualShopItems", []):
                cur.execute("""
                    REPLACE INTO user_virtual_shop_items 
                    (user_id, virtual_shop_id, virtual_shop_item_id, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_id,
                    item["virtualShopId"],
                    item["virtualShopItemId"],
                    item["status"]
                ))
        
        self.conn.commit()


    def get_user_virtual_live_tickets(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟Live票券数据"""
        return []
    
    def set_user_virtual_live_tickets(self, user_id: int, virtual_live_tickets_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟Live票券数据"""
        pass

    def get_user_virtual_live_pamphlets(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户虚拟Live小册子数据"""
        return []
    
    def set_user_virtual_live_pamphlets(self, user_id: int, virtual_live_pamphlets_data: list[Dict[str, Any]]) -> None:
        """设置用户虚拟Live小册子数据"""
        pass

    def get_user_used_virtual_live_tickets(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户已使用虚拟Live票券数据"""
        return []
    
    def set_user_used_virtual_live_tickets(self, user_id: int, used_virtual_live_tickets_data: list[Dict[str, Any]]) -> None:
        """设置用户已使用虚拟Live票券数据"""
        pass

    def get_user_avatar(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户豆腐人数据"""
        return {"avatarSkinColorId": 1}
    
    def set_user_avatar(self, user_id: int, avatar_data: Dict[str, Any]) -> None:
        """设置用户豆腐人数据"""
        pass

    def get_user_avatar_accessories(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人配饰数据"""
        return []
    
    def set_user_avatar_accessories(self, user_id: int, avatar_accessories_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人配饰数据"""
        pass

    def get_user_avatar_costumes(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人服装数据"""
        return [{"avatarCostumeId": 1}]
    
    def set_user_avatar_costumes(self, user_id: int, avatar_costumes_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人服装数据"""
        pass

    def get_user_avatar_motions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人动作数据"""
        return [
            {"avatarMotionId": 3},
            {"avatarMotionId": 5},
            {"avatarMotionId": 33},
            {"avatarMotionId": 34},
            {"avatarMotionId": 35}
        ]
    
    def set_user_avatar_motions(self, user_id: int, avatar_motions_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人动作数据"""
        pass

    def get_user_avatar_motion_favorites(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人动作收藏数据"""
        return [
            {"avatarMotionId": 3, "num": 4},
            {"avatarMotionId": 5, "num": 1},
            {"avatarMotionId": 33, "num": 2},
            {"avatarMotionId": 34, "num": 3},
            {"avatarMotionId": 35, "num": 0}
        ]
    
    def set_user_avatar_motion_favorites(self, user_id: int, avatar_motion_favorites_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人动作收藏数据"""
        pass

    def get_user_avatar_skin_colors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人肤色数据"""
        return [
            {"avatarSkinColorId": i} for i in range(1, 15)
        ]
    
    def set_user_avatar_skin_colors(self, user_id: int, avatar_skin_colors_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人肤色数据"""
        pass

    def get_user_avatar_coordinates(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户豆腐人坐标数据"""
        return []
    
    def set_user_avatar_coordinates(self, user_id: int, avatar_coordinates_data: list[Dict[str, Any]]) -> None:
        """设置用户豆腐人坐标数据"""
        pass

    def get_user_penlights(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户荧光棒数据"""
        return [{"penlightId": 1, "favoriteFlg": True}]
    
    def set_user_penlights(self, user_id: int, penlights_data: list[Dict[str, Any]]) -> None:
        """设置用户荧光棒数据"""
        pass

    def get_user_login_bonuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户登录奖励数据"""
        return []
    
    def set_user_login_bonuses(self, user_id: int, login_bonuses_data: list[Dict[str, Any]]) -> None:
        """设置用户登录奖励数据"""
        pass

    def get_user_platform_inherit_ios(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户iOS平台引继数据"""
        return {}
    
    def set_user_platform_inherit_ios(self, user_id: int, platform_inherit_ios_data: Dict[str, Any]) -> None:
        """设置用户iOS平台引继数据"""
        pass

    def get_user_platform_inherit_android(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户Android平台引继数据"""
        return {}
    
    def set_user_platform_inherit_android(self, user_id: int, platform_inherit_android_data: Dict[str, Any]) -> None:
        """设置用户Android平台引继数据"""
        pass

    def get_user_inherit(self, user_id: int, get_password: bool = False) -> Optional[Dict[str, Any]]:
        """获取用户引继数据"""
        if self.conn is None:
            logger.error("Database connection is not available")
            return None
        
        cur = self.conn.cursor()
        sql = """
            SELECT
                user_id, inherit_id, password
            FROM
                user_inherit
            WHERE
                user_id=?
        """
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row is None:
            return None
        result = {
            "userId": row["user_id"],
            "inheritId": row["inherit_id"]
        }
        if get_password:
            result["password"] = row["password"]
        return result

    
    def set_user_inherit(self, user_id: int, inherit_data: Dict[str, Any]) -> None:
        """设置用户引继数据"""
        if inherit_data == None or inherit_data == {}:
            return
        
        if self.conn is None:
            logger.error("Database connection is not available")
            return
        
        cur = self.conn.cursor()
        
        sql = """
            REPLACE INTO user_inherit
            (user_id, inherit_id, password)
            VALUES (?, ?, ?)
        """
        cur.execute(sql, (
            user_id,
            inherit_data.get("inheritId"),
            inherit_data.get("password")
        ))
        
        self.conn.commit()
    
    def get_user_inherit_by_inherit_id(self, inherit_id: str) -> Optional[Dict[str, Any]]:
        """通过引继ID获取用户引继数据"""
        if self.conn is None:
            logger.error("Database connection is not available")
            return None
        
        cur = self.conn.cursor()
        sql = """
            SELECT
                user_id, inherit_id, password
            FROM
                user_inherit
            WHERE
                inherit_id=?
        """
        cur.execute(sql, (inherit_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return {
            "userId": row["user_id"],
            "inheritId": row["inherit_id"],
            "password": row["password"]
        }

    def get_user_character_live_usage_counts(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户角色Live使用次数数据"""
        return []
    
    def set_user_character_live_usage_counts(self, user_id: int, character_live_usage_counts_data: list[Dict[str, Any]]) -> None:
        """设置用户角色Live使用次数数据"""
        pass

    def get_user_one_time_behaviors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户一次性行为数据"""
        return []
    
    def set_user_one_time_behaviors(self, user_id: int, one_time_behaviors_data: list[Dict[str, Any]]) -> None:
        """设置用户一次性行为数据"""
        pass

    def get_user_events(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户活动数据"""
        return []
    
    def set_user_events(self, user_id: int, events_data: list[Dict[str, Any]]) -> None:
        """设置用户活动数据"""
        pass

    def get_user_event_items(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户活动物品数据"""
        return []
    
    def set_user_event_items(self, user_id: int, event_items_data: list[Dict[str, Any]]) -> None:
        """设置用户活动物品数据"""
        pass

    def get_user_event_exchanges(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户活动兑换数据"""
        if self.conn is None:
            logger.error("Database connection is not available")
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                event_id, event_exchange_id, exchange_remaining, exchange_status
            FROM 
                user_event_exchanges 
            WHERE 
                user_id=? 
            ORDER BY 
                event_id, event_exchange_id
        """
        cur.execute(sql, (user_id,))
        exchanges = cur.fetchall()
        
        return [
            {
                "eventId": exchange["event_id"],
                "eventExchangeId": exchange["event_exchange_id"],
                **({"exchangeRemaining": exchange["exchange_remaining"]} if exchange["exchange_remaining"] is not None else {}), # 可选字段
                "exchangeStatus": exchange["exchange_status"]
            }
            for exchange in exchanges
        ]
    
    def set_user_event_exchanges(self, user_id: int, event_exchanges_data: list[Dict[str, Any]]) -> None:
        """设置用户活动兑换数据"""
        if self.conn is None:
            logger.error("Database connection is not available")
            return
        
        cur = self.conn.cursor()
        
        # 先删除现有数据
        sql = "DELETE FROM user_event_exchanges WHERE user_id=?"
        cur.execute(sql, (user_id,))
        
        # 插入新数据
        for exchange in event_exchanges_data:
            sql = """
                REPLACE INTO user_event_exchanges 
                (user_id, event_id, event_exchange_id, exchange_remaining, exchange_status) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                user_id,
                exchange.get("eventId"),
                exchange.get("eventExchangeId"),
                exchange.get("exchangeRemaining"),
                exchange.get("exchangeStatus", "exchangeable")
            ))
        
        self.conn.commit()

    def get_user_cheerful_carnivals(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户欢快嘉年华数据"""
        return []
    
    def set_user_cheerful_carnivals(self, user_id: int, cheerful_carnivals_data: list[Dict[str, Any]]) -> None:
        """设置用户欢快嘉年华数据"""
        pass

    def get_user_cheerful_carnival_behaviors(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户欢快嘉年华行为数据"""
        return []
    
    def set_user_cheerful_carnival_behaviors(self, user_id: int, cheerful_carnival_behaviors_data: list[Dict[str, Any]]) -> None:
        """设置用户欢快嘉年华行为数据"""
        pass

    def get_user_multi_live_penalty(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户多人Live惩罚数据"""
        return {}
    
    def set_user_multi_live_penalty(self, user_id: int, multi_live_penalty_data: Dict[str, Any]) -> None:
        """设置用户多人Live惩罚数据"""
        pass

    def get_user_auto_live(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户自动Live数据"""
        return {"count": 0}
    
    def set_user_auto_live(self, user_id: int, auto_live_data: Dict[str, Any]) -> None:
        """设置用户自动Live数据"""
        pass

    def get_user_friends(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户好友数据"""
        return []
    
    def set_user_friends(self, user_id: int, friends_data: list[Dict[str, Any]]) -> None:
        """设置用户好友数据"""
        pass

    def get_user_blocks(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户黑名单数据"""
        return []
    
    def set_user_blocks(self, user_id: int, blocks_data: list[Dict[str, Any]]) -> None:
        """设置用户黑名单数据"""
        pass

    def get_user_gacha_wishes(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户抽卡期望数据"""
        return []
    
    def set_user_gacha_wishes(self, user_id: int, gacha_wishes_data: list[Dict[str, Any]]) -> None:
        """设置用户抽卡期望数据"""
        pass

    def get_user_gift_gacha_wishes(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户礼物抽卡期望数据"""
        return []
    
    def set_user_gift_gacha_wishes(self, user_id: int, gift_gacha_wishes_data: list[Dict[str, Any]]) -> None:
        """设置用户礼物抽卡期望数据"""
        pass

    def get_user_categorized_gacha_wishes(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户分类抽卡期望数据"""
        return []
    
    def set_user_categorized_gacha_wishes(self, user_id: int, categorized_gacha_wishes_data: list[Dict[str, Any]]) -> None:
        """设置用户分类抽卡期望数据"""
        pass

    def get_user_boost_granteds(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户体力赠送数据"""
        return []
    
    def set_user_boost_granteds(self, user_id: int, boost_granteds_data: list[Dict[str, Any]]) -> None:
        """设置用户体力赠送数据"""
        pass

    def get_user_boost_receivables(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户可接收体力数据"""
        return []
    
    def set_user_boost_receivables(self, user_id: int, boost_receivables_data: list[Dict[str, Any]]) -> None:
        """设置用户可接收体力数据"""
        pass

    def get_user_boost_received(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户已接收体力数据"""
        return {}
    
    def set_user_boost_received(self, user_id: int, boost_received_data: Dict[str, Any]) -> None:
        """设置用户已接收体力数据"""
        pass

    def get_user_cheerful_carnival_result_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户欢快嘉年华结果奖励数据"""
        return []
    
    def set_user_cheerful_carnival_result_rewards(self, user_id: int, carnival_result_rewards_data: list[Dict[str, Any]]) -> None:
        """设置用户欢快嘉年华结果奖励数据"""
        pass

    def get_user_gacha_ceil_exchange_substitute_costs(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户扭蛋保底兑换替代成本数据"""
        return []
    
    def set_user_gacha_ceil_exchange_substitute_costs(self, user_id: int, substitute_costs_data: list[Dict[str, Any]]) -> None:
        """设置用户扭蛋保底兑换替代成本数据"""
        pass

    def get_user_custom_profiles(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户自定义档案数据"""
        return []
    
    def set_user_custom_profiles(self, user_id: int, custom_profiles_data: list[Dict[str, Any]]) -> None:
        """设置用户自定义档案数据"""
        pass

    def get_user_custom_profile_cards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户自定义档案卡片数据"""
        return []
    
    def set_user_custom_profile_cards(self, user_id: int, custom_profile_cards_data: list[Dict[str, Any]]) -> None:
        """设置用户自定义档案卡片数据"""
        pass

    def get_user_custom_profile_resources(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户自定义档案资源数据"""
        return []
    
    def set_user_custom_profile_resources(self, user_id: int, custom_profile_resources_data: list[Dict[str, Any]]) -> None:
        """设置用户自定义档案资源数据"""
        pass

    def get_user_custom_profile_resource_usages(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户自定义档案资源使用数据"""
        return []
    
    def set_user_custom_profile_resource_usages(self, user_id: int, resource_usages_data: list[Dict[str, Any]]) -> None:
        """设置用户自定义档案资源使用数据"""
        pass

    def get_user_custom_profile_gachas(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户自定义档案扭蛋数据"""
        return []
    
    def set_user_custom_profile_gachas(self, user_id: int, custom_profile_gachas_data: list[Dict[str, Any]]) -> None:
        """设置用户自定义档案扭蛋数据"""
        pass

    def get_user_rank_match_result(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户排位赛结果数据"""
        return {"liveId": "", "liveStatus": "none"}
    
    def set_user_rank_match_result(self, user_id: int, rank_match_result_data: Dict[str, Any]) -> None:
        """设置用户排位赛结果数据"""
        pass

    def get_user_rank_match_seasons(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户排位赛赛季数据"""
        return []
    
    def set_user_rank_match_seasons(self, user_id: int, rank_match_seasons_data: list[Dict[str, Any]]) -> None:
        """设置用户排位赛赛季数据"""
        pass

    def get_user_panel_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户面板任务数据"""
        return []
    
    def set_user_panel_missions(self, user_id: int, panel_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户面板任务数据"""
        pass

    def get_user_panel_mission_sheets(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户面板任务表数据"""
        return []
    
    def set_user_panel_mission_sheets(self, user_id: int, panel_mission_sheets_data: list[Dict[str, Any]]) -> None:
        """设置用户面板任务表数据"""
        pass

    def get_user_panel_mission_achieved_elements(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户面板任务已达成元素数据"""
        return []
    
    def set_user_panel_mission_achieved_elements(self, user_id: int, achieved_elements_data: list[Dict[str, Any]]) -> None:
        """设置用户面板任务已达成元素数据"""
        pass

    def get_user_event_missions(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户活动任务数据"""
        return []
    
    def set_user_event_missions(self, user_id: int, event_missions_data: list[Dict[str, Any]]) -> None:
        """设置用户活动任务数据"""
        pass

    def get_user_my_lists(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户收藏列表数据"""
        return []
    
    def set_user_my_lists(self, user_id: int, my_lists_data: list[Dict[str, Any]]) -> None:
        """设置用户收藏列表数据"""
        pass

    def get_user_paid_virtual_lives(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户付费虚拟Live数据"""
        return {"paidVirtualLiveIds": []}
    
    def set_user_paid_virtual_lives(self, user_id: int, paid_virtual_lives_data: Dict[str, Any]) -> None:
        """设置用户付费虚拟Live数据"""
        pass

    def get_user_paid_virtual_live_statuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户付费虚拟Live状态数据"""
        return []
    
    def set_user_paid_virtual_live_statuses(self, user_id: int, paid_virtual_live_statuses_data: list[Dict[str, Any]]) -> None:
        """设置用户付费虚拟Live状态数据"""
        pass

    def get_user_paid_virtual_live_shop_items(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户付费虚拟Live商店物品数据"""
        return {"paidVirtualLiveShopItemIds": []}
    
    def set_user_paid_virtual_live_shop_items(self, user_id: int, shop_items_data: Dict[str, Any]) -> None:
        """设置用户付费虚拟Live商店物品数据"""
        pass

    def get_user_gacha_free_resources(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户扭蛋免费资源数据"""
        return []
    
    def set_user_gacha_free_resources(self, user_id: int, gacha_free_resources_data: list[Dict[str, Any]]) -> None:
        """设置用户扭蛋免费资源数据"""
        pass

    def get_user_story_favorites(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户故事收藏数据"""
        return []
    
    def set_user_story_favorites(self, user_id: int, story_favorites_data: list[Dict[str, Any]]) -> None:
        """设置用户故事收藏数据"""
        pass

    def get_user_bookmarked_stories(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户书签故事数据"""
        return []
    
    def set_user_bookmarked_stories(self, user_id: int, bookmarked_stories_data: list[Dict[str, Any]]) -> None:
        """设置用户书签故事数据"""
        pass

    def get_user_friend_invitation_campaigns(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户好友邀请活动数据"""
        return []
    
    def set_user_friend_invitation_campaigns(self, user_id: int, invitation_campaigns_data: list[Dict[str, Any]]) -> None:
        """设置用户好友邀请活动数据"""
        pass

    def get_user_friend_invitation_campaign_mission_reward_counts(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户好友邀请活动任务奖励次数数据"""
        return []
    
    def set_user_friend_invitation_campaign_mission_reward_counts(self, user_id: int, reward_counts_data: list[Dict[str, Any]]) -> None:
        """设置用户好友邀请活动任务奖励次数数据"""
        pass

    def get_user_world_blooms(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户世界绽放数据"""
        return []
    
    def set_user_world_blooms(self, user_id: int, world_blooms_data: list[Dict[str, Any]]) -> None:
        """设置用户世界绽放数据"""
        pass

    def get_user_world_bloom_support_decks(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户世界绽放支援卡组数据"""
        return []
    
    def set_user_world_bloom_support_decks(self, user_id: int, support_decks_data: list[Dict[str, Any]]) -> None:
        """设置用户世界绽放支援卡组数据"""
        pass

    def get_user_live_character_archive_voice(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户Live角色档案语音数据"""
        return {
            "characterArchiveVoiceGroupIds": [
                1010001,1010002,1010003,1010004,1020001,1020002,1020003,1020004,1030001,1030002,1030003,1030004,1040001,1040002,1040003,1040004,1050001,1050002,1050003,1050004,1060001,1060002,1060003,1060004,1070001,1070002,1070003,1070004,1080001,1080002,1080003,1080004,1090001,1090002,1090003,1090004,1100001,1100002,1100003,1100004,1110001,1110002,1110003,1110004,1120001,1120002,1120003,1120004,1130001,1130002,1130003,1130004,1140001,1140002,1140003,1140004,1150001,1150002,1150003,1150004,1160001,1160002,1160003,1160004,1170001,1170002,1170003,1170004,1180001,1180002,1180003,1180004,1190001,1190002,1190003,1190004,1200001,1200002,1200003,1200004,1210001,1210002,1210003,1210004,1210005,1210006,1210007,1210008,1210009,1210010,1210011,1210012,1210013,1210014,1210015,1210016,1210017,1210018,1210019,1210020,1210021,1210022,1210023,1210024,1220001,1220002,1220003,1220004,1220005,1220006,1220007,1220008,1220009,1220010,1220011,1220012,1220013,1220014,1220015,1220016,1220017,1220018,1220019,1220020,1220021,1220022,1220023,1220024,1230001,1230002,1230003,1230004,1230005,1230006,1230007,1230008,1230009,1230010,1230011,1230012,1230013,1230014,1230015,1230016,1230017,1230018,1230019,1230020,1230021,1230022,1230023,1230024,1240001,1240002,1240003,1240004,1240005,1240006,1240007,1240008,1240009,1240010,1240011,1240012,1240013,1240014,1240015,1240016,1240017,1240018,1240019,1240020,1240021,1240022,1240023,1240024,1250001,1250002,1250003,1250004,1250005,1250006,1250007,1250008,1250009,1250010,1250011,1250012,1250013,1250014,1250015,1250016,1250017,1250018,1250019,1250020,1250021,1250022,1250023,1250024,1260001,1260002,1260003,1260004,1260005,1260006,1260007,1260008,1260009,1260010,1260011,1260012,1260013,1260014,1260015,1260016,1260017,1260018,1260019,1260020,1260021,1260022,1260023,1260024,3010001,3010002,3010003,3010004,3010005,3010006,3020001,3020002,3020003,3020004,3020005,3020006,3030001,3030002,3030003,3030004,3030005,3030006,3040001,3040002,3040003,3040004,3040005,3040006,3050001,3050002,3050003,3050004,3050005,3050006,3060001,3060002,3060003,3060004,3060005,3060006,3070001,3070002,3070003,3070004,3070005,3070006,3080001,3080002,3080003,3080004,3080005,3080006,3090001,3090002,3090003,3090004,3090005,3090006,3100001,3100002,3100003,3100004,3100005,3100006,3110001,3110002,3110003,3110004,3110005,3110006,3120001,3120002,3120003,3120004,3120005,3120006,3130001,3130002,3130003,3130004,3130005,3130006,3140001,3140002,3140003,3140004,3140005,3140006,3150001,3150002,3150003,3150004,3150005,3150006,3160001,3160002,3160003,3160004,3160005,3160006,3170001,3170002,3170003,3170004,3170005,3170006,3180001,3180002,3180003,3180004,3180005,3180006,3190001,3190002,3190003,3190004,3190005,3190006,3200001,3200002,3200003,3200004,3200005,3200006,3210001,3210002,3210003,3210004,3210005,3210006,3210007,3210008,3210009,3210010,3210011,3210012,3210013,3210014,3210015,3210016,3210017,3210018,3210019,3210020,3210021,3210022,3210023,3210024,3210025,3210026,3210027,3210028,3210029,3210030,3210031,3210032,3210033,3210034,3210035,3210036,3220001,3220002,3220003,3220004,3220005,3220006,3230001,3230002,3230003,3230004,3230005,3230006,3240001,3240002,3240003,3240004,3240005,3240006,3250001,3250002,3250003,3250004,3250005,3250006,3260001,3260002,3260003,3260004,3260005,3260006
            ]
        }
    
    def set_user_live_character_archive_voice(self, user_id: int, archive_voice_data: Dict[str, Any]) -> None:
        """设置用户Live角色档案语音数据"""
        pass

    def get_user_ad_rewards(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户广告奖励数据"""
        return []
    
    def set_user_ad_rewards(self, user_id: int, ad_rewards_data: list[Dict[str, Any]]) -> None:
        """设置用户广告奖励数据"""
        pass

    def get_user_serial_code_items(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户序列号物品数据"""
        return []
    
    def set_user_serial_code_items(self, user_id: int, serial_code_items_data: list[Dict[str, Any]]) -> None:
        """设置用户序列号物品数据"""
        pass

    def get_user_appeals(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户申诉数据"""
        return []
    
    def set_user_appeals(self, user_id: int, appeals_data: list[Dict[str, Any]]) -> None:
        """设置用户申诉数据"""
        pass

    def get_user_viewable_appeal(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户可查看申诉数据"""
        return {
            "appealIds": [243, 244]
        }
    
    def set_user_viewable_appeal(self, user_id: int, viewable_appeal_data: Dict[str, Any]) -> None:
        """设置用户可查看申诉数据"""
        pass

    def get_user_billing_refund_penalty(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户计费退款惩罚数据"""
        return {}
    
    def set_user_billing_refund_penalty(self, user_id: int, billing_refund_penalty_data: Dict[str, Any]) -> None:
        """设置用户计费退款惩罚数据"""
        pass

    def get_user_billing_refunds(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户计费退款数据"""
        return []
    
    def set_user_billing_refunds(self, user_id: int, billing_refunds_data: list[Dict[str, Any]]) -> None:
        """设置用户计费退款数据"""
        pass

    def get_user_unprocessed_orders(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户未处理订单数据"""
        return []
    
    def set_user_unprocessed_orders(self, user_id: int, unprocessed_orders_data: list[Dict[str, Any]]) -> None:
        """设置用户未处理订单数据"""
        pass

    def get_user_omikujis(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户抽签数据"""
        return []
    
    def set_user_omikujis(self, user_id: int, omikujis_data: list[Dict[str, Any]]) -> None:
        """设置用户抽签数据"""
        pass

    def get_user_preliminary_tournament_live_results(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户初赛锦标赛Live结果数据"""
        return []
    
    def set_user_preliminary_tournament_live_results(self, user_id: int, tournament_results_data: list[Dict[str, Any]]) -> None:
        """设置用户初赛锦标赛Live结果数据"""
        pass

    def get_user_platforms(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户平台数据"""
        return []
    
    def set_user_platforms(self, user_id: int, platforms_data: list[Dict[str, Any]]) -> None:
        """设置用户平台数据"""
        pass

    def get_user_mysekai_materials(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户MySekai材料数据"""
        return []
    
    def set_user_mysekai_materials(self, user_id: int, mysekai_materials_data: list[Dict[str, Any]]) -> None:
        """设置用户MySekai材料数据"""
        pass

    def get_user_mysekai_canvases(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户MySekai画布数据"""
        return []
    
    def set_user_mysekai_canvases(self, user_id: int, mysekai_canvases_data: list[Dict[str, Any]]) -> None:
        """设置用户MySekai画布数据"""
        pass

    def get_user_mysekai_gates(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户MySekai门户数据"""
        return []
    
    def set_user_mysekai_gates(self, user_id: int, mysekai_gates_data: list[Dict[str, Any]]) -> None:
        """设置用户MySekai门户数据"""
        pass

    def get_user_mysekai_character_talks(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户MySekai角色对话数据"""
        return []
    
    def set_user_mysekai_character_talks(self, user_id: int, mysekai_character_talks_data: list[Dict[str, Any]]) -> None:
        """设置用户MySekai角色对话数据"""
        pass

    def get_user_mysekai_colorful_pass(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户MySekai彩色通行证数据"""
        return {}
    
    def set_user_mysekai_colorful_pass(self, user_id: int, mysekai_colorful_pass_data: Dict[str, Any]) -> None:
        """设置用户MySekai彩色通行证数据"""
        pass

    def get_user_mysekai_fixture_game_character_performance_bonuses(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户MySekai固定游戏角色表现奖励数据"""
        return []
    
    def set_user_mysekai_fixture_game_character_performance_bonuses(self, user_id: int, performance_bonuses_data: list[Dict[str, Any]]) -> None:
        """设置用户MySekai固定游戏角色表现奖励数据"""
        pass

    def get_user_informations(self, user_id: int) -> list[Dict[str, Any]]:
        """获取用户信息列表（全局信息，与用户无关）"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return []
        
        cur = self.conn.cursor()
        sql = """
            SELECT 
                id, seq, display_order, information_type, information_tag, 
                browse_type, platform, title, path, start_at, end_at, 
                banner_assetbundle_name
            FROM 
                user_informations 
            ORDER BY 
                id
        """
        cur.execute(sql)
        informations = cur.fetchall()
        
        result = []
        for info in informations:
            info_dict = {
                "id": info["id"],
                "seq": info["seq"],
                "displayOrder": info["display_order"],
                "informationType": info["information_type"],
                "informationTag": info["information_tag"],
                "browseType": info["browse_type"],
                "platform": info["platform"],
                "title": info["title"],
                "path": info["path"],
                "startAt": info["start_at"]
            }
            
            # 可选字段
            if info["end_at"] is not None:
                info_dict["endAt"] = info["end_at"]
            if info["banner_assetbundle_name"] is not None:
                info_dict["bannerAssetbundleName"] = info["banner_assetbundle_name"]
                
            result.append(info_dict)
        
        return result
    
    def set_user_informations(self, informations_data: list[Dict[str, Any]]) -> None:
        """设置用户信息列表（全局信息，与用户无关）"""
        if self.conn is None:
            logger.error("数据库连接未建立")
            return
        
        cur = self.conn.cursor()
        
        # 先清空现有数据
        sql = "DELETE FROM user_informations"
        cur.execute(sql)
        
        # 插入新数据
        for info in informations_data:
            sql = """
                REPLACE INTO user_informations (
                    id, seq, display_order, information_type, information_tag,
                    browse_type, platform, title, path, start_at, end_at,
                    banner_assetbundle_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, (
                info.get("id"),
                info.get("seq"),
                info.get("displayOrder"),
                info.get("informationType"),
                info.get("informationTag"),
                info.get("browseType"),
                info.get("platform"),
                info.get("title"),
                info.get("path"),
                info.get("startAt"),
                info.get("endAt"),
                info.get("bannerAssetbundleName")
            ))
        
        self.conn.commit()

    
    getters = {
        "now": lambda db, user_id: int(time.time() * 1000),
        "refreshableTypes": lambda db, user_id: [],
        "userRegistration": get_user_registration,
        "userGamedata": get_user_gamedata,
        "userChargedCurrency": get_user_charged_currency,
        "userBoost": get_user_boost,
        "userConfig": get_user_config,
        "userTutorial": get_user_tutorial,
        "userAreas": get_user_areas,
        "userActionSets": get_user_action_sets,
        "userCards": get_user_cards,
        "userDecks": get_user_decks,
        "userMusics": get_user_musics,
        "userMusicVocals": get_user_music_vocals,
        "userMusicResults": get_user_music_results,
        "userMusicAchievements": get_user_music_achievements,
        "userShops": get_user_shops,
        "userBillingShopItems": get_user_billing_shop_items,
        "userColorfulPass": get_user_colorful_pass,
        "userColorfulPassV2": get_user_colorful_pass_v2,
        "userPracticeTickets": get_user_practice_tickets,
        "userSkillPracticeTickets": get_user_skill_practice_tickets,
        "userMaterials": get_user_materials,
        "userGachas": get_user_gachas,
        "userGachaBonusPoints": get_user_gacha_bonus_points,
        "userUnitEpisodeStatuses": get_user_unit_episode_statuses,
        "userSpecialEpisodeStatuses": get_user_special_episode_statuses,
        "userEventEpisodeStatuses": get_user_event_episode_statuses,
        "userArchiveEventEpisodeStatuses": get_user_archive_event_episode_statuses,
        "userCharacterProfileEpisodeStatuses": get_user_character_profile_episode_statuses,
        "userStoryMission": get_user_story_mission,
        "userEventArchiveCompleteReadRewards": get_user_event_archive_complete_read_rewards,
        "userUnits": get_user_units,
        "userPresents": get_user_presents,
        "userCostume3dStatuses": get_user_costume_3d_statuses,
        "userCostume3dShopItems": get_user_costume_3d_shop_items,
        "userCharacterCostume3ds": get_user_character_costume_3ds,
        "userReleaseConditions": get_user_release_conditions,
        "unreadUserTopics": get_unread_user_topics,
        "userHomeBanners": get_user_home_banners,
        "userStamps": get_user_stamps,
        "userStampFavorites": get_user_stamp_favorites,
        "userStampFavoriteTabs": get_user_stamp_favorite_tabs,
        "userMaterialExchanges": get_user_material_exchanges,
        "userGachaCeilExchanges": get_user_gacha_ceil_exchanges,
        "userGachaCeilItems": get_user_gacha_ceil_items,
        "userGachaTickets": get_user_gacha_tickets,
        "userBoostItems": get_user_boost_items,
        "userCharacters": get_user_characters,
        "userCharacterMissionV2s": get_user_character_mission_v2s,
        "userCharacterMissionV2Statuses": get_user_character_mission_v2_statuses,
        "userBonds": get_user_bonds,
        "userBondsRewards": get_user_bonds_rewards,
        "userNormalMissions": get_user_normal_missions,
        "userBeginnerMissions": get_user_beginner_missions,
        "userBeginnerMissionV2s": get_user_beginner_mission_v2s,
        "userBeginnerMissionBehavior": get_user_beginner_mission_behavior,
        "userMissionStatuses": get_user_mission_statuses,
        "userLiveMissions": get_user_live_missions,
        "userFixCostumes": get_user_fix_costumes,
        "userProfile": get_user_profile,
        "userHonors": get_user_honors,
        "userHonorMissions": get_user_honor_missions,
        "userProfileHonors": get_user_profile_honors,
        "userBondsHonors": get_user_bonds_honors,
        "userBondsHonorWords": get_user_bonds_honor_words,
        "userPlayerFrames": get_user_player_frames,
        "userChallengeLivePlayStatuses": get_user_challenge_live_play_statuses,
        "userChallengeLiveSoloDecks": get_user_challenge_live_solo_decks,
        "userChallengeLiveSoloResults": get_user_challenge_live_solo_results,
        "userChallengeLiveSoloStages": get_user_challenge_live_solo_stages,
        "userChallengeLiveSoloHighScoreRewards": get_user_challenge_live_solo_high_score_rewards,
        "userVirtualLiveBeginnerScheduleStatuses": get_user_virtual_live_beginner_schedule_statuses,
        "userVirtualLiveScheduleStatuses": get_user_virtual_live_schedule_statuses,
        "userArchiveVirtualLiveStatuses": get_user_archive_virtual_live_statuses,
        "userVirtualLiveRewards": get_user_virtual_live_rewards,
        "userVirtualShops": get_user_virtual_shops,
        "userVirtualLiveTickets": get_user_virtual_live_tickets,
        "userVirtualLivePamphlets": get_user_virtual_live_pamphlets,
        "userUsedVirtualLiveTickets": get_user_used_virtual_live_tickets,
        "userAvatar": get_user_avatar,
        "userAvatarAccessories": get_user_avatar_accessories,
        "userAvatarCostumes": get_user_avatar_costumes,
        "userAvatarMotions": get_user_avatar_motions,
        "userAvatarMotionFavorites": get_user_avatar_motion_favorites,
        "userAvatarSkinColors": get_user_avatar_skin_colors,
        "userAvatarCoordinates": get_user_avatar_coordinates,
        "userPenlights": get_user_penlights,
        "userLoginBonuses": get_user_login_bonuses,
        "userPlatformInheritIos": get_user_platform_inherit_ios,
        "userPlatformInheritAndroid": get_user_platform_inherit_android,
        "userInherit": get_user_inherit,
        "userCharacterLiveUsageCounts": get_user_character_live_usage_counts,
        "userOneTimeBehaviors": get_user_one_time_behaviors,
        "userEvents": get_user_events,
        "userEventItems": get_user_event_items,
        "userEventExchanges": get_user_event_exchanges,
        "userCheerfulCarnivals": get_user_cheerful_carnivals,
        "userCheerfulCarnivalBehaviors": get_user_cheerful_carnival_behaviors,
        "userMultiLivePenalty": get_user_multi_live_penalty,
        "userAutoLive": get_user_auto_live,
        "userFriends": get_user_friends,
        "userBlocks": get_user_blocks,
        "userGachaWishes": get_user_gacha_wishes,
        "userGiftGachaWishes": get_user_gift_gacha_wishes,
        "userCategorizedGachaWishes": get_user_categorized_gacha_wishes,
        "userBoostGranteds": get_user_boost_granteds,
        "userBoostReceivables": get_user_boost_receivables,
        "userBoostReceived": get_user_boost_received,
        "userCheerfulCarnivalResultRewards": get_user_cheerful_carnival_result_rewards,
        "userGachaCeilExchangeSubstituteCosts": get_user_gacha_ceil_exchange_substitute_costs,
        "userCustomProfiles": get_user_custom_profiles,
        "userCustomProfileCards": get_user_custom_profile_cards,
        "userCustomProfileResources": get_user_custom_profile_resources,
        "userCustomProfileResourceUsages": get_user_custom_profile_resource_usages,
        "userCustomProfileGachas": get_user_custom_profile_gachas,
        "userRankMatchResult": get_user_rank_match_result,
        "userRankMatchSeasons": get_user_rank_match_seasons,
        "userPanelMissions": get_user_panel_missions,
        "userPanelMissionSheets": get_user_panel_mission_sheets,
        "userPanelMissionAchievedElements": get_user_panel_mission_achieved_elements,
        "userEventMissions": get_user_event_missions,
        "userMyLists": get_user_my_lists,
        "userPaidVirtualLives": get_user_paid_virtual_lives,
        "userPaidVirtualLiveStatuses": get_user_paid_virtual_live_statuses,
        "userPaidVirtualLiveShopItems": get_user_paid_virtual_live_shop_items,
        "userGachaFreeResources": get_user_gacha_free_resources,
        "userStoryFavorites": get_user_story_favorites,
        "userBookmarkedStories": get_user_bookmarked_stories,
        "userFriendInvitationCampaigns": get_user_friend_invitation_campaigns,
        "userFriendInvitationCampaignMissionRewardCounts": get_user_friend_invitation_campaign_mission_reward_counts,
        "userWorldBlooms": get_user_world_blooms,
        "userWorldBloomSupportDecks": get_user_world_bloom_support_decks,
        "userLiveCharacterArchiveVoice": get_user_live_character_archive_voice,
        "userAdRewards": get_user_ad_rewards,
        "userSerialCodeItems": get_user_serial_code_items,
        "userAppeals": get_user_appeals,
        "userViewableAppeal": get_user_viewable_appeal,
        "userBillingRefundPenalty": get_user_billing_refund_penalty,
        "userBillingRefunds": get_user_billing_refunds,
        "userUnprocessedOrders": get_user_unprocessed_orders,
        "userOmikujis": get_user_omikujis,
        "userPreliminaryTournamentLiveResults": get_user_preliminary_tournament_live_results,
        "userPlatforms": get_user_platforms,
        "userMysekaiMaterials": get_user_mysekai_materials,
        "userMysekaiCanvases": get_user_mysekai_canvases,
        "userMysekaiGates": get_user_mysekai_gates,
        "userMysekaiCharacterTalks": get_user_mysekai_character_talks,
        "userMysekaiColorfulPass": get_user_mysekai_colorful_pass,
        "userMysekaiFixtureGameCharacterPerformanceBonuses": get_user_mysekai_fixture_game_character_performance_bonuses,
        "userInformations": get_user_informations
    }
    

    def get_new_user_id(self) -> int:
        """获取一个新的用户ID"""
        if self.conn is None:
            logger.error("Database connection is not available")
            return 1
        
        cur = self.conn.cursor()
        sql = "SELECT MAX(user_id) as max_id FROM user_registration"
        cur.execute(sql)
        row = cur.fetchone()
        
        return (row["max_id"] or 0) + 1
    
    def get_user_credential(self, user_id: int) -> Optional[str]:
        """获取用户认证凭据"""
        if self.conn is None:
            return None
        
        cur = self.conn.cursor()
        sql = "SELECT credential FROM user_credentials WHERE user_id = ?"
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        
        if row:
            return row["credential"]
        return None

    def set_user_credential(self, user_id: int, credential: str) -> None:
        """设置用户认证凭据"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        sql = """
            INSERT INTO user_credentials (user_id, credential) 
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET credential=excluded.credential
        """
        cur.execute(sql, (user_id, credential))
        self.conn.commit()

    def get_user_token(self, user_id: int) -> Optional[str]:
        """获取用户会话令牌"""
        if self.conn is None:
            return None
        
        cur = self.conn.cursor()
        sql = "SELECT session_token FROM user_tokens WHERE user_id = ?"
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        
        if row:
            return row["session_token"]
        return None

    def set_user_token(self, user_id: int, session_token: str) -> None:
        """设置用户会话令牌"""
        if self.conn is None:
            return
        
        cur = self.conn.cursor()
        sql = """
            INSERT INTO user_tokens (user_id, session_token) 
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET session_token=excluded.session_token
        """
        cur.execute(sql, (user_id, session_token))
        self.conn.commit()