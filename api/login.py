from flask import Blueprint, Response, current_app, request
from werkzeug.local import LocalProxy

from game.users import Users
from config import logger
from crypto.crypto import prsk_dec, prsk_enc
from crypto.signature import gen_user_credential

login_bp = Blueprint('login', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


@login_bp.route('/api/user', methods=['POST'])
def handle_register_user():
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)
    
    user_id = users.fork_new_user()
    user = users.get_user(user_id)
    logger.info(f"New user registered: ID={user_id}")
    suite_user_data = user.get_suite_user_data()
    response_data = {
        "userRegistration": suite_user_data["userRegistration"],
        "credential": gen_user_credential(user_id),
        "updatedResources": suite_user_data
    }
    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')


@login_bp.route('/api/suite/user/<int:user_id>', methods=['GET'])
def handle_suite_user(user_id: int):
    if not users.user_exists(user_id): # only for deactivated user
        user = users.get_user(0) 
    else: 
        user = users.get_user(user_id)
    
    response_data = user.get_suite_user_data()
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')