

from __config__ import parametros_xpath, empresas, filter_name, chrome_version

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import time, sleep
from datetime import datetime


def login(driver):
    from __key__ import uid, pwd
    driver.find_element_by_id('user').send_keys(uid)
    driver.find_element_by_id('password').send_keys(pwd)
    driver.find_element_by_xpath('//*[@id="submit-button"]').click()
    print('\nLogin Realizado.')

    if driver.find_element_by_id('error-message').get_attribute('innerHTML') != '':
        print('Muitos usuários logados. Tente mais tarde em um horário com fluxo de pessoas menor.')


def find_filter_index(driver, filter_name):
    """ Encontra o indice do filtro desejado entre todos os filtros pré-criados """
    html = driver.find_element_by_xpath('//*[@id="qtip-5-content"]/div/div/div/ul').get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    filters = soup.find_all('li')
    if filters == '':
        return True
    for n, filter in enumerate(filters, start=1):
        if filter.text.strip() == filter_name:
            return n
    return False


def select_preset_filter(driver):
    driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/footer/div/div[2]/a').click()
    sleep(2)
    filter_index = find_filter_index(driver, filter_name)
    if filter_index:
        driver.find_element_by_xpath(f'//*[@id="qtip-5-content"]/div/div/div/ul/li[{filter_index}]/a').click()
        print('Filtro Carregado.\n')
    else:
        print('Filtro não encontrado. Por favor, verifique o nome.')


def select_empresa(empresa, xpath):
    """ Encontra a empresa na lista de seleção - combobox"""
    for option in driver.find_element_by_xpath(xpath).find_elements_by_tag_name('option'):
        if option.get_attribute('label') == empresa:
            option.click()


def submit_report(driver, report_name):
    driver.find_element_by_xpath(parametros_xpath['Titulo']).clear()
    driver.find_element_by_xpath(parametros_xpath['Titulo']).send_keys(report_name)
    driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/footer/button').click()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Relatório Gerado: ', report_name)
    sleep(5)


def find_report(driver, report_name):
    """ Encontra o índice do relatório e verifica sua disponibilidade para download"""
    html = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]').get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    reports = soup.find('ul').find_all('li', class_='item ng-scope')
    for n, report in enumerate(reports):
        if reports[n].find('h5').text == report_name:
            # print(n + 1, reports[n].find('h5').text, reports[n].find_all('span')[4].text)
            available = int(reports[1].find_all('span')[4].text.split(':')[1].strip().split(' ')[0]) < 0
            return n + 1, available


def get_all_reports(driver):
    html = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]').get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    reports = soup.find('ul').find_all('li', class_='item ng-scope')
    result = {}
    for n, report in enumerate(reports):
        available = int(reports[n].find_all('span')[4].text.split(':')[1].strip().split(' ')[0]) < 0
        id_report = reports[n].find_all('span')[5].text.split(':')[1].strip()
        creation = reports[n].find_all('span')[3].text
        result[n + 1] = {'Name': reports[n].find('h5').text, 'Download': available, 'ID': id_report, 'Creation': creation}
    return result


def scrolldown_load_older_reports(driver):
    """ Scroll down na lista de relatórios disponíveis, carregar mais relatórios """
    for i in range(5):
        element = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]/div/button')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]/div/button').click()
        sleep(3)


def download_report(driver):
    driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{index}]/button[1]').click()
    sleep(4)
    driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{index}]/span[1]/a[2]/i').click()
    to_be_downloaded.remove(report)
    sleep(4)


if __name__ == '__main__':
    temp_ini = datetime.now().replace(microsecond=0)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get('https://app.hugme.com.br/')
    sleep(3)

    login(driver)
    sleep(3)

    driver.get('https://app.hugme.com.br/app.html#/dados/tickets/exportar/')
    while 'Novo relatório' not in driver.page_source:
        pass

    select_preset_filter(driver)

    new_reports = []
    for empresa, selection_name in empresas.items():
        select_empresa(empresa=selection_name, xpath=parametros_xpath['Empresa'])
        titulo = empresa + '_' + str(time()).replace('.', '')
        submit_report(driver, report_name=titulo)
        new_reports.append(titulo)

    to_be_downloaded = new_reports.copy()
    print('\nVerificando disponibilidade de download...\n')

    while not to_be_downloaded == []:
        driver.refresh()
        while 'Carregar mais' not in driver.page_source: pass
        sleep(20)

        for report in to_be_downloaded:
            index, available = find_report(driver, report_name=report)
            if available:
                download_report(driver)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Download: ', report)

    print('Extração concluída.\n')
    print('Tempo de execução: ', datetime.now().replace(microsecond=0) - temp_ini)
    driver.close()
    driver.quit()

