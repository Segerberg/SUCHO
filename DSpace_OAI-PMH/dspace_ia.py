from lxml import etree
from sickle import Sickle
import sys
import validators
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_nav_links(url, headers):
    yield url
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    nav = soup.find_all('nav')
    for n in nav:
        links = n.find_all('a', href=True)
        for link in links:
            if validators.url(link['href']):
                yield link['href']

def get_records(url, headers):
    sickle = Sickle(url, headers=headers)
    records = sickle.ListRecords(metadataPrefix='oai_dc')
    parser = etree.XMLParser()
    nsmap = {"oai": "http://www.openarchives.org/OAI/2.0/",
             "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
             "dc": "http://purl.org/dc/elements/1.1/"}

    for record in records:
        tree = etree.fromstring(str(record), parser)
        dc = tree.xpath("//oai:record/oai:metadata/oai_dc:dc", namespaces=nsmap)
        if len(dc) >= 1:
            dc = dc[0]
            for element in dc:
                try:
                    if validators.url(element.text):
                        yield element.text
                except TypeError:
                    pass
    return sickle

def main(url, headers):
    paths = ["/oai/openaire","/oai/request", "/oai2/request"]
    try:
        yield from get_records(url, headers)
    except:
        for path in paths:
            u = urlparse(url)
            try:
                yield from get_records(f'{u.scheme}://{u.netloc}{path}')
            except:
                continue

if __name__ == '__main__':
    headers = {
        'User-Agent': 'OAI-Harvester'
    }
    url = sys.argv[1]
    scheme= urlparse(url).scheme
    hostname = urlparse(url).hostname
    for link in get_nav_links(f"{scheme}://{hostname}", headers):
      print(link)

    for record in main(url, headers):
      print(record)


