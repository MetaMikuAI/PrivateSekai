from flask import Blueprint, Response, current_app, request
from werkzeug.local import LocalProxy

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec

home_bp = Blueprint('home', __name__)
users = LocalProxy(lambda: current_app.users)  # type: ignore


@home_bp.route('/api/user/<int:user_id>/home/refresh', methods=['PUT'])
def handle_user_home_refresh(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    # request_data = prsk_dec(body)

    user = users.get_user(user_id)
    user.update_refreshable_types('userFriends')
    response_data = {"updatedResources": user.get_refresh_data() }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@home_bp.route('/api/information', methods=['GET'])
def handle_information():
    user = users.get_user(0)
    response_data = {
        "informations": user.userInformations
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')
