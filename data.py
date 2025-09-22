import json
import time

# TODO: 我们可能需要一个 user 0, 新用户从此 fork

def get_user_by_id(user_id: int) -> dict:
    # 获取某用户的全部信息, 一般在登录时访问 /api/suite/user/<user_id>/ 时调用
    with open(f'data/users/{user_id}.json', 'r') as f:
        user = json.load(f)

    user['now'] = int(time.time() * 1000)
    return user

# 只检验引继码 ID 和密码以及过期时间, 返回 user_id 或 None
def check_user_inherit(inherit_id: str, password: str) -> int | None:
    with open(f'data/inherits.json', 'r') as f:
        inherits = json.load(f)

    for inherit in inherits:
        if inherit['inheritId'] == inherit_id and inherit['password'] == password and inherit['expiredAt'] > int(time.time() * 1000):
            return inherit['userId']

# 设置引继码, 若已有则应覆盖
def add_user_inherit(user_id: int, inherit_id: str, password: str):
    with open(f'data/inherits.json', 'r') as f:
        inherits = json.load(f)

    now = int(time.time() * 1000)
    ONE_MONTH = 30 * 24 * 60 * 60 * 1000
    new_inherit = {
        'userId': user_id,
        'inheritId': inherit_id,
        'password': password,
        'createdAt': now,
        'expiredAt': now + ONE_MONTH
    }

    index = next((i for i, inherit in enumerate(inherits) if inherit['inheritId'] == inherit_id), None)
    if index is not None:
        inherits[index] = new_inherit
    else:
        inherits.append(new_inherit)

    with open(f'data/inherit.json', 'w') as f:
        json.dump(inherits, f, indent=4)

# 清理过期引继码, 不过可能用不上
def clean_expired_inherits():
    with open(f'data/inherits.json', 'r') as f:
        inherits = json.load(f)

    now = int(time.time() * 1000)
    inherits = [inherit for inherit in inherits if inherit['expiredAt'] > now]
    # inherits = list(filter(lambda inherit: inherit['expiredAt'] > now, inherits))

    with open(f'data/inherits.json', 'w') as f:
        json.dump(inherits, f, indent=4)

# /api/inherit/user/<inherit_id> 应返回简要信息
def get_inherit_info(user_id: int, is_execute_inherit: bool) -> dict:
    with open(f'data/{user_id}.json', 'r') as f:
        user = json.load(f)
    
    data = {
        "afterUserGamedata": {
            "userId": user["userGamedata"]["userId"],
            "name": user["userGamedata"]['name'],
            "deck": user["userGamedata"]['deck'],
            "rank": user["userGamedata"]['rank']
        },
        "userEventDeviceTransferRestrict": {
            "isRestrictDeviceTransfer": False
        }
    }
    
    # 继承引继码时, 应当分发新的引继码
    if is_execute_inherit:
        data["credential"] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjcmVkZW50aWFsIjoiYWFiNjU1ZWMtYWIyNi00N2M4LTg5ZTYtYmZlNDVhZTg1ZDUzIiwidXNlcklkIjoiNDU4MTcyNjI3NDQzODE4NTAxIn0.crdTPK0sPUn-LDcg9MiJyYr4u4-yaWGuH_kgvuCd1EE"
    # TODO: 尚不清楚 JWT 的构造, 此处暂时使用重放

    return data
