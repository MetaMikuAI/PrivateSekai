from flask import Blueprint, Response, current_app, request
from werkzeug.local import LocalProxy
import time

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec
from crypto.signature import verify_credential, gen_session_token, jwt_verify, gen_user_credential
from config import api_user_auth, api_system

auth_bp = Blueprint('auth', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


# 这里游戏客户端通过本地保存的 credential 来与服务器交换得到 sessionToken(一次一密)
@auth_bp.route('/api/user/<int:user_id>/auth', methods=['PUT'])
def handle_auth_user(user_id: int):
    if 'refreshUpdatedResources' in request.args and request.args.get('refreshUpdatedResources') != 'False':
        logger.warning("Unsupported parameter 'refreshUpdatedResources' is not 'False'")
    
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)

    if 'credential' not in request_data:
        logger.error("Missing 'credential' in request data")
        return Response("Bad Request: Missing credential", status=400)

    credential = request_data['credential']
    if not verify_credential(credential, user_id):
        logger.error(f"Invalid credential for user {user_id}")
        return Response("Unauthorized: Invalid credential", status=401)

    logger.info(f"User {user_id} authenticated with credential {credential}")

    response_data = api_user_auth
    
    response_data['sessionToken'] = gen_session_token(user_id)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@auth_bp.route('/api/system', methods=['GET'])
def handle_system_info():
    response_data = api_system
    response_data['serverDate'] = int(time.time() * 1000)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')