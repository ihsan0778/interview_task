from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from django.conf import settings

# Padding function for AES
def pad(data):
    block_size = AES.block_size
    if len(data) % block_size == 0:
        return data
    return data + (block_size - len(data) % block_size) * chr(block_size - len(data) % block_size).encode()

# Unpadding function for AES
def unpad(data):
    return data[:-ord(data[-1:])]

def encrypt_data(data):
    key = settings.AES_ENCRYPTION_KEY.encode()
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode()))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    return {'iv': iv, 'ciphertext': ct}

def decrypt_data(enc_data):
    print(settings.AES_ENCRYPTION_KEY)
    key = settings.AES_ENCRYPTION_KEY.encode()
    iv = b64decode(enc_data['iv'])
    ct = b64decode(enc_data['ciphertext'])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct))
    return pt.decode('utf-8')
