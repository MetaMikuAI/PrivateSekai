from flask import Blueprint, Response, current_app
from werkzeug.local import LocalProxy
import json

from config import DEBUG
from game.users import Users

debug_bp = Blueprint('debug', __name__)

users: Users = LocalProxy(lambda: current_app.users)  # type: ignore

@debug_bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return Response(status=204)

@debug_bp.route('/metamiku/debug/getUserList', methods=['GET'])
def handle_get_user_list():
    if not DEBUG:
        return Response("Debug mode is off", status=403)

    user_list = users.get_user_list()
    return Response(user_list, content_type='application/json')

@debug_bp.route('/metamiku/debug/getUserSuiteData/<int:user_id>', methods=['GET'])
def handle_get_user_suite_data(user_id: int):
    if not DEBUG:
        return Response("Debug mode is off", status=403)
    
    if not users.user_exists(user_id):
        return Response("User not found", status=404)

    user = users.get_user(user_id)
    response_data = user.get_suite_user_data()
    response_body = json.dumps(response_data, ensure_ascii=False)
    return Response(response_body, content_type='application/json')
