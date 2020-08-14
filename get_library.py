from utils import *
from pprint import pprint as pp
import requests, json, sys

access_token = get_access_token()
short = False if len(sys.argv) < 2 or sys.argv[1] != 'short' else True

res = requests.get('https://products.izettle.com/organizations/self/products/v2',
                   headers = {'Authorization': 'Bearer %s' % access_token})

def print_products(short):
    for product in json.loads(res.text):
        if short:
            price = 0
            for variant in product['variants']:
                price = variant['price']['amount'] / 100
            if product['category'] is None: category = ''
            else: category = product['category']['name']
            name = product['name']
            uuid = product['uuid']
            print(f'{uuid} {category=} {name=} {price=}')
        else:
            pp(product)

if __name__ == '__main__':
    print_products(short)
