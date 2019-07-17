
import requests
from datetime import datetime
from time import sleep
from pandas import set_option, DataFrame

set_option('display.max_rows', 30)
set_option('display.max_columns', 100)
set_option('display.width', 10000)

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

url = "https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/query/companyComplains/50/{}?company=11871"

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

result = []
retry = []
for n in range(0, 95001, 50):
    session = requests.Session()
    requisicao = session.get(url.format(n), headers=header)
    status = requisicao.status_code
    if status == 200:
        requisicao = requisicao.json()['complainResult']['complains']['data']
        for r in requisicao:
            r['pagina'] = n
        result = result + requisicao
        print(n, len(result))
    else:
        retry.append(n)
    sleep(10)

sec = 10
while not retry == []:
    print('NOVA TENTANTIVA - ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' - ', len(retry), ' - ', retry)
    for n in retry:
        session = requests.Session()
        requisicao = session.get(url.format(n), headers=header)
        if requisicao.status_code == 200:
            requisicao = requisicao.json()['complainResult']['complains']['data']
            for r in requisicao:
                r['pagina'] = n
            result = result + requisicao
            retry.remove(n)
            print(n, len(result))
            sleep(sec)
    sec += 1

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

df = DataFrame(result, columns=list(result[0].keys()))

null_cols = [
    'additionalFields', 'requesterName', 'marketplaceComplain',
    'moderateReason', 'files', 'indexable', 'phones', 'canBeEvaluated', 'moderateRequested', 'user',
]

masked_cols = [
    'moderationUserName', 'deletionReason', 'ip', 'moderationReasonDescription', 'deletedIp', 'userEmail', 'address',
    'userName'
]

df = df.drop(columns=null_cols + masked_cols).sort_values('created')


def generate_url(title, id):
    import unicodedata
    url = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode("utf-8")
    url = ''.join(char for char in url if char.isalnum() or char == ' ')
    url = url.lower().replace(' +', ' ').strip().replace(' ', '-')
    url = url + '_' + id + '/'
    return url


df.apply(lambda x: generate_url(x.title, x.id), axis=1)

df.to_pickle('reclame_aqui\\data\\base_reclamacoes.pkl')
