from utils import *
from pprint import pprint as pp
import requests, json, sys

access_token = get_access_token()
method = sys.argv[1]
server = sys.argv[2]
path = sys.argv[3]
url = 'https://%s.izettle.com/%s' % (server, path)
res = getattr(requests, method)(url, headers = {'Authorization': 'Bearer %s' % access_token})
pp((url, res))
pp(json.loads(res.text))
