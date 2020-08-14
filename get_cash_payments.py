from utils import *
from pprint import pprint as pp
import requests, json, sys, decimal
from datetime import datetime, timedelta

if len(sys.argv) != 3:
    sys.stderr.write('Usage: %s <days> <previous amount>\n')
    sys.exit(1)
access_token = get_access_token()
offset = int(sys.argv[1])
prev_amount = decimal.Decimal(sys.argv[2])
start_date = (datetime.now() - timedelta(days = offset)).strftime('%Y-%m-%d')
method = 'get'
server = 'purchase'
path = 'purchases/v2'
url = 'https://%s.izettle.com/%s' % (server, path)
res = getattr(requests, method)(url,
                                headers = {'Authorization': 'Bearer %s' % access_token},
                                params = {'startDate': start_date})
data = json.loads(res.text)
full_amount = decimal.Decimal(0)
print(start_date, "IN KASSE:", "%6.2f" % prev_amount)
for purchase in data['purchases']:
    cash = False;
    date_created = datetime.strptime(purchase['created'].replace('+0000', ''), '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M')
    amount = decimal.Decimal(purchase['amount']);
    handout = decimal.Decimal(0)
    change = decimal.Decimal(0)
    for payment in purchase['payments']:
        if payment['type'] == 'IZETTLE_CASH':
            cash = True
            handout += payment['attributes']['handedAmount']
            if 'changeAmount' in payment['attributes']:
                change += payment['attributes']['changeAmount']
    if cash:
        full_amount += amount
        print("%s % 7s % 7s % 7s" % (date_created,
                                     "%6.2f" % (amount / 100),
                                     "%6.2f" % (handout / 100),
                                     "%6.2f" % (change / 100)))
print("SUM AMOUNT:", "%6.2f" % (full_amount / 100))
print("OUT KASSE:", "%6.2f" % (prev_amount + (full_amount / 100)))
