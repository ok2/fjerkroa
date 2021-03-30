from utils import *
from pprint import pprint as pp
import requests, json, sys, decimal, pytz
from datetime import datetime, timedelta

timezone = pytz.timezone('Europe/Oslo')
if (len(sys.argv) != 13 and len(sys.argv) != 6) \
   or (len(sys.argv) == 6 and sys.argv[4] != '-'):
    sys.stderr.write('Usage: %s <offset> <days> <previous amount> <500> <200> <100> <50> <20> <10> <5> <1> <removed>\n')
    sys.stderr.write('       %s <offset> <days> <previous amount> - <removed>\n')
    sys.exit(1)
access_token = get_access_token()
if len(sys.argv) == 13:
    sys_argv = sys.argv
else:
    sys_argv = sys.argv[:4]
    for line in sys.stdin.readlines():
        line = line.strip()
        if len(line) != 0:
            sys_argv.append(line)
    sys_argv.append(sys.argv[5])
offset = int(sys_argv[1])
days_number = int(sys_argv[2])
prev_amount = decimal.Decimal(sys_argv[3])
removed = decimal.Decimal(sys_argv[12])
cash_types = [500, 200, 100, 50, 20, 10, 5, 1, 1]
cash_amount = decimal.Decimal(0)
for cash_str in sys_argv[4:]:
    cash_type = cash_types.pop(0)
    if '=' in cash_str:
        cash_type, cash_str = cash_str.split('=')
        cash_type = int(cash_type)
    cash_amount += decimal.Decimal(cash_str) * cash_type
start_date = (datetime.now().replace(tzinfo = timezone) - timedelta(days = offset)).strftime('%Y-%m-%d')
stop_date = datetime.now().replace(tzinfo = timezone) - timedelta(days = offset) + timedelta(days = days_number)
method = 'get'
server = 'purchase'
path = 'purchases/v2'
url = 'https://%s.izettle.com/%s' % (server, path)
res = getattr(requests, method)(url,
                                headers = {'Authorization': 'Bearer %s' % access_token},
                                params = {'startDate': start_date})
data = json.loads(res.text)
last_date_created = None
full_amount = decimal.Decimal(0)
to_break = False
for purchase in data['purchases']:
    cash = False;
    try: timestamp = datetime.strptime(purchase['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
    except: timestamp = datetime.strptime(purchase['created'], '%Y-%m-%dT%H:%M:%S%z')
    if timestamp > stop_date: continue
    timestamp = timestamp.astimezone(timezone)
    date_created = timestamp.strftime('%Y-%m-%d')
    time_created = timestamp.strftime('%H:%M')
    amount = decimal.Decimal(purchase['amount']);
    handout = decimal.Decimal(0)
    change = decimal.Decimal(0)
    for payment in purchase['payments']:
        if payment['type'] == 'IZETTLE_CASH':
            cash = True
            handout += payment['attributes']['handedAmount']
            if 'changeAmount' in payment['attributes']:
                change += payment['attributes']['changeAmount']
    if cash and amount > 0:
        if last_date_created != date_created and (full_amount > 0 or last_date_created is None):
            if last_date_created is not None:
                print("SUM AMOUNT:", "%7.0f" % (full_amount / 100))
                print("OUT KASSE: ", "%7.0f" % (prev_amount + (full_amount / 100)), "\n")
            prev_amount = prev_amount + (full_amount/100)
            print(date_created, "IN KASSE:", "%7.0f" % prev_amount)
            full_amount = decimal.Decimal(0)
            last_date_created = date_created
        full_amount += amount
        print("%s %s % 8s % 8s % 8s" % (date_created, time_created,
                                        "%7.0f" % (amount / 100),
                                        "%7.0f" % (handout / 100),
                                        "%7.0f" % (change / 100)))
print("SUM AMOUNT:", "%7.0f" % (full_amount / 100))
new_amount = prev_amount + (full_amount / 100)
print("OUT KASSE: ", "%7.0f" % new_amount)
print("\nREAL STATE:", "%7.0f-%7.0f=%7.0f" % (cash_amount, removed, cash_amount-removed))
print("DIFFERENCE:", "%7.0f" % (cash_amount - new_amount))
