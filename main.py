import os
import time
from flask import Flask, request, Response, jsonify

from user import *
from config import logger
from utils import load_json
from crypto import prsk_enc, prsk_dec
from signature import verify_credential, gen_session_token, jwt_verify, gen_user_credential

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_general_error(e: Exception):
    logger.exception(f"An error occurred: {str(e)}")
    return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500


@app.route('/api/user', methods=['POST'])
def handle_register_user():
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)
    
    user_id = create_new_user(user_id = None, device_info=request_data)
    logger.info(f"New user registered: ID={user_id}")
    suite_user_data = get_suite_user_data(user_id)
    response_data = {
        "userRegistration": suite_user_data["userRegistration"],
        "credential": gen_user_credential(user_id),
        "updatedResources": suite_user_data
    }
    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')


@app.route('/api/user/<int:user_id>/<uuid>', methods=['POST'])
def handel_a0030f53_41e9_4b52_a8a4_993b807d5869(user_id: int, uuid: str):
    return Response(status=200)


# 这里游戏客户端通过本地保存的 credential 来与服务器交换得到 sessionToken(一次一密)
@app.route('/api/user/<int:user_id>/auth', methods=['PUT'])
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

    response_data = load_json('template/api_user_auth.json')
    response_data['sessionToken'] = gen_session_token(user_id)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@app.route('/api/system', methods=['GET'])
def handle_system_info():
    response_data = load_json('template/api_system.json')
    response_data['serverDate'] = int(time.time() * 1000)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@app.route('/api/suite/user/<int:user_id>', methods=['GET'])
def handle_suite_user(user_id: int):
    response_data = get_suite_user_data(user_id)
    if response_data["userRegistration"] is None:
        response_data = get_suite_user_data(user_id=0)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@app.route('/api/suitemasterfile/<version>/<path:filename>', methods=['GET'])
def handle_suitemasterfile(version: str, filename: str):
    base_path = f'suitemasterfile/{version}'
    file_path = os.path.join(base_path, filename)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return Response("Not Found", status=404)
    
    data = load_json(file_path)
    file_data = prsk_enc(data)

    response = Response(file_data, content_type='application/octet-stream')
    return response


@app.route('/api/user/<int:user_id>/tutorial', methods=['PATCH']) # 施工中
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
    logger.info(f"User {user_id} updated tutorial status to {tutorial_status}")

    response_data = get_user_refresh(user_id)
    response_data["updatedResources"]

    rtypes = update_tutorial_status(user_id, tutorial_status)
    response_data = get_user_refresh(user_id, rtypes)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


@app.route('/api/user/<int:user_id>', methods=['PATCH'])
def handle_user_update(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    request_data = prsk_dec(body)

    if 'userGamedata' not in request_data:
        logger.error("Missing 'userGamedata' in request data")
        return Response("Bad Request: Missing userGamedata", status=400)

    rtypes = update_user_gamedata(user_id, request_data['userGamedata'])
    response_data = get_user_refresh(user_id, rtypes)
    logger.info(f"User {user_id} gamedata updated")

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# POST /api/user/<int:user_id>/deactivate
@app.route('/api/user/<int:user_id>/deactivate', methods=['POST'])
def handle_user_deactivate(user_id: int):
    logger.info(f"User {user_id} deactivated")
    return Response(status=200)


# /api/user/1/home/refresh
@app.route('/api/user/<int:user_id>/home/refresh', methods=['PUT'])
def handle_user_home_refresh(user_id: int):
    body = request.get_data()
    
    if body is None or len(body) == 0:
        logger.error("Received empty request body")
        return Response("Bad Request: Empty body", status=400)
    
    # request_data = prsk_dec(body)

    response_data = get_user_refresh(user_id)
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# GET /api/user/<userId>/restrict-info
@app.route('/api/user/<int:user_id>/restrict-info', methods=['GET'])
def handle_user_restrict_info(user_id: int):
    response_data = {
        "isRestrictDeviceTransfer": False
    }
    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# PUT /api/user/<userId>/inherit
@app.route('/api/user/<int:user_id>/inherit', methods=['PUT'])
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
    inherit_id = set_user_inherit(user_id, password)
    rtypes = {"userInherit"}

    logger.info(f"User {user_id} set inherit ID {inherit_id}")
    response_data = {
        "inheritId": inherit_id
    }

    response_data = get_user_refresh(user_id, rtypes)
    response_data["userInherit"] = {
        "inheritId": inherit_id,
    }

    response_body = prsk_enc(response_data)
    return Response(response_body, content_type='application/octet-stream')


# POST /api/inherit/user/inheritId?isExecuteInherit=False
@app.route('/api/inherit/user/<string:inherit_id>', methods=['POST'])
def handle_inherit_user(inherit_id: str):
    if 'isExecuteInherit' not in request.args:
        logger.error("Missing 'isExecuteInherit' parameter")
        return Response("Bad Request: Missing isExecuteInherit parameter", status=400)
    
    is_execute_inherit = request.args.get('isExecuteInherit')
    if is_execute_inherit not in ['True', 'False']:
        logger.error("Invalid 'isExecuteInherit' parameter value")
        return Response("Bad Request: Invalid isExecuteInherit parameter value", status=400)

    # body = request.get_data()
    # assert body == bytes.fromhex('ffa3bd6214f33fe73cb72fee2262bedb')

    inherit_token = request.headers.get('X-Inherit-Id-Verify-Token')
    if inherit_token is None:
        logger.error("Missing 'X-Inherit-Id-Verify-Token' header")
        return Response("Bad Request: Missing X-Inherit-Id-Verify-Token header", status=400)
    
    inherit_data = jwt_verify(inherit_token)
    if inherit_data is None or 'inheritId' not in inherit_data or inherit_data['inheritId'] != inherit_id:
        logger.error("Invalid inherit token or inherit ID mismatch")
        return Response("Unauthorized: Invalid inherit token or inherit ID mismatch", status=401)

    if 'password' not in inherit_data:
        logger.error("Missing 'password' in request data")
        return Response("Bad Request: Missing password", status=400)
    
    password = inherit_data['password']
    user_id = verify_user_inherit(inherit_id, password)
    if user_id is None:
        logger.error(f"Invalid inherit ID or password for inherit ID {inherit_id}")
        return Response("Unauthorized: Invalid inherit ID or password", status=401)

    logger.info(f"User {user_id} inherited account with inherit ID {inherit_id}")
    suite_user_data = get_suite_user_data(user_id)
    response_data = {
        "afterUserGamedata": get_after_user_gamedata(user_id),
        "userEventDeviceTransferRestrict": {
            "isRestrictDeviceTransfer": False
        }
    }

    if is_execute_inherit == 'True':
        response_data["credential"] = gen_user_credential(user_id)

    response_body = prsk_enc(response_data)

    return Response(response_body, content_type='application/octet-stream')


if __name__ == '__main__':
    if not os.path.exists("sekai-master-db-diff"): # very IMPORTANT
        logger.error("sekai-master-db-diff directory not found! Please clone it from https://github.com/Sekai-World/sekai-master-db-diff.git")
        raise FileNotFoundError("sekai-master-db-diff directory not found.")

    if not os.path.exists("sekai.db"):
        logger.info("sekai.db not found, creating new database...")
        create_default_user()
        logger.info("Database and default user created.")

    print("Private Sekai is running on 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)