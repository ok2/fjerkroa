from utils import *
from pprint import pprint as pp
from datetime import datetime, timedelta
import requests, json, sys, pytz, time, os, hashlib, string

products_to_display = {
    '0be85e70-1cf3-11ea-ab6c-796ce77a8c54',
    '0bf4d9c0-d6fc-11ea-ba2d-82f22241f0cf',
    '2a8b3be0-1cf3-11ea-810d-636cc28e0a01',
    '2cce79c0-1a01-11ea-be2f-cea2e83b0f02',
    '49ba53c0-1cf3-11ea-a453-0cdfacad4f21',
    '636cd950-1cf3-11ea-83fa-6c8442b24f2a',
    '6a51c060-19e1-11ea-aebc-960f77e91a0b',
    '6fde1f40-19e3-11ea-b659-a2716e21a90e',
    '90b43020-1cf3-11ea-8616-51cbb4a16783',
    '97673920-19de-11ea-8e77-1247b74fae1c',
    'ab248f10-19e0-11ea-90e5-e9295c94209a',
    'ae158ce0-1cf3-11ea-a579-32cfd65eab6b',
    'b845d390-a4f8-11ea-8f9b-5ca8cba5baac',
    'bf1f4380-19df-11ea-b3a0-e478aaa6c22a',
    'f13f3660-19dd-11ea-b6e8-50ad43873b88',
}

try: out_file = sys.argv[1]
except: out_file = 'kooking.data'
access_token = None
access_token_limit = 1000
access_token_usage = access_token_limit
timezone = pytz.timezone('Europe/Oslo')

def get_purchases(offset = 0):
    global access_token_usage, access_token
    if access_token_usage >= access_token_limit:
        access_token = get_access_token()
        access_token_usage = 0
    else: access_token_usage += 1
    start_date = (datetime.now() - timedelta(days = offset)).strftime('%Y-%m-%d')
    res = requests.get('https://purchase.izettle.com/purchases/v2',
                       headers = {'Authorization': 'Bearer %s' % access_token},
                       params = {'startDate': start_date})
    response = json.loads(res.text)
    if 'purchases' not in response:
        if ret.get('errorType', '') == 'ACCESS_TOKEN_EXPIRED':
            access_token_usage = access_token_limit
            return get_purchases(offset)
        pp(response)
        raise RuntimeError('Got wrong response!')
    return response['purchases']

def kooking_purchases(purchases_list):
    ret = []; setnum = 0;
    for purchase in purchases_list:
        found = False; prodnum = 0; prodquant = 0
        for product in purchase['products']:
            if 'productUuid' in product and product['productUuid'] in products_to_display:
                found = True
                prodquant += int(product['quantity'])
        if not found: continue
        setnum += 1
        setletter = string.ascii_letters[setnum % len(string.ascii_letters)]
        for product in purchase['products']:
            if 'productUuid' in product and product['productUuid'] in products_to_display:
                timestamp = datetime.strptime(purchase['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
                ts = timestamp.astimezone(timezone).isoformat()
                quantity = int(product['quantity'])
                for num in range(quantity):
                    prodnum += 1
                    ret.append({'ts': ts,
                                'purchase': purchase['purchaseUUID'],
                                'product': product['productUuid'],
                                'variant': product['variantUuid'],
                                'variant_name': product['variantName'],
                                'setnum': setnum,
                                'setletter': setletter,
                                'num': num,
                                'quantity': quantity,
                                'prodnum': prodnum,
                                'prodquant': prodquant,
                                'description': product['description'],
                                'comment': product.get('comment', ''),
                                'name': product['name']})
    return ret

def kooking_service(out_file, offset = 2):
    last_token, last_purchases = None, None
    while True:
        try:
            data = kooking_purchases(get_purchases(offset = offset))
            cur_token, cur_purchases = hashlib.sha1(access_token.encode('utf-8')).hexdigest(), len(data)
            if (cur_token, cur_purchases) != (last_token, last_purchases):
                last_token, last_purchases = cur_token, cur_purchases
                print(time.asctime(), cur_token, 'purchases:', cur_purchases)
            with open(out_file + '.tmp', 'w') as fd:
                fd.write(json.dumps(data))
            os.rename(out_file + '.tmp', out_file)
        except Exception as err:
            print(time.asctime(), repr(err))
        sys.stdout.flush()
        time.sleep(5)

if __name__ == '__main__':
    kooking_service(out_file)
