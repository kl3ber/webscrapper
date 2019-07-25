
from consumidor_gov.config import uid, pwd
from pandas import DataFrame
from datetime import datetime
from time import sleep


class Comparativo(object):
    def __init__(self):
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

        self.home = 'https://www.consumidor.gov.br/pages/indicador/ranking/listar.json?'
        self.position = 'sEcho=3&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&mDataProp_0=posicao&mDataProp_1'
        self.parameter = '=nomeFantasiaOuRazaoSocial&mDataProp_2=valor&segmento={}&periodo={}'

        self.segmentos = {8: 'Varejo', 9: 'Comércio Eletrônico', }
        self.periodos = [7, 30, 90, 180, 365]

        self.date = datetime.now().replace(microsecond=0).isoformat(' ')

        self.indicadores = {
            8: {
                'Índice de Solução':        '&tipo=solucao&_=1562779626083',
                'Indice de Satisfação':     '&tipo=satisfacao&_=1562779626084',
                'Prazo Médio de Resposta':  '&tipo=prazo&_=1563387712900',
                'Reclamações Respondidas':  '&tipo=respondidas&_=1563387712901',
            },
            9: {
                'Índice de Solução':        '&tipo=solucao&_=1563387712902',
                'Índice de Satisfação':     '&tipo=satisfacao&_=1563387712903',
                'Prazo Médio de Resposta':  '&tipo=prazo&_=1563387712904',
                'Reclamações Respondidas':  '&tipo=respondidas&_=1563387712905',
            },
        }

        self.daily_file = None
        self.final_file = None

    def comparison_between_companies(self):
        import requests

        payload = {'inUserName': uid, 'inUserPass': pwd}
        result = DataFrame()
        for key, segmento in self.segmentos.items():
            for p in self.periodos:
                for indicador, tipo in self.indicadores[key].items():
                    # print(parameter.format(key, p) + tipo, key, segmento, indicador, )
                    url = self.home + self.position + self.parameter.format(key, p) + tipo
                    session = requests.Session()
                    r = session.get(url, headers=self.header, data=payload)

                    df = DataFrame(r.json()['dados']['aaData'])
                    df = df[['numeroIdentificacao', 'nomeFantasiaOuRazaoSocial', 'posicao', 'valor']]
                    df.columns = ['id_empresa', 'razao_social', 'posicao', 'nota']
                    df['segmento'] = segmento
                    df['indicador'] = indicador
                    df['periodo'] = p

                    result = result.append(df)

        result['nota'] = result.nota.astype(float)
        result['data'] = self.date
        cols = ['data', 'id_empresa', 'razao_social', 'segmento', 'indicador', 'periodo', 'nota', 'posicao']
        result = result[cols]

        self.daily_file = f"consumidor_gov\\data\\{datetime.now().strftime('%Y%m%d_%H%M%S')}_comparativo.csv"
        result.to_csv(self.daily_file, index=False)

    def add_new_day_data(self):
        from pandas import read_csv

        df = read_csv('consumidor_gov\\data\\_comparativo.csv')
        ingest = read_csv(self.daily_file)

        df = df.append(ingest, sort=False)
        df.to_csv('consumidor_gov\\data\\_comparativo.csv')

    def process_legacy_file(self):
        from pandas import read_excel

        df = read_excel('consumidor_gov\\data\\Base_Indicadores.xlsx', 'Ind')
        df.columns = ['razao_social', 'data', 'indicador', 'periodo', 'nota', 'posicao']
        df['id_empresa'] = ''
        df['segmento'] = ''
        df = df[['data', 'id_empresa', 'razao_social', 'segmento', 'indicador', 'periodo', 'nota', 'posicao']]
        df.to_csv(f"consumidor_gov\\data\\00000000_000000_comparativo.csv", index=False)

    def generate_unique_base(self):
        from pandas import read_csv, concat
        from os import listdir

        folder = 'consumidor_gov\\data\\'
        dtypes = {'id_empresa': 'str', 'posicao': 'float'}

        base = concat([read_csv(folder + file, dtype=dtypes) for file in listdir(folder) if file.endswith('csv')], sort=False)
        base['posicao'] = base.posicao.astype(int)
        base['data'] = base.data.astype('datetime64')

        base.to_csv(folder + '_comparativo.csv', index=False)

    def move_to_storage_account(self, file, storage='blob'):
        from hugme.__key__ import acc, key
        from datetime import datetime

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Movendo arquivo final para o {} storage...'.format(object))

        if storage == 'blob':
            from azure.storage.blob import BlockBlobService, PublicAccess

            block_blob_service = BlockBlobService(account_name=acc, account_key=key)
            block_blob_service.set_container_acl('final', public_access=PublicAccess.Container)
            block_blob_service.create_blob_from_path(
                container_name='consumidorgov',
                blob_name='comparativo',
                file_path='consumidor_gov\\data\\' + file,
            )

        elif storage == 'files':
            from azure.storage.file import FileService

            file_service = FileService(account_name=acc, account_key=key)
            file_service.create_file_from_path(
                share_name='complains',
                directory_name='hugme',
                file_name='base.csv',
                local_file_path='' + file,
            )

        else:
            return False


class EmpresasDoGrupo(object):
    def __init__(self):
        self.destination_folder = 'consumidor_gov\\data\\'
        self.driver = None

    def start_driver(self):
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        options = Options()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.destination_folder}}
        driver.execute("send_command", params)

        self.driver = driver

    def access_website(self):
        self.driver.get('https://www.consumidor.gov.br/pages/administrativo/login')
        self.driver.implicitly_wait(300)

    def login(self):
        self.driver.find_element_by_xpath('//*[@id="login"]').send_keys(uid)
        self.driver.find_element_by_xpath('//*[@id="senha"]').send_keys(pwd)
        sleep(1)
        self.driver.find_element_by_xpath('//*[@id="btnLoginPageForm"]').click()

    def access_reports_page(self):
        self.driver.get('https://www.consumidor.gov.br/pages/exportacao-dados/novo')
        self.driver.implicitly_wait(10)

    def calculate_period(self):
        from datetime import date
        from dateutil.relativedelta import relativedelta

        date_end = date.today() - relativedelta(days=1)
        date_ini = date_end - relativedelta(months=2)

        return date_ini, date_end

    def set_filters(self, start_date, finish_date):
        self.driver.find_element_by_xpath('//*[@id="dataIniPeriodo"]').send_keys(start_date)
        sleep(1)
        self.driver.find_element_by_xpath('//*[@id="dataFimPeriodo"]').send_keys(finish_date)
        sleep(1)
        self.driver.find_element_by_xpath('//*[@id="colunasExportadas1"]').click()
        sleep(1)
        self.driver.find_element_by_xpath('//*[@id="btnExportar"]').click()

    def get_companies(self, driver):
        from bs4 import BeautifulSoup
        html = driver.find_element_by_xpath('//*[@id="menu_sel_fornecedor"]').get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        return {option.text: option['value'] for option in soup.find_all('option') if option['value'] != 'Selecione'}


if __name__ == '__main__':
    rpa = Comparativo()
    rpa.comparison_between_companies()
    rpa.add_new_day_data()

    if not rpa.final_file:
        rpa.final_file = '_comparativo.csv'
    rpa.move_to_storage_account(file=rpa.final_file, storage='blob')
