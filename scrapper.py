
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome(ChromeDriverManager(version='73.0.3683.68').install())
driver.maximize_window()
driver.get('https://app.hugme.com.br/')
time.sleep(3)

uid = 'fabricio.sbravatti@atento.com'
pwd = 'Atento2019'

empresa = ['Extra.com.br', ]
titulo = str(time.time()).replace('.', '')

# Login
driver.find_element_by_id('user').send_keys(uid)
driver.find_element_by_id('password').send_keys(pwd)
driver.find_element_by_xpath('//*[@id="submit-button"]').click()

if driver.find_element_by_id('error-message').get_attribute('innerHTML') != '':
    print('Muitos usuários logados. Tente mais tarde em um horário com fluxo de pessoas menor.')

time.sleep(5)
driver.get('https://app.hugme.com.br/app.html#/dados/monitor/exportar/')
time.sleep(5)

# Parâmetros do Relatório
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/select').send_keys(empresa[0])
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/input').send_keys(titulo)
driver.find_element_by_xpath('//*[@id="periodoPreDefinido"]').send_keys('Ontem')
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/div[2]/div[2]/ul/li[31]/label/input').click()

# Gerar relatório
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/div/footer/button').click()
driver.refresh()
time.sleep(5)

# Encontrar índice do relatório
html = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div[2]').get_attribute('innerHTML')
soup = BeautifulSoup(html, 'html.parser')
reports = soup.find('ul').find_all('li')
li = None
while li is None:
    for n in range(len(reports) - 2):
        if reports[n].find('h5').text.strip() == titulo:
            print(n, reports[n].find('h5').text.strip())
            li = n + 1
            break

if li is None:
    print('Erro')

# Baixar Relatório
driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{li}]/button[1]').click()
time.sleep(5)

# Excluir Relatório
driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div/div[2]/div/div[2]/ul/li[{li}]/span[1]/a[2]/i').click()

print('Extração concluída.')


#driver.close()
#driver.quit()





