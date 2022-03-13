import logging
import os
import datetime

import click
import requests
from lxml import etree
from tqdm.auto import tqdm


def download_file(url, savepath, file_id):
    suffix = url.split('.')[-1]        
    local_filename = f"{file_id}.{suffix}"
    
    if not os.path.exists(os.path.join(savepath, local_filename)):
        response = requests.get(url, stream=True)

        with tqdm.wrapattr(
                open(os.path.join(savepath, local_filename), "wb"), "write",
                unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                desc=local_filename, total=int(response.headers.get('content-length', 0))
        ) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)


@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--replace', '-r', multiple=True)

def get_data(input_dir, replace):
    nsmap = {"oai": "http://www.openarchives.org/OAI/2.0/", "mets": "http://www.loc.gov/METS/",
             "xlink": "http://www.w3.org/1999/xlink"}
    root_dir = input_dir
    parser = etree.XMLParser()
    total_records = len(os.listdir(root_dir))
    count = 0
    log_format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename=os.path.join(f"dspace_download_{datetime.datetime.now().strftime('%Y%m%d-%H_%M_%S')}.log"),
                        filemode="w",
                        format=log_format,
                        level=logging.INFO)

    logger = logging.getLogger()

    for root, dir, files in os.walk(root_dir):
        count += 1
        tqdm.write(f"{count}/{total_records}")
        for file in files:
            if file.endswith(".xml") and len(files) == 1:

                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as file:
                    metsfile = file.read()
                    tree = etree.fromstring(metsfile, parser)
                    fileGrp = tree.xpath("//oai:record/oai:metadata/mets:mets/mets:fileSec/mets:fileGrp",
                                         namespaces=nsmap)
                    for grp in fileGrp:
                        mfiles = grp.xpath("mets:file", namespaces=nsmap)
                        for r in mfiles:
                            href = r.xpath("mets:FLocat/@xlink:href", namespaces=nsmap)
                            file_id = r.xpath("@ID", namespaces=nsmap)[0]
                            url = href[0]
                            if replace:
                                url = href[0].replace(replace[0], replace[1])

                            try:
                                download_file(url, root, file_id)

                            except requests.exceptions.ConnectionError:
                                logger.error(f'Failed to download {url}')
                                pass

if __name__ == '__main__':
    get_data()
