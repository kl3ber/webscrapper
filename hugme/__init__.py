
from hugme.__config__ import xpath, empresas, filter_name, chrome_version

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep


class HugMe(object):
    def __init__(self, hide=False):
        self.filter_name = filter_name
        self.empresas = empresas
        self.new_reports = []
        self.downloaded_files = []

        self.driver = None
        self.hide = hide

    def access_website(self):
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.headless = self.hide

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()
        driver.get('https://app.hugme.com.br/')
        self.driver = driver

    def login(self, retries=15):
        from hugme.__key__ import uid, pwd
        from datetime import datetime
        self.driver.find_element_by_id('user').send_keys(uid)
        self.driver.find_element_by_id('password').send_keys(pwd)
        sleep(2)
        print('')

        for i in range(retries):
            self.driver.find_element_by_xpath('//*[@id="submit-button"]').click()
            sleep(5)

            if self.driver.current_url == 'https://app.hugme.com.br/app.html#/':
                return print('Login realizado.')
            else:
                print(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    self.driver.find_element_by_xpath('//*[@id="error-message"]').text
                )
                sleep(10)
        return print('Não foi possível logar no sistema.')

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
        """ Encontra a empresa na lista de seleção - combobox"""
        for option in self.driver.find_element_by_xpath(xpath['Empresa']).find_elements_by_tag_name('option'):
            if option.get_attribute('label') == empresa:
                option.click()

    def submit_report(self, report_name):
        """ Escreve o nome/titulo do relatório e subemete/clica em 'Gerar Relatório' """
        from datetime import datetime
        self.driver.find_element_by_xpath(xpath['Titulo']).clear()
        self.driver.find_element_by_xpath(xpath['Titulo']).send_keys(report_name)
        sleep(1)
        self.driver.find_element_by_xpath(xpath['Gerar Relatório']).click()
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Relatório Gerado: ', report_name)
        sleep(5)

    def scrolldown_load_older_reports(self, times=1):
        """ Scroll down na lista de relatórios disponíveis, carregar mais relatórios """
        for i in range(times):
            element = self.driver.find_element_by_xpath(xpath['Carregar Mais'])
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.driver.find_element_by_xpath(xpath['Carregar Mais']).click()
            sleep(3)

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

    def download_report(self, index):
        """ Downlaod do relatóio """
        self.driver.find_element_by_xpath(xpath['Download'].format(index)).click()
        sleep(5)

    def check_file_download(self, report_name):
        from os import listdir, path
        for file in listdir(path.expanduser('~/Downloads/')):
            if report_name.replace('_', '').lower() in file:
                return True
        return False

    def delete_report(self, index):
        """ Exclusão do relatório """
        self.driver.find_element_by_xpath(xpath['Excluir'].format(index)).click()
        sleep(5)

    def check_destination_folder(self):
        from os import getcwd
        name = self.__class__.__name__.lower()
        return getcwd() + '\\data\\' if getcwd().split('\\')[-1] == name else getcwd() + '\\' + name + '\\data\\'

    def move_downloaded_file(self, report_name):
        """ Mover um arquivo """
        from os import listdir, path, getcwd
        from shutil import move

        for file in listdir(path.expanduser('~\\Downloads\\')):
            if report_name.replace('_', '').lower() in file:
                move(path.expanduser('~\\Downloads\\') + file, getcwd() + '\\data\\' + file)

    def move_all_downloaded_files(self):
        """ mover todos os arquivos baixados de uma vez """
        from os import listdir, path
        from shutil import move

        destination = self.check_destination_folder()

        result = [
            file
            for file in listdir(path.expanduser('~\\Downloads\\'))
            for report in self.new_reports
            if report.replace('_', '').lower()in file
        ]
        return [move(path.expanduser('~\\Downloads\\') + file, destination + file) for file in result]


if __name__ == '__main__':
    from pandas import set_option, read_excel, DataFrame
    from os import getcwd, listdir

    set_option('display.max_rows', 15)
    set_option('display.max_columns', 300)
    set_option('display.width', 3000)

    path = getcwd() + '\\hugme\\data\\'
    files = listdir(path)

    downloaded_files = {
        '1012_bartira15617461772969072_1561746345009.xlsx':                 'Bartira',
        '1013_casasbahialojafisica15617461851143312_1561746375009.xlsx':    'Casas Bahia Loja Física',
        '1014_pontofriolojafisica1561746193466698_1561746405009.xlsx':      'Ponto Frio Loja Física',
        '137_extra15617461191844656_1561746135025.xlsx':                    'Extra',
        '138_pontofriolojavirtual1561746127091306_1561746165011.xlsx':      'Ponto Frio Loja Virutal',
        '139_casasbahialojavirtual1561746136120041_1561746195010.xlsx':     'Casas Bahia Loja Virtual',
        '159_barateiro15617461449438148_1561746225011.xlsx':                'Barateiro',
        '159_casasbahiamarketplace15617461523521512_1561746255010.xlsx':    'Casas Bahia Marketplace',
        '159_pontofriomarketplace15617461606023254_1561746285015.xlsx':     'Ponto Frio Markeplace',
        '492_extramarketplace15617461691500351_1561746315010.xlsx':         'Extra Marketplace',
    }

    base_reclamacoes = DataFrame()
    for file, empresa in downloaded_files.items():
        df = read_excel(path + file, header=3)
        df['Empresa'] = empresa
        base_reclamacoes = base_reclamacoes.append(df)

    cols = base_reclamacoes.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    base_reclamacoes = base_reclamacoes[cols]

    for col in base_reclamacoes.columns:
        if 'Unnamed' in col:
            base_reclamacoes.drop(columns=col, inplace=True)

    base_reclamacoes.to_csv(path + 'base_reclamacoes.csv')

