
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, set_option

set_option('display.max_rows', 15)
set_option('display.max_columns', 30)
set_option('display.width', 3000)

home = 'https://www.netshoes.com.br/'

url_all = {
    'Masculino': 'lst/departamento-calcados-masculino/masculino?mi=hm_ger_mntop_H-CAL-calcados',
    'Feminino': 'lst/departamento-calcados-feminino/feminino?mi=hm_ger_mntop_M-C%2FAL-calcados',
    'Infantil': 'lst/calcado-infantil?genero=menino&genero=menina&genero=bebe-menino&genero=bebe-menina&mi=hm_ger_mntop_CR-CAL-calcados',
}

url_categories_by_sex = {
    'Masculino': {
        'Botas': 'botas/masculino?mi=hm_ger_mntop_H-CAL-calcados-botas',
        'Chinelos': 'masculino?tipo-de-produto=chinelos&tipo-de-produto=chinelos-e-sandalias&mi=hm_ger_mntop_H-CAL-chinelos-sandalias',
        'Chuteiras': 'chuteiras/masculino?mi=hm_ger_mntop_H-CAL-calcados-chuteiras',
        'Crocs': 'crocs-classico/masculino?mi=hm_ger_mntop_H-CAL-crocs',
        'Sapatenis': 'sapatenis/masculino?mi=hm_ger_mntop_H-CAL-calcados-sapatenis',
        'Tenis': 'tenis/masculino?mi=hm_ger_mntop_H-CAL-tenis',
        'Tenis Performance': 'tenis-performance/masculino?mi=hm_ger_mntop_H-CAL-tenis-performance',
    },
    'Feminino': {
        'Botas': 'botas/feminino?mi=hm_ger_mntop_M-CAL-calcados-botas',
        'Chinelos': 'feminino?tipo-de-produto=chinelos&tipo-de-produto=chinelos-e-sandalias&mi=hm_ger_mntop_M-CAL-chinelos-sandalias',
        'Croscs': 'crocs-classico/feminino?mi=hm_ger_mntop_M-CAL-crocs',
        'Sapatilhas': 'sapatilhas/feminino?',
        'Tenis': 'tenis/feminino?mi=hm_ger_mntop_M-CAL-tenis',
        'Tenis Performance': 'tenis-performance/feminino?mi=hm_ger_mntop_H-CAL-tenis-performance-feminino',
    },
    'Infantil': {},
}

sufix = '&psn=Menu_Top&nsCat=Artificial&page={}'

data = []
for key, value in url_categories_by_sex.items():
    if key != 'Infantil':
        gender = key
        categories = value

        for category, url in categories.items():
            print(gender, category, len(data))

            for page in range(1, 100):
                r = requests.get(home + url + sufix.format(page))
                soup = BeautifulSoup(r.text, 'html.parser')

                if soup.find('h2').text == 'Não foi possível encontrar resultados para o termo procurado':
                    break

                soup = soup.find('div', {'id': 'item-list'}).find('div', {'class': 'wrapper'})
                soup = soup.find_all('div', {'class': 'item card-desktop card-with-rating lazy-price item-desktop--3'})

                for n, product in enumerate(soup):
                    info = {
                        'gender': gender,
                        'category': category,
                        'product_category': product.find('button')['product-category'],
                        'data_department': product.find('span')['data-department'],
                        'page': page,
                        'data_position': n,
                        'parent_sku': product['parent-sku'],
                        'title': product.find('a', {'class': 'i card-link'})['title'],
                        'href': 'https://' + product.find('a', {'class': 'i card-link'})['href'],
                    }
                    data.append(info)

df = DataFrame(data, columns=data[0].keys())


def get_infos(url):
    import re

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        buybox = soup.find(id='buy-box')

        price = float(buybox.find(itemprop='price')['content'])
        original_price = float(buybox.find('del').text[3:].replace(',', '.')) if buybox.find('del') is not None else price
        savings = - float(re.search('\(([^)]+)', buybox.find(class_='default-price saving mult-seller').text).group(1).replace('%','')) / 100 if price != original_price else 0

        if soup.find('section', class_='badges-item').text == '':
            realease = False
            reviews = int(soup.find('a', {'href': '#reviews'}).text.split(' ')[0])
            recommend = int(soup.find('div', class_='line-average').text.replace('%', '')) / 100
            rating = float(soup.find('span', {'itemprop': 'ratingValue'}).text)
        else:
            realease = True
            reviews = 0
            recommend = 0
            rating = None

        return {
            'available': buybox.find(class_='if-available hide') is None,
            'price': price,
            'original_price': original_price,
            'savings': savings,
            'installment': buybox.find(class_='installments-price').text.split(' ')[0].replace('x', ''),
            'product_seller': buybox.find(class_='product-seller').text[22:].strip(),
            'color': soup.find('span', class_='sku-select-title').text,
            'sizes': ','.join([item.find('a').text for item in soup.find('ul', {'data-type': 'size'}).find_all('li')]),
            'new_realease': realease,
            'reviews': reviews,
            'recommend': recommend,
            'rating': rating,
        }

    except:
        return 'error'


inside_data = df['href'].apply(get_infos)

df.sample(5)

def get_product_by_internal_api():
    url = 'https://www.netshoes.com.br/frdmprcs/U51-0247-016'

