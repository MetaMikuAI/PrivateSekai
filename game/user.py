import time
from box import Box
from .card import UserCardMixin
from .tutorial import UserTutorialMixin
from .inherit import UserInheritMixin
from .special_story import UserSpecialStoryMixin
from .present import UserPresentMixin
from config import SKIP_TUTORIAL
from typing import Any

class User(UserCardMixin, UserTutorialMixin, UserInheritMixin, UserSpecialStoryMixin, UserPresentMixin, Box):
    def __init__(self, data=None, **kwargs):
        """
        data 可以是:
        - dict
        - None (空对象)
        """
        if data is None:
            data = {}
        super().__init__(data, **kwargs)

    def to_dict(self):
        """转回 dict"""
        return super().to_dict()

    @classmethod
    def from_dict(cls, data):
        """从 dict 创建 User"""
        return cls(data)
    
    def get_user_id(self) -> int:
        return self.userRegistration.userId
    
    def init_all_user_id(self, new_user_id: int):
        self.userRegistration.userId = new_user_id
        self.userGamedata.userId = new_user_id
        self.userProfile.userId = new_user_id

        field = [
            "userCards", 
            "userDecks", 
            "userUnits", 
            "unreadUserTopics", 
            "userMaterialExchanges", 
            "userGachaCeilExchanges", 
            "userCharacterMissionV2Statuses"
        ]
        for f in field:
            for g in getattr(self, f):
                g.userId = new_user_id
    
    def init_all_user_time(self, current_time: int):
        self.now = current_time
        self.userRegistration.registeredAt = current_time
        self.userBoost.recoveryAt = current_time
        for userCard in self.userCards:
            userCard.createdAt = current_time
        for userPresent in self.userPresents:
            userPresent.grantedAt = current_time
        for userCostume3dStatus in self.userCostume3dStatuses:
            if hasattr(userCostume3dStatus, "obtainedAt"):
                userCostume3dStatus.obtainedAt = current_time
        for userReleaseCondition in self.userReleaseConditions:
            userReleaseCondition.createdAt = current_time

        if SKIP_TUTORIAL:
            self.userTutorial = {
                'tutorialStatus': 'end',
                'endAt': current_time
            }

        # userHomeBanners # 这个不改
    
    def init_not_suite(self):
        """增加一个私有的 notsuite 字段，该字段不随 get_suite_user_data 导出"""
        self.notsuite = {
            'userInherit': {
                'inheritId': '',
                'password': ''
            },
            'userPresentHistories': []
        }


    def update_user_name(self, new_name: str):
        self.userGamedata.name = new_name

    def update_refreshable_types(self, rtype: str):
        rtypes = self.refreshableTypes
        if rtype not in rtypes:
            rtypes.append(rtype)
            self.refreshableTypes = rtypes

    def get_suite_user_data(self) -> dict:
        self.now = int(time.time() * 1000)
        suite_data = self.to_dict()
        if hasattr(suite_data, "notsuite"):
            del suite_data["notsuite"]
        return suite_data
    
    def get_not_suite_data(self) -> dict:
        not_suite_data = self.notsuite if hasattr(self, "notsuite") else {}
        return not_suite_data
    
    def get_all_data(self) -> dict:
        all_data = self.to_dict()
        return all_data

    def get_refresh_data(self, delete_rtypes: set[str] = set()) -> dict[str, Any]:
        base_rtypes = {
            "now", 
            "refreshableTypes", 
            "userPresents", 
            "unreadUserTopics", 
            "userHomeBanners", 
            "userMaterialExchanges", 
            "userGachaCeilExchanges", 
            # "userBeginnerMissionBehavior",
            "userRankMatchResult", 
            "userViewableAppeal",
            "userBillingRefunds",
            "userUnprocessedOrders",
            "userInformations"
        }

        rtypes = (set(self.refreshableTypes) | base_rtypes) - delete_rtypes

        self.refreshableTypes = []
        refresh_data = {rtype: getattr(self, rtype, None) for rtype in rtypes if hasattr(self, rtype)}
        refresh_data["now"] = int(time.time() * 1000) # type: ignore
        return refresh_data