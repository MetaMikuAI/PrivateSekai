from flask import Blueprint, Response, current_app, request
from werkzeug.local import LocalProxy

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec

tutorial_bp = Blueprint('tutorial', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


@tutorial_bp.route('/api/user/<int:user_id>/tutorial', methods=['PATCH'])
def handle_tutorial_update(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)

    if 'tutorialStatus' not in request_data:
        logger.error("Missing 'tutorialStatus' in request data")
        return Response("Bad Request: Missing tutorialStatus", status=400)

    tutorial_status = request_data['tutorialStatus']
    logger.info(f"User {user_id} updated tutorial status to `{tutorial_status}`")

    user = users.get_user(user_id)
    response_data = user.get_refresh_data()

    user.update_tutorial_progress(tutorial_status)
    response_data = {"updatedResources": user.get_refresh_data()}

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')

@tutorial_bp.route('/api/user/<int:user_id>', methods=['PATCH'])
def handle_user_update(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)

    if 'userGamedata' not in request_data:
        logger.error("Missing 'userGamedata' in request data")
        return Response("Bad Request: Missing userGamedata", status=400)

    new_name = request_data['userGamedata'].get('name', None)
    if new_name is None:
        logger.error("Missing 'name' in userGamedata")
        return Response("Bad Request: Missing name in userGamedata", status=400)

    user = users.get_user(user_id)
    user.update_user_name(new_name)

    user.update_refreshable_types('userGamedata')

    response_data = {"updatedResources": user.get_refresh_data()}
    logger.info(f"User {user_id} gamedata updated")

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')