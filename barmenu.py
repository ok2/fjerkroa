from utils import *
from pprint import pprint as pp
import requests, json

pages_config = (
    ('Menu', ('Mat', 'Extra')),
    ('Barmenu', None),
    ('Menu', ('Is', 'Drikke')),
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
            desc = '\\Expl{%s}' % latex(product['description'])
        else: desc = ''
        subcategory['entries'].append('\\Entry{%s%s}{%d,- kr}' % \
                                      (latex(product['name']), desc,
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
\begin{center} \Huge Fj\ae{}rkroa \\ \LARGE %s \end{center}
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
        entries_list = list(sorted(subcategory['entries']))
        for entry in entries_list:
            print('%s%s' % (entry, r'' if entry == entries_list[-1] else r'\\'))
        print('\\end{Group}')
    print(r'''};
\end{tikzpicture}
};
\end{tikzpicture}''')
