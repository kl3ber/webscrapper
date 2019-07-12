
from consumidor_gov.__config__ import uid, pwd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

payload = {'inUserName': uid, 'inUserPass': pwd}
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',}

url = {
    'Varejo': {
        'Indice de Solução': '',
        '': '',
        'Reclamações Respondidas': 'https://www.consumidor.gov.br/pages/indicador/ranking/listar.json?sEcho=3&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&mDataProp_0=posicao&mDataProp_1=nomeFantasiaOuRazaoSocial&mDataProp_2=valor&segmento=8&periodo={}&tipo=solucao&_=1562779626083',
    },
    'Comercio Eletronico': {},
}

url = 'https://www.consumidor.gov.br/pages/indicador/ranking/listar.json?sEcho=3&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&mDataProp_0=posicao&mDataProp_1=nomeFantasiaOuRazaoSocial&mDataProp_2=valor&segmento=8&periodo={}&tipo=satisfacao&_=1562779626084'

session = requests.Session()
r = session.get(url['Varejo']['Reclamações Respondidas'].format(30), headers=header,  data=payload)
r = session.get(url.format(30), headers=header,  data=payload)

result = r.json()['dados']['aaData']
df = DataFrame(result)

df