
empresa = [
    'Extra.com.br',
    'Barateiro.com',
    'Bartira Móveis',
]

filter_name = 'Simulador SQUAD GPA'

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