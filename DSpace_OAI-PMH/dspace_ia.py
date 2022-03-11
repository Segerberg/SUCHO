from lxml import etree
from sickle import Sickle
import sys
import validators
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_nav_links(url):
    print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    nav = soup.find_all('nav')
    for n in nav:
        links = n.find_all('a', href=True)
        for link in links:
            if validators.url(link['href']):
                print(link['href'])

def main(url):
    sickle = Sickle(url)
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
                        print(element.text)
                except TypeError:
                    pass


if __name__ == '__main__':
    url = sys.argv[1]
    scheme= urlparse(url).scheme
    hostname = urlparse(url).hostname
    get_nav_links(f"{scheme}://{hostname}")

    main(url)
