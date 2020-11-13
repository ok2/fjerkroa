from utils import *
from pprint import pprint as pp
import requests, json

pages_config = (
    ('Menu', ('Mat', 'Extra')),
    ('Menu:Pizza', ('Pizza:',)),
    ('Barmenu', ('Øl', 'Vine&ånder')),
    ('Barmenu:Drinks', ('Drink:',)),
    ('Menu:Is', ('Is:',)),
    ('Menu:Drikke', ('Drikke:',)),
    ('Menu:Takeaway pizza', ('TakeawayPizza:',)),
    ('Menu:Takeaway', ('Takeaway:',)),
)

access_token = get_access_token()
res = requests.get('https://products.izettle.com/organizations/self/library',
                   headers = {'Authorization': 'Bearer %s' % access_token})

def get_subcategories(main):
    product_list = json.loads(res.text)['products']
    subcategory_dict = {}
    for product in product_list:
        if product['category'] is None: continue
        if not product['category']['name'].startswith(main): continue
        subcategory = product['category']['name'].split('/')[1].strip()
        if subcategory not in subcategory_dict:
            subcategory_dict[subcategory] = {'name': latex(subcategory), 'entries': []}
        subcategory = subcategory_dict[subcategory]
        if product['description'] is not None:
            subcategory['entries'].append('\\EEntry{%s}{%d,- kr}{%s}' % \
                                          (latex(product['name']),
                                           product['variants'][0]['price']['amount']//100,
                                           latex(product['description'].removeprefix('TAKEAWAY'))))
        else:
            subcategory['entries'].append('\\Entry{%s}{%d,- kr}' % \
                                          (latex(product['name']),
                                           product['variants'][0]['price']['amount']//100))
    return subcategory_dict

first_page = True
for main, subs in pages_config:
    if ':' in main:
        main, main_name = main.split(':')
    else: main_name = main
    subcategory_dict = get_subcategories(main)
    if not first_page: print('\\newpage\n\\thispagestyle{empty}')
    else: first_page = False
    print(r'''
\begin{tikzpicture} [remember picture, overlay] %%
\node at (current page.center){%%
\begin{tikzpicture}
\MyCadre{60}{8}{12}%%
\node[text width=13cm] at (thecenter){%%
\begin{center} \Huge %s \end{center}
\vspace{1cm}
''' % latex(main_name))
    first_sub = True
    if subs is None:
        subs = sorted(subcategory_dict.keys())
    for subcategory_id in subs:
        if ':' in subcategory_id:
            subcategory_id, subcategory_name = subcategory_id.split(':')
        else: subcategory_name = subcategory_id
        subcategory = subcategory_dict[subcategory_id]
        if not first_sub: print('\n\\Tiret\n')
        else: first_sub = False
        print('\\begin{Group}{%s}' % latex(subcategory_name))
        entries_list = list(sorted(subcategory['entries'], key = lambda x: x.replace('EEntry', 'Entry')))
        for entry in entries_list:
            #print('%s%s' % (entry, r'' if entry == entries_list[-1] else r'\\'))
            print(entry)
        print('\\end{Group}')
    print(r'''};
\end{tikzpicture}
};
\end{tikzpicture}''')
