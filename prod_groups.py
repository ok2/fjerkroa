from utils import *
from pprint import pprint as pp
import requests, json

access_token = get_access_token()

res = requests.get('https://products.izettle.com/organizations/self/categories/v2',
                   headers = {'Authorization': 'Bearer %s' % access_token})
pp(json.loads(res.text))

res = requests.get('https://products.izettle.com/organizations/self/products/v2',
                   headers = {'Authorization': 'Bearer %s' % access_token})
pp(json.loads(res.text))
