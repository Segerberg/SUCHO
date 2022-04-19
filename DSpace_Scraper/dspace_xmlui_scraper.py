import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urlparse

"""
USAGE

python dspace_xmlui_scraper.py https://dspace.somewhere.com

"""

def get_records(url):
    try:
        headers = {
            'User-Agent': 'DSPACE-Scraper'
        }
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        divs = soup.find_all('div', {'class':'artifact-title'})
        current_page = soup.find('li', {'class': 'current-page-link'}).find('a', href=True).text
        next_page = soup.find('a', {'class': 'next-page-link'})
        try:
            last_page = soup.find('li', {'class': 'last-page-link'}).find('a', href=True).text
        except AttributeError:
            last_page = None
            pass

        print(f"Getting records: page {current_page} of {last_page}")
        for div in divs:
            link = div.find('a', href=True)
            records.append(link['href'])
        if next_page:
            get_records(base_url + '/xmlui/' + next_page['href'])

    except requests.exceptions.ConnectionError as e:
        print(e)
        pass


if __name__ == '__main__':
    base_url = sys.argv[1]
    records = []
    get_records(base_url+"/xmlui/discover?rpp=100&etal=0&scope=/&group_by=none")

    with open(f"{urlparse(base_url).netloc}.txt", 'w') as f:
        for record in records:
            f.write(f'{base_url}{record}')
            f.write('\n')

