from warcio.capture_http import capture_http
import requests
import os
import json
import datetime
out_dir = "dlib.ukma.edu.ua"
warc = f"dlib.ukma.edu.ua_{datetime.datetime.now().strftime('%Y%m%d-%H_%M_%S')}_.warc.gz"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

seen = []

def get_next_header_links(header):
    header_links = {}
    if not 'link' in header:
        return None
    for l in header['link'].split(','):
        h = l.split(';')
        header_links[h[1].split('=')[1].replace('"', "")] = h[0].replace("<",'').replace(">",'')
    if not 'next' in header_links:
        return None
    return header_links['next']


def get(next):
    print(next)
    with capture_http(os.path.join(out_dir,warc)):
        r = requests.get(next)
        next_link = get_next_header_links(r.headers)
        if next_link:
            data = json.loads(r.content)
            for i in data:
                if 'url' in i:
                    link = i['url']
                    if link not in seen:
                        get(link)
                if 'files' in i:
                    link = i['files']['url']
                    if link not in seen:
                        get(i['files']['url'])
                if 'file_urls' in i:
                    link = i['file_urls']['original']
                    if link not in seen:
                        get(i['file_urls']['original'])



endpoints = ['site','items', 'resources', 'collections',
             'files', 'item_types', 'elements', 'element_sets',
             'users', 'tags', 'exhibits', 'exhibit_pages', 'simple_pages',
             'artifacts', 'persons', 'extended_collections', 'extended_items'
             ]

for e in endpoints:
    get(f'https://dlib.ukma.edu.ua/api/{e}')



