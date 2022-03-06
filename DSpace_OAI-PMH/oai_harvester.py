from lxml import etree
from sickle import Sickle
import os
import requests
import click
from progress.spinner import PieSpinner
import logging
import datetime


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def get_records(records, parser, nsmap, root_dir):
    c = 0
    total_size = 0
    spinner = PieSpinner('Harvesting... ')
    for record in records:
        spinner.next()
        c += 1
        if c ==5:
            break

        tree = etree.fromstring(str(record), parser)
        id = tree.xpath("//oai:record/oai:header/oai:identifier", namespaces=nsmap)[0].text.replace(":", "_").replace(
            "/", "_")
        fileGrp = tree.xpath("//oai:record/oai:metadata/mets:mets/mets:fileSec/mets:fileGrp", namespaces=nsmap)
        for grp in fileGrp:
            mfiles = grp.xpath("mets:file", namespaces=nsmap)
            for r in mfiles:
                size = r.xpath("@SIZE", namespaces=nsmap)
                total_size += int(size[0])

        path = os.path.join(root_dir, id)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, f"{id}.xml"), 'w', encoding='utf-8') as doc:
            doc.write(etree.tostring(tree, pretty_print=True, encoding="unicode"))

    print(f"\n Saved {c} records")
    print(f"Download size for this collection is: {human_readable_size(total_size)}")

@click.command()
@click.option('--url')
@click.option('--output-dir')

def main(url, output_dir):
    log_format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename=os.path.join(f"oai_harvester_{datetime.datetime.now().strftime('%Y%m%d-%H_%M_%S')}.log"),
                        filemode="w",
                        format=log_format,
                        level=logging.INFO)

    logger = logging.getLogger()

    root_dir = output_dir
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    parser = etree.XMLParser()
    nsmap = {"oai": "http://www.openarchives.org/OAI/2.0/", "mets": "http://www.loc.gov/METS/"}
    sickle = Sickle(url)

    try:
        records = sickle.ListRecords(metadataPrefix='mets')
        get_records(records,parser,nsmap,root_dir)

    except:
        dsets = sickle.ListSets()
        for dset in dsets:
            tree = etree.fromstring(str(dset), parser)
            set_spec = tree.xpath("//oai:set/oai:setSpec", namespaces=nsmap)
            records = sickle.ListRecords(metadataPrefix='mets', set=set_spec[0].text)

            try:
                get_records(records,parser,nsmap,root_dir)
            except requests.exceptions.HTTPError as e:
                logger.error(e)
                continue
    try:
        sets_dir = os.path.join(root_dir,'sets')
        if not os.path.exists(sets_dir):
            os.makedirs(sets_dir)
        sets = sickle.ListSets()
        for s in sets:
            tree = etree.fromstring(str(s), parser)
            setSpec = tree.xpath("//oai:set/oai:setSpec", namespaces=nsmap)[0].text
            with open(os.path.join(sets_dir,f"{setSpec}.xml"), 'w', encoding='utf-8') as set_file:
                set_file.write(etree.tostring(tree, pretty_print=True, encoding="unicode"))
    except:
        raise


if __name__ == '__main__':
    main()

# 'dspace.kntu.kr.ua'
# 'http://dspace.kntu.kr.ua/oai/request'