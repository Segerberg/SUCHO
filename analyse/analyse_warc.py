import json
import os
import sys
from warcio.archiveiterator import ArchiveIterator
from urllib.parse import urlparse
import multiprocessing


def main(root_dir):
    data = {
        "warcs": [],
    }

    warcs_to_analyse = []
    stat_file = os.path.join('stats.json')

    if os.path.isfile(stat_file):
        with open(stat_file, 'r') as json_file:
            data = json.loads(json_file.read())

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('warc.gz') and file not in data['warcs']:
                warcs_to_analyse.append(os.path.join(root, file))
                data['warcs'].append(file)

    with multiprocessing.Pool(50) as pool:
        print(f'Staring with: {len(warcs_to_analyse)} warcs to analyse')
        for w in pool.map(analyse_warc, warcs_to_analyse):
            if w:
                for host, value in w.items():
                    if not host in data:
                        data[host] = {"count": value['count'], "size": value['size'], "mimes": value['mimes']}
                    else:
                        data[host]['count'] += value['count']
                        data[host]['size'] += value['size']
                        for mime, n in value['mimes'].items():
                            if mime in data[host]['mimes']:
                                data[host]['mimes'][mime] += n
                            else:
                                data[host]['mimes'][mime] = n

    with open(stat_file, 'w') as out_file:
        out_file.write(json.dumps(data, indent=4))

def analyse_warc(warc_file):
    data = {}
    try:
        with open(warc_file, 'rb') as stream:
            print(f'reading: {warc_file}')
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
                        if not host in data:
                            data[host] = {"count": 1, "size":int(content_length), "mimes":{mime:1}}
                        else:
                            data[host]['count'] += 1
                            data[host]['size'] += int(content_length)
                            if mime in data[host]['mimes']:
                                data[host]['mimes'][mime] += 1
                            else:
                                data[host]['mimes'][mime] = 1

    except:
        pass
    return data


if __name__ == "__main__":
    root_dir = sys.argv[1]
    main(root_dir)


