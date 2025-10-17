from flask import Blueprint, Response, current_app, request
from werkzeug.local import LocalProxy

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec
from crypto.signature import jwt_verify, gen_user_credential

inherit_bp = Blueprint('inherit', __name__)
users = LocalProxy(lambda: current_app.users)  # type: ignore


@inherit_bp.route('/api/user/<int:user_id>/restrict-info', methods=['GET'])
def handle_user_restrict_info(user_id: int):
    response_data = {
        "isRestrictDeviceTransfer": False
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@inherit_bp.route('/api/user/<int:user_id>/inherit', methods=['PUT'])
def handle_user_inherit(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)

    if 'password' not in request_data:
        logger.error("Missing 'password' in request data")
        return Response("Bad Request: Missing password", status=400)
    
    password = request_data['password']
    user = users.get_user(user_id)
    inherit_id = user.set_user_inherit(password)

    logger.info(f"User {user_id} set inherit ID {inherit_id}")
    response_data = {
        'inheritId': inherit_id
    }

    response_data = {'updatedResources': user.get_refresh_data()}
    response_data['userInherit'] = {
        'inheritId': inherit_id
    }

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')

@inherit_bp.route('/api/inherit/user/<string:inherit_id>', methods=['POST'])
def handle_inherit_user(inherit_id: str):
    if 'isExecuteInherit' not in request.args:
        logger.error("Missing 'isExecuteInherit' parameter")
        return Response("Bad Request: Missing isExecuteInherit parameter", status=400)
    
    is_execute_inherit = request.args.get('isExecuteInherit')
    if is_execute_inherit not in ['True', 'False']:
        logger.error("Invalid 'isExecuteInherit' parameter value")
        return Response("Bad Request: Invalid isExecuteInherit parameter value", status=400)

    # body = request.get_data()
    # assert body == MAGIC_BYTES

    inherit_token = request.headers.get('X-Inherit-Id-Verify-Token')
    if inherit_token is None:
        logger.error("Missing 'X-Inherit-Id-Verify-Token' header")
        return Response("Bad Request: Missing X-Inherit-Id-Verify-Token header", status=400)
    
    inherit_data = jwt_verify(inherit_token)
    if inherit_data is None or 'inheritId' not in inherit_data or inherit_data['inheritId'] != inherit_id:
        logger.error("Invalid inherit token or inherit ID mismatch")
        return Response("Unauthorized: Invalid inherit token or inherit ID mismatch", status=401)
        # TODO: replace with the true error response

    if 'password' not in inherit_data:
        logger.error("Missing 'password' in request data")
        return Response("Bad Request: Missing password", status=400)
    
    password = inherit_data['password']
    # user_id = verify_user_inherit(inherit_id, password)

    for user_id, user in users:
        if user.verify_inherit(inherit_id, password):
            break
    else:
        user_id = None
        logger.warning(f"Inherit ID {inherit_id} with provided password not found")
        return Response("Unauthorized: Invalid inherit ID or password", status=401)
    
    user = users.get_user(user_id)
    logger.info(f"User {user_id} inherited account with inherit ID {inherit_id}")
    response_data = {
        "afterUserGamedata": user.get_after_user_gamedata(),
        "userEventDeviceTransferRestrict": {
            "isRestrictDeviceTransfer": False
        }
    }

    if is_execute_inherit == 'True':
        response_data["credential"] = gen_user_credential(user_id)

    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')