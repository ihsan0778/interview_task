import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

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

class EncryptionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST':
            try:
                import pdb
                pdb.set_trace()
                decrypted_data = decrypt_data(request.body.decode())
                request._body = decrypted_data.encode()
                request.POST = json.loads(decrypted_data)
            except Exception as e:
                logger.error(f"Decryption error: {str(e)}")
                return JsonResponse({'error': 'Decryption error', 'message': str(e)}, status=400)

    def process_response(self, request, response):
        try:
            if response['Content-Type'] == 'application/json':
                encrypted_data = encrypt_data(response.content.decode())
                response.content = encrypted_data
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
        return response
