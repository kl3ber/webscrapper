
from __key__ import uid, pwd
from __config__ import parametros_xpath, empresa, filter_name

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome(ChromeDriverManager(version='73.0.3683.68').install())
driver.maximize_window()
driver.get('https://app.hugme.com.br/')
time.sleep(3)

# Login
driver.find_element_by_id('user').send_keys(uid)
driver.find_element_by_id('password').send_keys(pwd)
driver.find_element_by_xpath('//*[@id="submit-button"]').click()

if driver.find_element_by_id('error-message').get_attribute('innerHTML') != '':
    print('Muitos usuários logados. Tente mais tarde em um horário com fluxo de pessoas menor.')

time.sleep(5)
driver.get('https://app.hugme.com.br/app.html#/dados/tickets/exportar/')
time.sleep(5)


# Filtros
def find_filter_index(driver, filter_name):
    html = driver.find_element_by_xpath('//*[@id="qtip-5-content"]/div/div/div/ul').get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    filters = soup.find_all('li')
    for n, filter in enumerate(filters, start=1):
        if filter.text.strip() == filter_name:
            return n
    return False


driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/footer/div/div[2]/a').click()
filter_index = find_filter_index(driver, filter_name)
if filter_index is False:
    print('Nenhum filtro encontrado com esse nome.')
else:
    driver.find_element_by_xpath(f'//*[@id="qtip-5-content"]/div/div/div/ul/li[{filter_index}]/a').click()


titulo = str(time.time()).replace('.', '')


# Gerar relatório
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/footer/button').click()
driver.refresh()
time.sleep(5)


def find_report_index(driver, report_name):
    """ Encontra o índice do relatório """
    html = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]').get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    reports = soup.find('ul').find_all('li')
    for n, report in enumerate(reports):
        if reports[n].find('h5').text.strip() == report_name:
            print(n, reports[n].find('h5').text.strip())
            return n


# Baixar Relatório
report_li = find_report_index(driver, report_name=titulo)
driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{report_li}]/button[1]').click()
time.sleep(5)

# Excluir Relatório
driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{report_li}]/span[1]/a[2]/i').click()

print('Extração concluída.')


#driver.close()
#driver.quit()





