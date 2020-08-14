from utils import *
from pprint import pprint as pp
from datetime import datetime, timedelta
import requests, json, sys, pytz

products_to_display = {'b845d390-a4f8-11ea-8f9b-5ca8cba5baac',
                       'f13f3660-19dd-11ea-b6e8-50ad43873b88',
                       '97673920-19de-11ea-8e77-1247b74fae1c',
                       'bf1f4380-19df-11ea-b3a0-e478aaa6c22a',
                       '6a51c060-19e1-11ea-aebc-960f77e91a0b'}

access_token = get_access_token()
short = False if len(sys.argv) < 2 or sys.argv[1] != 'short' else True
offset = 0
start_date = (datetime.now() - timedelta(days = offset)).strftime('%Y-%m-%d')
timezone = pytz.timezone('Europe/Oslo')

res = requests.get('https://purchase.izettle.com/purchases/v2',
                   headers = {'Authorization': 'Bearer %s' % access_token},
                   params = {'startDate': start_date})
purchases_list = json.loads(res.text)['purchases']

def print_purchases(purchases_list):
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
    print(json.dumps(print_purchases(purchases_list)))
