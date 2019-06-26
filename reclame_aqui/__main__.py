
import requests
from bs4 import BeautifulSoup
import json

r = requests.get('https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/companies/redirect')
soup = BeautifulSoup(r.text, 'html.parser')
soup

r.json()