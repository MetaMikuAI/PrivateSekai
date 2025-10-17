from flask import Blueprint, Response, current_app
from werkzeug.local import LocalProxy

from game.users import Users

misc_bp = Blueprint('misc', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore

@misc_bp.route('/api/user/<int:user_id>/<uuid>', methods=['POST'])
def handel_a0030f53_41e9_4b52_a8a4_993b807d5869(user_id: int, uuid: str):
    return Response(status=200)