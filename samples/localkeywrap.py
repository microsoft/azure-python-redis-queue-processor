# Load modules
import base64

from azure.keyvault import KeyVaultClient
from azure.common.credentials import ServicePrincipalCredentials

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives import hashes

# Tests only
import random, string

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def bytes_to_int(bytes):
    result = 0

    for b in bytes:
        result = result * 256 + ord(b)

    return result

def wrap_aes_key(aes_key, public_json_key):
    int_n = bytes_to_int(json_key.n)
    int_e = bytes_to_int(json_key.e)
    public_numbers = RSAPublicNumbers(int_e, int_n)
    public_key = public_numbers.public_key(default_backend())

    wrapped_key = public_key.encrypt(aes_key, padding.OAEP(
                                                        mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                                        algorithm=hashes.SHA1(),
                                                        label=None))
    return wrapped_key    

# Azure setup
aes_key = ''

azure_vault = ''
credentials = ServicePrincipalCredentials(
    client_id = '',
    secret = '',
    tenant = '',
)

client = KeyVaultClient(
    credentials
)

key_bundle = client.get_key(azure_vault, '', '')
json_key = key_bundle.key

for i in range(100):
    key = randomword(24)
    wrapped_key = wrap_aes_key(key, json_key)
    restored_aes_key = client.unwrap_key(azure_vault, '', '', 'RSA-OAEP', wrapped_key)
    if key != restored_aes_key.result:
        print("==========================")
        print(key)
        print("--------------------------")
        print(restored_aes_key.result)
        print("")
