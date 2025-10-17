import jwt
from jwt import InvalidTokenError
from typing import Any, Dict
from typing import Optional
from uuid import uuid4
from base64 import urlsafe_b64encode, urlsafe_b64decode
import json

from config import jwt_key, jwt_alg, IGNORE_INVALID_CREDENTIAL

# TODO: 当前鉴权只检验合理性，并未绑定 userId 与 credential/sessionToken

def jwt_signature(payload: Dict, key: Optional[str] = None, algorithm: Optional[str] = None) -> str:
	if key is None:
		key = jwt_key
	if algorithm is None:
		algorithm = jwt_alg
	token = jwt.encode(payload, key, algorithm=algorithm)
	return token

def jwt_verify(token: str, key: Optional[str] = None, algorithms: Optional[list] = None) -> Optional[Dict[str, Any]]:
	if key is None:
		key = jwt_key
	if algorithms is None:
		algorithms = [jwt_alg]
	try:
		if IGNORE_INVALID_CREDENTIAL:
			return json.loads(urlsafe_b64decode(token.split(".")[1] + "===").decode())
		payload = jwt.decode(token, key, algorithms=algorithms)
		return payload
	except InvalidTokenError:
		return None

def gen_user_signature(user_id: int) -> str:
	payload = {
		"userId": user_id,
	}
	signature = jwt_signature(payload)

	# with SekaiDatabase() as db:
	# 	db.set_user_credential(user_id, signature)

	return signature

def gen_user_credential(user_id: int) -> Optional[str]:
	payload = {
		"credential": str(uuid4()),
		"userId": user_id
	}
	credential = jwt_signature(payload)
	# with SekaiDatabase() as db:
	# 	db.set_user_credential(user_id, credential)
	return credential

def verify_credential(credential: str, user_id: int) -> bool:
	if IGNORE_INVALID_CREDENTIAL:
		return True
	payload = jwt_verify(credential)
	if payload is None:
		return False
	if "userId" not in payload or payload["userId"] != user_id:
		return False
	# with SekaiDatabase() as db:
	# 	stored_credential = db.get_user_credential(user_id)
	# 	if stored_credential is None or stored_credential != credential:
	# 		return False
	return True

def gen_session_token(user_id: int) -> str:
	payload = {
		"userId": user_id,
		"sessionToken": str(uuid4())
	}
	session_token = jwt_signature(payload)
	# with SekaiDatabase() as db:
	# 	db.set_user_token(user_id, session_token)
	return session_token

def verify_session_token(session_token: str, user_id: int) -> bool:
	payload = jwt_verify(session_token)
	if payload is None:
		return False
	if "userId" not in payload or payload["userId"] != user_id:
		return False
	# with SekaiDatabase() as db:
	# 	stored_token = db.get_user_token(user_id)
	# 	if stored_token is None or stored_token != session_token:
	# 		return False
	return True