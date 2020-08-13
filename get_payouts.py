from utils import *
from pprint import pprint as pp
import requests, json, sys, decimal
from datetime import datetime, timedelta

#organizations/self/accounts/LIQUID/transactions\?start=2020-08-01T00:00:00\&end=2020-08-14T00:00:00\&includeTransactionType=PAYOUT

if len(sys.argv) != 2:
    sys.stderr.write('Usage: %s <days>\n')
    sys.exit(1)
access_token = get_access_token()
offset = int(sys.argv[1])
start_date = (datetime.now() - timedelta(days = offset)).strftime('%Y-%m-%dT%H:%M:%S')
end_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
method = 'get'
server = 'finance'
path = 'organizations/self/accounts/LIQUID/transactions'
url = 'https://%s.izettle.com/%s' % (server, path)
res = getattr(requests, method)(url,
                                headers = {'Authorization': 'Bearer %s' % access_token},
                                params = {'start': start_date,
                                          'end': end_date,
                                          'includeTransactionType': 'PAYOUT'})
data = json.loads(res.text)
full_amount = decimal.Decimal(0)
for payout in data['data']:
    amount = decimal.Decimal(payout['amount']) * -1 / 100
    full_amount += amount
    print(payout['timestamp'], amount)
print("SUM:", full_amount)
