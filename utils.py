from config import *
import requests, json, re

def latex(s):
    return re.sub(r'\s*&\s*', r' og ', s)

def get_access_token():
    res = requests.post('https://oauth.izettle.com/token',
                        data = {'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                'client_id': CLIENT_ID,
                                'assertion': ASSERTION},
                        headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    return json.loads(res.text)['access_token']
