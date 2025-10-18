from flask import Blueprint, Response, current_app
from werkzeug.local import LocalProxy

from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec
from typing import Any

story_bp = Blueprint('story', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


@story_bp.route('/api/user/<int:user_id>/story/special_story/episode/<int:special_episode_id>', methods=['POST'])
def handle_user_special_story_episode(user_id: int, special_episode_id: int):
    user = users.get_user(user_id)
    user.read_episode(special_episode_id)

    user.update_refreshable_types('userSpecialEpisodeStatuses')
    # user.update_refreshable_types('userVirtualShops')
    # user.update_refreshable_types('userVirtualLiveTickets')
    response_data: dict[str, Any] = {"updatedResources": user.get_refresh_data({"userBeginnerMissionBehavior"}) }
    
    # response_data['obtainedResources'] = [
    #     {
    #         "resourceId": 25,
    #         "resourceType": "virtual_live_ticket",
    #         "quantity": 1
    #     }
    # ]

    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')


@story_bp.route('/api/user/<int:user_id>/story/recommend', methods=['GET'])
def handle_user_story_recommend(user_id: int):
    # user = users.get_user(user_id)

    # TODO: implement recommendation logic
    response_data: dict[str, Any] = {
        "userStoryRecommends": [
            {
                "storyType": "unit_story",
                "storyId": 10,
                "reason": "continuously",
                "category": "continuously",
                "seq": 1
            },
            {
                "storyType": "unit_story",
                "storyId": 9,
                "reason": "main_story",
                "category": "random",
                "seq": 2
            },
            {
                "storyType": "event_story",
                "storyId": 27,
                "reason": "recommend",
                "category": "random",
                "seq": 3
            }
        ]
    }

    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')


# TODO
@story_bp.route('/api/user/<int:user_id>/story-favorite/friend/status/<string:story_type>', methods=['GET'])
def handle_user_story_favorite_friend_status(user_id: int, story_type: str):
    response_data: dict[str, Any] = {
        "friendStoryFavoriteStatuses": []
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# TODO
@story_bp.route('/api/user/<int:user_id>/story-episode-bookmark/<string:story_type>/story/<int:story_id>', methods=['GET'])
def handle_user_story_episode_bookmark(user_id: int, story_type: str, story_id: int):
    response_data: dict[str, Any] = {
        "userStoryEpisodeBookmarks": []
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# TODO
@story_bp.route('/api/user/<int:user_id>/story/archive_event_story/episode/<int:episode_id>/log', methods=['POST'])
def handle_user_archive_event_story_episode_log(user_id: int, episode_id: int):
    user = users.get_user(user_id)
    response_data: dict[str, Any] = {
        'updatedResources': user.get_refresh_data(delete_rtypes={'userBeginnerMissionBehavior'}),
        'userObtainResourceResults': []
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')