from utils import *
from pprint import pprint as pp
import requests, json

DESCRIPTIONS = {'7f2dc940-d73f-11ea-9281-6b34ea01d17c': {'description': 'øl, sprite'},
                'b7c0e930-192c-11ea-b9a3-907efee5668f': {'description': 'whiskey, brunt sukker, kaffe, krem'},
                '69d35330-d73f-11ea-9281-6b34ea01d17c': {'description': 'captain morgan, cola'},
                '760545f0-d73f-11ea-9281-6b34ea01d17c': {'description': 'øl, cola'},
                'ea7f0ac0-d73e-11ea-8772-ab6a47ea4e3f': {'description': 'vodka, piscang ambon, sprite'},
                '533a42a0-d73f-11ea-9281-6b34ea01d17c': {'description': 'bacardi, sprite'},

                '11cb92ee-26ac-11eb-8a1b-416a9fe6428f': {'description': 'kahlua, bailey\'s, grand marnier'}, # b52 shot
                '6213d7c6-26ab-11eb-8a1b-416a9fe6428f': {'description': 'rum, ananas juice, cocos melk, cocos krem'}, # pina colada
                '6f229d08-26ab-11eb-8a1b-416a9fe6428f': {'description': 'tequila, appelsinjuice, sirup'}, # tequila sunrise
                'f0384f1e-26ab-11eb-8a1b-416a9fe6428f': {'description': 'white rum, drambuie, lime juice, sitron juice'}, # north pole
                '289b1030-26ac-11eb-8a1b-416a9fe6428f': {'description': 'hot apple souce, whiskey, ananas juice'}, # hot apple sauce
                
                '97673920-19de-11ea-8e77-1247b74fae1c': {'description': 'med salat, dressing og chips'}, # hamburgertalerken
                '2cce79c0-1a01-11ea-be2f-cea2e83b0f02': {'description': 'med salat og dressing'}, # hamburger
                '6a51c060-19e1-11ea-aebc-960f77e91a0b': {'description': 'med salat, dressing, bearnaise og chips'}, # schnitzel
                'f13f3660-19dd-11ea-b6e8-50ad43873b88': {'description': 'med salat, dressing, bearnaise og chips'}, # biffsnadder
                'b845d390-a4f8-11ea-8f9b-5ca8cba5baac': {'description': 'med salat, dressing, bearnaise og chips'}, # løvbiff
                '2a8b3be0-1cf3-11ea-810d-636cc28e0a01': {'description': 'med salat, dressing og chips'}, # hamburgertalerken
                '49ba53c0-1cf3-11ea-a453-0cdfacad4f21': {'description': 'med salat og dressing'}, # hamburger
                '90b43020-1cf3-11ea-8616-51cbb4a16783': {'description': 'med salat, dressing, bearnaise og chips'}, # schnitzel
                '0be85e70-1cf3-11ea-ab6c-796ce77a8c54': {'description': 'med salat, dressing, bearnaise og chips'}, # biffsnadder

                '720e6670-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, salami og ost'}, # salami pizza
                'b21ac920-25aa-11eb-9845-e37fa62ac814': {'description': 'TAKEAWAY tomatsaus, salami og ost'}, # salami pizza (takeaway)
                '9acf23b0-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, skinke og ost'}, # skinke pizza
                '2bc3a710-25ab-11eb-b727-73df053d26bf': {'description': 'TAKEAWAY tomatsaus, skinke og ost'}, # skinke pizza (takeaway)
                'b4001d30-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, salami, skinke, sopp, knasende paprika og milde pepperoni, ost'}, # speciale pizza
                '52e70800-25ab-11eb-a98b-6b6f7cc60cee': {'description': 'TAKEAWAY tomatsaus, salami, skinke, sopp, knasende paprika og milde pepperoni, ost'}, # speciale pizza (takeaway)
                'c576f070-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, med pepperoni salami og mild pepperoni'}, # diablo pizza
                '53eabc60-25ab-11eb-8ba3-df3fed286e08': {'description': 'TAKEAWAY tomatsaus, med pepperoni salami og mild pepperoni'}, # diablo pizza (takeaway)
                'd9387700-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, skinke, ananas, ost'}, # hawaii pizza
                '562df5a0-25ab-11eb-b8e1-91fc07e1d909': {'description': 'TAKEAWAY tomatsaus, skinke, ananas, ost'}, # hawaii pizza (takeaway)
                'e97dcf20-25a5-11eb-9eef-d3f992a1bed8': {'description': 'tomatsaus, kylling, løk, ananas, paprika'}, # kylling pizza
                '571918f0-25ab-11eb-9ea1-75e42ea54798': {'description': 'TAKEAWAY tomatsaus, kylling, løk, ananas, paprika'}, # kylling pizza (takeaway)
}

def do_changes(product, res = False):
    if product['online'] is not None:
        product['online'] = None
        return do_changes(product, res = True)
    if (desc := DESCRIPTIONS.get(product['uuid'], None)) is not None:
        for k, v in desc.items():
            if product[k] != v:
                product[k] = v
                return do_changes(product, res = True)
    return res

access_token = get_access_token()
res = requests.get('https://products.izettle.com/organizations/self/products/v2',
                   headers = {'Authorization': 'Bearer %s' % access_token})
products_list = json.loads(res.text)
categories_dict = {}
for product in products_list:
    if product['category'] is None: continue
    categories_dict[product['category']['name']] = product['category']['uuid']
for product in products_list:
    category_fixed = False
    if product['category'] is not None and \
       product['category']['uuid'] != categories_dict[product['category']['name']]:
        product['category']['uuid'] = categories_dict[product['category']['name']]
        category_fixed = True
    if do_changes(product) or category_fixed:
        res = requests.put('https://products.izettle.com/organizations/self/products/v2/%s' % product['uuid'],
                           headers = {'Authorization': 'Bearer %s' % access_token,
                                      'If-Match': '*',
                                      'Content-Type': 'application/json'},
                           data = json.dumps(product))
        pp(json.dumps(res.text))
