
from hugme.config import xpath

from importlib import import_module
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep


class HugMe(object):
    def __init__(self, operacao, headless=True):
        self.operacao = operacao.lower().strip().replace(' ', '_')
        self.filter_name = getattr(import_module(f'hugme.{self.operacao}'), 'FILTER_NAME')
        self.empresas = getattr(import_module(f'hugme.{self.operacao}'), 'EMPRESAS')

        self.driver = None
        self.headless = headless
        self.logged = False

        self.destination_folder = self.check_destination_folder()
        self.new_reports = {}
        self.downloaded_files = {}
        self.final_file = None

    def __enter__(self):
        self.start_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
            sleep(2)

    def start_driver(self):
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.headless = self.headless
        options.add_argument("--log-level=3")
        # # options.add_argument("--incognito")
        # options.add_argument("--mute-audio")
        # options.add_argument("--disable-notifications")
        # options.add_argument('--no-sandbox')
        # options.add_argument('--verbose')
        # options.add_experimental_option('prefs', {
        #     'download.default_directory': self.destination_folder,
        #     'download.prompt_for_download': False,
        #     'download.directory_upgrade': True,
        #     'safebrowsing_for_trusted_sources_enabled': False,
        #     'safebrowsing.disable_download_protection': True,
        #     'safebrowsing.enabled': False,
        # })

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.destination_folder}}
        driver.execute("send_command", params)

        self.driver = driver

    def access_website(self):
        # self.driver.maximize_window()
        self.driver.implicitly_wait(300)
        self.driver.get('https://app.hugme.com.br/')

    def login(self, retries=15):
        from datetime import datetime

        uid, pwd = tuple(getattr(import_module(f'hugme.__key__'), self.operacao.upper()).values())

        self.driver.find_element_by_id('user').clear()
        self.driver.find_element_by_id('password').clear()

        self.driver.find_element_by_id('user').send_keys(uid)
        self.driver.find_element_by_id('password').send_keys(pwd)
        sleep(2)
        print('')

        for i in range(retries):
            self.driver.find_element_by_xpath('//*[@id="submit-button"]').click()
            sleep(5)

            if self.driver.current_url == 'https://app.hugme.com.br/app.html#/':
                self.logged = True
                return print('Login realizado.')
            else:
                error = self.driver.find_element_by_xpath('//*[@id="error-message"]').text
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error)
                sleep(10)

        return print(self.operacao + ': ', 'Não foi possível logar no sistema.')

    def access_reports_page(self):
        self.driver.get('https://app.hugme.com.br/app.html#/dados/tickets/exportar/')
        while 'Novo relatório' not in self.driver.page_source: pass

    def find_filter_index(self, filter_name):
        """ Encontra o indice do filtro desejado entre todos os filtros pré-criados """
        html = self.driver.find_element_by_xpath(xpath['Lista de Filtros']).get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        filters = soup.find_all('li')
        for n, filter in enumerate(filters, start=1):
            if filter.text.strip() == filter_name:
                return n
        return False

    def select_preset_filter(self):
        """ Encontra e seleciona o filtro pré-criado na listas de filtros salvos """
        self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/div[1]/header/h1').click()
        self.driver.find_element_by_xpath(xpath['Filtros Salvos']).click()
        sleep(2)

        filter_index = self.find_filter_index(self.filter_name)

        if filter_index:
            self.driver.find_element_by_xpath(xpath['Selecionar Filtro'].format(filter_index)).click()
            print('Filtro Carregado.\n')
        else:
            print('Filtro não encontrado. Por favor, verifique o nome.\n')

    def select_empresa(self, empresa):
        """ Encontra e seleciona a empresa na lista de seleção - combobox"""
        for option in self.driver.find_element_by_xpath(xpath['Empresa']).find_elements_by_tag_name('option'):
            if option.get_attribute('label') == empresa:
                option.click()

    def submit_report(self, report_name):
        """ Escreve o nome/titulo do relatório e subemete/clica em 'Gerar Relatório' """
        from datetime import datetime
        self.driver.find_element_by_xpath(xpath['Titulo']).clear()
        sleep(3)
        self.driver.find_element_by_xpath(xpath['Titulo']).send_keys(report_name)
        sleep(3)
        self.driver.find_element_by_xpath(xpath['Gerar Relatório']).click()
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Relatório Gerado: ', report_name)
        sleep(5)

    def get_all_reports(self):
        """ Retorna todos os relatórios listados """
        html = self.driver.find_element_by_xpath(xpath['Lista de Relatórios']).get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        reports = soup.find('ul').find_all('li', class_='item ng-scope')
        result = {}
        for n, report in enumerate(reports):
            available = int(reports[n].find_all('span')[4].text.split(':')[1].strip().split(' ')[0]) < 0
            id_report = reports[n].find_all('span')[5].text.split(':')[1].strip()
            creation = reports[n].find_all('span')[3].text
            result[n + 1] = {'Name': reports[n].find('h5').text, 'Download': available, 'ID': id_report, 'Creation': creation}
        return result

    def find_report(self, report_name):
        """ Encontra o índice do relatório, verifica o tempo restante/disponibilidade para download"""
        html = self.driver.find_element_by_xpath(xpath['Lista de Relatórios']).get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        reports = soup.find('ul').find_all('li', class_='item ng-scope')
        for n, report in enumerate(reports):
            if reports[n].find('h5').text == report_name:
                # print(n + 1, reports[n].find('h5').text, reports[n].find_all('span')[4].text)
                # minutes_left = int(reports[n].find_all('span')[4].text.split(' ')[1])
                download = len(reports[n].find_all('button', class_='')) == 1
                return n + 1, download

    def scrolldown_load_older_reports(self, times=1):
        """ Scroll down na lista de relatórios disponíveis, carregar mais relatórios """
        if len(self.get_all_reports()) <= 21: return
        while 'Carregar mais' not in self.driver.page_source: pass
        sleep(3)
        for i in range(times):
            element = self.driver.find_element_by_xpath(xpath['Carregar Mais'])
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.find_element_by_xpath(xpath['Carregar Mais']).click()
            sleep(3)

    def load_more_reports(self, times=1):
        for i in range(times):
            html = self.driver.find_element_by_xpath(xpath['Lista de Relatórios']).get_attribute('innerHTML')
            while 'Carregar mais' not in html: pass
            sleep(2)
            self.driver.find_element_by_xpath(xpath['Carregar Mais']).click()
            sleep(3)

    def download_report(self, index):
        """ Downlaod do relatório """
        self.driver.find_element_by_xpath(xpath['Download'].format(index)).click()
        sleep(5)

    def check_file_download(self, report_name):
        """ Verifica se o download do arquivo já terminou """
        from os import listdir

        for file in listdir(self.destination_folder):
            if report_name.replace('_', '').replace(' ', '-').lower() in file:
                return True
        return False

    def delete_report(self, index):
        """ Exclusão de relatório por index """
        self.driver.find_element_by_xpath(xpath['Excluir'].format(index)).click()
        sleep(5)

    def delete_all_reports(self):
        """ Deleta todos os novos relatórios gerados """
        self.scrolldown_load_older_reports(times=5)
        for file in self.new_reports.keys():
            index, download = self.find_report(report_name=file)
            self.delete_report(index)

    def check_destination_folder(self):
        """ Verifica qual o path completo da pasta hugme/data """
        from os import getcwd
        name = self.__class__.__name__.lower()
        return getcwd() + '\\data\\' if getcwd().split('\\')[-1] == name else getcwd() + '\\' + name + '\\data\\'

    def get_downloaded_files_names(self):
        from os import listdir

        result = {
            empresa: file
            for empresa, report in self.new_reports.items()
            for file in listdir(self.destination_folder)
            if report.replace('_', '').lower() in file
        }

        self.downloaded_files = result

    def move_downloaded_file(self, report_name):
        """ Mover apenas arquivo para a pasta data do projeto """
        from os import path
        from shutil import move

        origin = path.expanduser('~\\Downloads\\') + report_name + '.csv'
        destination = self.destination_folder + report_name + '.csv'
        try:
            move(origin, destination)
        except FileNotFoundError:
            pass

    def move_all_downloaded_files(self):
        """ Mover todos os arquivos baixados de uma só vez para a pasta data do projeto """
        from os import path
        from shutil import move

        for file in self.downloaded_files.values():
            move(path.expanduser('~\\Downloads\\') + file, self.destination_folder + file)

    def concatenate_files(self):
        """ Consolida a base de reclamações de todas as empresas em apenas um arquivo """
        from pandas import read_excel, DataFrame
        from datetime import datetime

        print('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Concatenando os arquivos ...')

        base_reclamacoes = DataFrame()
        for empresa, file in self.downloaded_files.items():
            df = read_excel(self.destination_folder + file, header=3)
            df['Empresa'] = empresa
            base_reclamacoes = base_reclamacoes.append(df)

        for col in base_reclamacoes.columns:
            if 'Unnamed' in col:
                base_reclamacoes.drop(columns=col, inplace=True)

        file = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + self.operacao + '.csv'
        self.final_file = self.destination_folder + file
        base_reclamacoes.to_csv(self.final_file, index=False)

    def delete_all_downloaded_files(self):
        """ Deleta os arquivos baixados """
        from os import remove

        for file in list(self.downloaded_files.values()):
            remove(self.destination_folder + file)

    def move_to_blob(self):
        from azure.storage.blob import BlockBlobService, PublicAccess
        from datetime import datetime

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Movendo arquivo final para o blob storage...')

        acc, key = tuple(getattr(import_module(f'hugme.__key__'), 'STORAGE_ACCOUNT').values())

        block_blob_service = BlockBlobService(account_name=acc, account_key=key)
        block_blob_service.set_container_acl('hugme', public_access=PublicAccess.Container)
        block_blob_service.create_blob_from_path(
            container_name='hugme',
            blob_name=self.operacao,
            file_path=self.final_file,
        )


if __name__ == '__main__':
    pass
