import requests
import base64
from decoder import decrypt_token 
class LineClient:
    def __init__(self, token ):
        decodeToken=decrypt_token(base64.b64decode(token.encode('utf-8'))).decode("utf-8").replace("\x05", "") 
        self.token=decodeToken
    def NotifyMessage(self,msg):
        headers = {
            "Authorization": "Bearer " + self.token, 
            "Content-Type" : "application/x-www-form-urlencoded"
        }
        
        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code
        
