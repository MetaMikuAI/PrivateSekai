import string
import random
from typing import Optional, Callable

class UserInheritMixin:
    def set_user_inherit(self, password: str) -> str:
        # if not hasattr(self, 'userInherit'):
        #     self.userInherit = {}
        userInherit = getattr(self, 'userInherit', None)
        assert userInherit is not None

        
        inherit_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        self.userInherit = {
            'inheritId': inherit_id,
            'password': password    # WARN: 实际不应存放于此，存于此处仅为简便实现
        }
        
        update_refreshable_types: Optional[Callable] = getattr(self, 'update_refreshable_types', None)
        assert update_refreshable_types
        update_refreshable_types('userInherit')
        
        return inherit_id

    def get_after_user_gamedata(self) -> dict:
        user_game_data = getattr(self, 'userGamedata', None)
        assert user_game_data

        data = {
            "userId": user_game_data.userId,
            "name": user_game_data.name,
            "deck": user_game_data.deck,
            "rank": user_game_data.rank,
        }
        return data
    
    def verify_inherit(self, inherit_id: str, password: str) -> bool:
        user_inherit = getattr(self, 'userInherit', None)
        assert user_inherit is not None
        
        if user_inherit.get('inheritId') != inherit_id or user_inherit.get('password') != password:
            return False
        
        return True
