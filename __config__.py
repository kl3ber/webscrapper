
chrome_version = '75.0.3770.100'
# chrome_version = '73.0.3683.68'

empresas = {
    'EXTRA': 'Extra.com.br',
    'BARATEIRO': 'Barateiro.com',
    'BARTIRA': 'Bartira Móveis',
}

filter_name = 'SQUAD VVJ'

parametros_xpath = {
    'Empresa': '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/select',
    'Titulo': '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/input',
    'Periodo': '//*[@id="periodoPreDefinido"]',
    'Ordenação': [
        '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[4]/select[1]',
        '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[4]/select[2]',
    ],
    'Filtro': '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/ul/li/select',

}