from utils import *
from pprint import pprint as pp
from datetime import datetime, timedelta
import requests, json, sys, pytz, time, os, hashlib

products_to_display = {'b845d390-a4f8-11ea-8f9b-5ca8cba5baac',
                       'f13f3660-19dd-11ea-b6e8-50ad43873b88',
                       '97673920-19de-11ea-8e77-1247b74fae1c',
                       'bf1f4380-19df-11ea-b3a0-e478aaa6c22a',
                       '6a51c060-19e1-11ea-aebc-960f77e91a0b'}

try: out_file = sys.argv[1]
except: out_file = 'kooking.data'
access_token = None
access_token_usage = 100
timezone = pytz.timezone('Europe/Oslo')

def get_purchases():
    global access_token_usage, access_token
    if access_token_usage >= 100:
        access_token = get_access_token()
        access_token_usage = 0
    else: access_token_usage += 1
    start_date = datetime.now().strftime('%Y-%m-%d')
    res = requests.get('https://purchase.izettle.com/purchases/v2',
                       headers = {'Authorization': 'Bearer %s' % access_token},
                       params = {'startDate': start_date})
    return json.loads(res.text)['purchases']

def kooking_purchases(purchases_list):
    ret = []
    for purchase in purchases_list:
        for product in purchase['products']:
            if 'productUuid' in product and product['productUuid'] in products_to_display:
                timestamp = datetime.strptime(purchase['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
                ts = timestamp.astimezone(timezone).isoformat()
                ret.append({'ts': ts,
                            'purchase': purchase['purchaseUUID'],
                            'product': product['productUuid'],
                            'name': product['name']})
    return ret
                
if __name__ == '__main__':
    while True:
        try:
            data = kooking_purchases(get_purchases())
            print(time.asctime(), hashlib.sha1(access_token.encode('utf-8')).hexdigest(), 'purchases:', len(data))
            with open(out_file + '.tmp', 'w') as fd:
                fd.write(json.dumps(data))
            os.rename(out_file + '.tmp', out_file)
        except Exception as err:
            print(time.asctime(), repr(err))
        time.sleep(5)
