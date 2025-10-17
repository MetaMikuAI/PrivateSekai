import time
from typing import Optional, Callable

# class UserTutorialMixin:
class UserSpecialStoryMixin:
    def read_episode(self, special_episode_id: int, is_not_skipped: bool = False):
        user_special_episode_statuses = getattr(self, 'userSpecialEpisodeStatuses', None)
        assert user_special_episode_statuses is not None

        # UPDATE userSpecialEpisodeStatuses 
        # SET status = 'already_read' 
        # WHERE episodeId = special_episode_id;
        for status in user_special_episode_statuses:
            if status.episodeId == special_episode_id:
                status.status = 'already_read'
                status.isNotSkipped = is_not_skipped
                update_refreshable_types: Optional[Callable] = getattr(self, 'update_refreshable_types', None)
                assert update_refreshable_types
                update_refreshable_types('userSpecialEpisodeStatuses')
                return