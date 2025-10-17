from game.user import User
import json
import time
from typing import Optional

class Users:
    def __init__(self):
        self.users: dict[int, User] = {}
        self.create_user_0()

    def get_user(self, user_id: int) -> User:
        if user_id not in self.users:
            self.users[user_id] = User()
        return self.users[user_id]
    
    def create_user_0(self):
        user_id = 0
        with open("template/user_0.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)
        user = User(user_data)
        self.users[user_id] = user
    
    def get_new_user_id(self) -> int:
        return max(self.users.keys(), default=-1) + 1

    def fork_new_user(self, user_id: Optional[int] = None) -> int:
        if user_id is None:
            new_user_id = self.get_new_user_id()
        else:
            new_user_id = user_id
        from_user = self.get_user(0)
        new_user = User(from_user)

        new_user.init_all_user_id(new_user_id)
        now = int(time.time() * 1000)
        new_user.init_all_user_time(now)

        self.users[new_user_id] = new_user
        return new_user_id
    
    def user_exists(self, user_id: int) -> bool:
        return user_id in self.users
    
    def get_user_list(self) -> str:
        user_list = [{"userId": user_id} for user_id in self.users.keys()]
        return json.dumps(user_list)
    
    def __iter__(self):
        """使 Users 类可以迭代，迭代时返回 (user_id, user) 元组"""
        return iter(self.users.items())
    
    def __len__(self):
        """返回用户数量"""
        return len(self.users)
    
    def __contains__(self, user_id: int):
        """支持 'user_id in users' 语法"""
        return user_id in self.users


if __name__ == "__main__":
    users = Users()
    users.create_user_0()
    user_0 = users.get_user(0)
    print(user_0)