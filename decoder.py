from Crypto.Cipher import AES
import base64
 
 
def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size) 
def _cipher():
    key = 'wantleavechtfuck'
    iv = 'wantleavechtfuck'
    return AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
 
def encrypt_token(data):
    return _cipher().encrypt(_pad(data))
    
def decrypt_token(data):
    return _cipher().decrypt(data)
 
# t=base64.b64encode(encrypt_token('Zig9VFkOprykdW9alMG2wlBpgmB0hlnA6pKacw1ObHs')).decode("utf-8") 
# t2=decrypt_token(base64.b64decode(b'Ri8yf+9qTihDpRjSa9V6BPuhT8I2SOtPbcG1TxV0HgWqhME6yqvseeMSdYqTPThV'))
