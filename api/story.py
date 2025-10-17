from flask import Blueprint, Response, current_app
from werkzeug.local import LocalProxy

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec
from typing import Any

story_bp = Blueprint('story', __name__)
users = LocalProxy(lambda: current_app.users)  # type: ignore


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
