from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging
import base64

logger = logging.getLogger(__name__)
from django.http import JsonResponse

AES_KEY = settings.AES_KEY
def encrypt_data(data):
    cipher = AES.new(AES_KEY,  AES.MODE_EAX)
    encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_data(data):
    cipher = AES.new(AES_KEY,  AES.MODE_EAX)
    decoded_data = base64.b64decode(data)
    decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
    return decrypted_data.decode('utf-8')