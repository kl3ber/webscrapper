
from hugme.__config__ import xpath, empresas, filter_name, chrome_version

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep


class HugMe(object):
    def __init__(self, hide=False):
        self.filter_name = filter_name
        self.empresas = empresas
        self.new_reports = []

        self.driver = None
        self.hide = hide
        self.access_website()

    def access_website(self):
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.headless = self.hide

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()
        driver.get('https://app.hugme.com.br/')
        self.driver = driver

    def login(self):
        from __key__ import uid, pwd
        self.driver.find_element_by_id('user').send_keys(uid)
        self.driver.find_element_by_id('password').send_keys(pwd)
        self.driver.find_element_by_xpath('//*[@id="submit-button"]').click()
        return self.driver.find_element_by_xpath('//*[@id="error-message"]').text
        #sleep(3)

        #if self.driver.current_url == 'https://app.hugme.com.br/app.html#/':
        #    return 'Login realizado.'
        #else:
        #    return self.driver.find_element_by_xpath('//*[@id="error-message"]').text

    def access_reports_page(self):
        self.driver.get('https://app.hugme.com.br/app.html#/dados/tickets/exportar/')
        while 'Novo relatório' not in self.driver.page_source:
            pass

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
        sleep(4)

    def move_downloaded_file(self, report_name):
        from os import listdir, path
        from shutil import move

        for file in listdir(path.expanduser('~\\Downloads\\')):
            if report_name.replace('_', '').lower() in file:
                move(path.expanduser('~/Downloads/') + file, 'data/' + file)

    def move_all_downloaded_files(self):
        from os import listdir, path
        from shutil import move

        result = [
            file
            for file in listdir(path.expanduser('~\\Downloads\\'))
            for report in self.new_reports
            if report.replace('_', '').lower()in file
        ]
        return [move(path.expanduser('~/Downloads/') + file, 'data/' + file) for file in result]


if __name__ == '__main__':
    from time import time, sleep
    from datetime import datetime
    from hugme import HugMe

    temp_ini = datetime.now().replace(microsecond=0)
    rpa = HugMe()
    rpa.login()

    rpa.access_reports_page()
    rpa.select_preset_filter()

    for empresa, selection_name in rpa.empresas.items():
        rpa.select_empresa(empresa=selection_name)
        titulo = empresa.replace(' ', '_') + '_' + str(time()).replace('.', '')
        rpa.submit_report(report_name=titulo)
        rpa.new_reports.append(titulo)

    to_be_downloaded = rpa.new_reports.copy()
    print('\nVerificando disponibilidade de download...\n')

    while not to_be_downloaded == []:
        rpa.driver.refresh()
        # while 'Carregar mais' not in rpa.driver.page_source: pass
        sleep(30)

        for report in to_be_downloaded:
            index, download = rpa.find_report(report_name=report)
            if download:
                rpa.download_report(index)
                while not rpa.check_file_download(report): pass
                sleep(3)

                rpa.delete_report(index)
                rpa.move_downloaded_file(report)
                to_be_downloaded.remove(report)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Download: ', report)

    rpa.driver.refresh()

    print('\nExtração concluída.\n')
    print('Tempo de execução: ', datetime.now().replace(microsecond=0) - temp_ini)
    rpa.driver.close()
    rpa.driver.quit()
