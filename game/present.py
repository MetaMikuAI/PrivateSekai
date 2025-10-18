import time
from typing import Any

class UserPresentMixin:
    def receive_present(self, present_id_list: list[int]) -> list[dict[str, Any]]:
        received_user_presents = []        
        for present_id in present_id_list:
            received_user_present = self._receive_one_present(present_id)
            if received_user_present:
                received_user_presents.append(received_user_present)
            
        return received_user_presents
        
    # TODO: 需要完成实际的业务逻辑
    def _receive_one_present(self, present_id: int) -> dict[str, Any]:
        user_presents = getattr(self, 'userPresents', None)
        assert user_presents is not None

        notsuite = getattr(self, 'notsuite', None)
        assert notsuite is not None

        user_present_histories = getattr(notsuite, 'userPresentHistories', None)
        assert user_present_histories is not None

        for user_present in user_presents:
            if user_present.presentId == present_id:
                user_present.receivedAt = int(time.time() * 1000)
                user_present_histories.append(user_present)
                user_presents.remove(user_present)
                return user_present.to_dict()
        
        return {}
    
    def get_present_history(self) -> list:
        notsuite = getattr(self, 'notsuite', None)
        assert notsuite is not None

        user_present_histories = getattr(notsuite, 'userPresentHistories', None)
        assert user_present_histories is not None

        return user_present_histories