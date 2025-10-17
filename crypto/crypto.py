import msgpack
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from functools import wraps
from flask import request, Response

from config import key, iv

def decrypt_aes_cbc(data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
    return decrypted_data

def encrypt_aes_cbc(data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data


def encode_msgpack(data: dict) -> bytes:
    if data is None:
        raise ValueError("Input data for encode_msgpack cannot be None")
    packed = msgpack.packb(data, use_bin_type=True, use_single_float=True)
    if not isinstance(packed, bytes):
        raise TypeError("msgpack.packb did not return bytes")
    return packed

def decode_msgpack(data: bytes) -> dict:
    return msgpack.unpackb(data, raw=False)


def prsk_enc(data: dict) -> bytes:
    packed = encode_msgpack(data)
    encrypted = encrypt_aes_cbc(packed)
    return encrypted


def prsk_dec(data: bytes) -> dict:
    decrypted = decrypt_aes_cbc(data)
    decoded = decode_msgpack(decrypted)
    return decoded

