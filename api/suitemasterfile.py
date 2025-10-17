import os
import json
from flask import Blueprint, Response, current_app
from werkzeug.local import LocalProxy

from config import DEBUG, logger
from game.users import Users
from crypto.crypto import prsk_enc, prsk_dec

suitemasterfile_bp = Blueprint('suitemasterfile', __name__)
users: Users = LocalProxy(lambda: current_app.users)  # type: ignore


@suitemasterfile_bp.route('/api/suitemasterfile/<version>/<path:filename>', methods=['GET'])
def handle_suitemasterfile(version: str, filename: str):
    base_path = f'suitemasterfile/{version}'
    file_path = os.path.join(base_path, filename)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return Response("Not Found", status=404)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from file: {file_path}")
            return Response("Internal Server Error: Failed to decode JSON", status=500)
        
    file_data = prsk_enc(data)

    response = Response(file_data, content_type='application/octet-stream')
    return response