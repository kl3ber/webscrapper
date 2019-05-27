
# Parâmetros do Relatório
driver.find_element_by_xpath(parametros_xpath['Empresa']).send_keys(empresa[0])
driver.find_element_by_xpath(parametros_xpath['Titulo']).send_keys(titulo)

driver.find_element_by_xpath('//*[@id="preDefinido"]').click()
driver.find_element_by_xpath(parametros_xpath['Periodo']).send_keys('Mês Corrente')

driver.find_element_by_xpath(parametros_xpath['Ordenação'][0]).send_keys('Data Reclamação')
driver.find_element_by_xpath(parametros_xpath['Ordenação'][1]).send_keys('decrescente')

driver.find_element_by_xpath(parametros_xpath['Filtro']).send_keys('Origens')
driver.find_element_by_xpath('//*[@id="s2id_autogen14"]').send_keys('ReclameAQUI')