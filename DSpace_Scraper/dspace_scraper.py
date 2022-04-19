import requests
from bs4 import BeautifulSoup
import click
from urllib.parse import urlparse
import sys


def get_xmlui_records(base_url, url):
    try:
        headers = {
            'User-Agent': 'DSPACE-Scraper'
        }
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        divs = soup.find_all('div', {'class':'artifact-title'})
        try:
            current_page = soup.find('li', {'class': 'current-page-link'}).find('a', href=True).text
        except AttributeError:
            print("xmlui not working try using --ui jspui instead ")
            sys.exit(1)

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
            get_xmlui_records(base_url, base_url + '/xmlui/' + next_page['href'])

    except requests.exceptions.ConnectionError as e:
        print(e)
        pass


def get_jspui_records(base_url, url):
    try:
        headers = {
            'User-Agent': 'DSPACE-Scraper'
        }
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        tds = soup.find_all('td', {'headers':'t2'})
        next_page = soup.find('div', {'class': 'panel-footer'}).find('a', {'class':'pull-right'})
        for td in tds:
            link = td.find('a', href=True)
            print(link['href'])
            records.append(link['href'])
        if next_page:
            get_jspui_records(base_url, base_url + next_page['href'])
    except requests.exceptions.ConnectionError as e:
        print(e)
        pass

@click.command()
@click.option('--url')
@click.option('--ui', default='xmlui')
def main(url, ui):
    base_url = url
    if ui == 'xmlui':
        get_xmlui_records(base_url, base_url + "/xmlui/discover?rpp=100&etal=0&scope=/&group_by=none")
    elif ui =='jspui':
        get_jspui_records(base_url, base_url + '/jspui/browse?type=dateissued&sort_by=2&order=ASC&rpp=100')
    else:
        raise

    with open(f"{urlparse(base_url).netloc}.txt", 'w') as f:
        for record in records:

            f.write(f'{base_url}{record}')
            f.write('\n')

if __name__ == '__main__':
    records = []
    main()






