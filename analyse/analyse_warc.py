import json
import os
import sys
from warcio.archiveiterator import ArchiveIterator
from urllib.parse import urlparse

def main(root_dir):
    data = {
        "warcs":[],
        "total_records": 0
    }
    stat_file = os.path.join(root_dir,'stats.json')
    if os.path.isfile(stat_file):
        with open(stat_file, 'r') as json_file:
            data = json.loads(json_file.read())

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('warc.gz') and file not in data['warcs']:
                data['warcs'].append(file)
                print(f'Readning: {file}')
                with open(os.path.join(root,file), 'rb') as stream:
                    for record in ArchiveIterator(stream):
                        if record.rec_type == 'response':
                            target_uri = record.rec_headers.get_header('WARC-Target-URI')
                            host = urlparse(target_uri).netloc
                            content_length = record.rec_headers.get_header('Content-Length')
                            if record.http_headers:
                                mime = record.http_headers.get_header('Content-Type')
                                if mime:
                                    mime = mime.split(';')[0]
                            if '.ua' in host:
                                data['total_records'] += 1
                                if not host in data:
                                    data[host] = {
                                        "count": 1,
                                        "size":int(content_length),
                                        "mimes":{mime:1},
                                    }
                                else:
                                    data[host]['count'] += 1
                                    data[host]['size'] += int(content_length)
                                    if mime in data[host]['mimes']:
                                        data[host]['mimes'][mime] += 1
                                    else:
                                        data[host]['mimes'][mime] = 1
    with open(stat_file,'w') as out_file:
        out_file.write(json.dumps(data, indent=4))

if __name__ == "__main__":
    root_dir = sys.argv[1]
    main(root_dir)

