# This is just a one-time use script to fetch suitemasterfile from the official server.
# You can ignore this file.
# some sensitive info like key, iv, cookie are removed. Please fill them yourself.

import requests
import json
import os
import msgpack

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

COOKIE = ''
key = b''
iv = b''

api_user_auth_path = 'template/api_user_auth.json'
with open(api_user_auth_path, 'r', encoding='utf-8') as f:
    api_user_auth = json.load(f)

suiteMasterSplitPath = api_user_auth['suiteMasterSplitPath']

api_url = lambda part: f'https://production-game-api.sekai.colorfulpalette.org/api/{part}'
# example: GET https://production-game-api.sekai.colorfulpalette.org/api/suitemasterfile/6.0.0.40/00_e26640afd7819a315cd4b13660b3431ea0a7365d3e0640b9129ac106ae82dfe5


def decrypt_aes_cbc(data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
    return decrypted_data

def decode_msgpack(data: bytes) -> dict:
    return msgpack.unpackb(data, raw=False)

def prsk_dec(data: bytes) -> dict:
    decrypted = decrypt_aes_cbc(data)
    decoded = decode_msgpack(decrypted)
    return decoded


dir_path = '/'.join(suiteMasterSplitPath[0].split('/')[0:2])
if os.path.exists(dir_path) is False:
    os.makedirs(dir_path)

for part in suiteMasterSplitPath:
    print(f'Downloading part {part}...')
    response = requests.get(api_url(part), headers={'Cookie': COOKIE})
    data = prsk_dec(response.content)
    with open(part, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
    print(f'Part {part} downloaded.')