from flask import Blueprint, Response, request, current_app
from werkzeug.local import LocalProxy

from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec
from typing import Any

present_bp = Blueprint('present', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


@present_bp.route('/api/user/<int:user_id>/present/history', methods=['GET'])
def handle_user_present_history(user_id: int):
    user = users.get_user(user_id)

    response_data: dict[str, Any] = {
        "userPresentHistories": user.get_present_history()
    }
    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')

@present_bp.route('/api/user/<int:user_id>/present', methods=['POST'])
def handle_user_present(user_id: int):
    user = users.get_user(user_id)

    present_data = prsk_dec(request.data)
    received_user_presents = user.receive_present(present_data.get("presentIds", []))
    
    response_data: dict[str, Any] = {
        "updatedResources": user.get_refresh_data(),
        "receivedUserPresents": received_user_presents
    }

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')