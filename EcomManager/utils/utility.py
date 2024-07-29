import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv
from django.utils.encoding import force_str
load_dotenv()

AES_SECRET_KEY = bytes(os.getenv('AES_SECRET_KEY'), 'utf-8')
AES_IV = bytes(os.getenv('AES_IV'), 'utf-8')

def encrypt_data(plaintext):
    cipher = AES.new(AES_SECRET_KEY, AES.MODE_CBC, AES_IV)
    padded_plaintext = pad(plaintext.encode(), 16)
    ciphertext = cipher.encrypt(padded_plaintext)
    return base64.b64encode(ciphertext).decode()
def decrypt_data(encrypted_data):
    cipher = AES.new(AES_SECRET_KEY, AES.MODE_CBC, AES_IV)
    decoded_data = base64.b64decode(encrypted_data)
    try:
        decrypted_data = unpad(cipher.decrypt(decoded_data), 16)
    except ValueError as e:
        # Print the debug information
        print(f"Decryption failed: {str(e)}")
        print(f"Ciphertext: {decoded_data}")
        print(f"Key: {AES_SECRET_KEY}")
        print(f"IV: {AES_IV}")
        raise
    return decrypted_data.decode('utf-8')


def encrypt_object_fields(obj):
    encrypted_data = {}
    
    for field in obj._meta.fields:
        field_name = field.name
        value = getattr(obj, field_name)
        
        if value is not None and not callable(value):
            try:
                encrypted_data[field_name] = encrypt_data(force_str(value))
            except Exception as e:
                print(f"Encryption failed for {field_name}: {e}")
                encrypted_data[field_name] = None

    return encrypted_data
def decrypt_object_fields(encrypted_obj):
    decrypted_obj = {}
    
    for field, value in encrypted_obj.items():
        if isinstance(value, str):
            decrypted_obj[field] = decrypt_data(value)
        else:
            decrypted_obj[field] = value  # Or handle other types appropriately
    
    return decrypted_obj