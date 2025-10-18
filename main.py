import os
from flask import Flask, jsonify

from game.users import Users
from config import logger

from api.auth import auth_bp
from api.debug import debug_bp
from api.home import home_bp
from api.inherit import inherit_bp
from api.login import login_bp
from api.misc import misc_bp
from api.present import present_bp
from api.story import story_bp
from api.suitemasterfile import suitemasterfile_bp
from api.tutorial import tutorial_bp

app = Flask(__name__)
app.users = Users() # type: ignore


@app.errorhandler(Exception)
def handle_general_error(e: Exception):
    logger.exception(f"An error occurred: {str(e)}")
    return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500

app.register_blueprint(auth_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(inherit_bp)
app.register_blueprint(home_bp)
app.register_blueprint(login_bp)
app.register_blueprint(misc_bp)
app.register_blueprint(present_bp)
app.register_blueprint(story_bp)
app.register_blueprint(suitemasterfile_bp)
app.register_blueprint(tutorial_bp)


if __name__ == '__main__':
    if not os.path.exists("sekai-master-db-diff"): # very IMPORTANT
        logger.error("sekai-master-db-diff directory not found! Please clone it from https://github.com/Sekai-World/sekai-master-db-diff.git")
        raise FileNotFoundError("sekai-master-db-diff directory not found.")

    print("Private Sekai is running on 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)