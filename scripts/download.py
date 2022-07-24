import os
import re
import sys
import ssl
import argparse
import requests
import tensorflow as tf
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

"""
Adding paths to the configuration files and amazon graph packages.
"""
config_path = os.path.join(os.getcwd(), 'config')
sys.path.append(config_path)

from wikipedia_config import *


if __name__ == '__main__':
    """
    Check if the variable are properly defined in the paths file.
    """
    paths = ['project', 'dump_date', 'dataset_home']
    for path in paths:
        if path not in vars():
            raise Exception(f'Variable {path} not defined in the config file.')


    """
    Processing command line arguements.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-w","--dumps", help="Download the wikipedia dumps",
                                        action="store_true")
    parser.add_argument("-d","--dates", help="prints out wikipedia-dump dates",
                                        action="store_true")
    parser.add_argument("-a","--abstract", help="Download abstract dumps",
                                        action="store_true")
    args = parser.parse_args()


    """
    Downloading wikipedia dumps.
    """
    base_url = f'https://dumps.wikimedia.org/{project}/'

    """
    Print dump dates.
    """
    if args.dates:
        index = requests.get(base_url).text
        soup_index = BeautifulSoup(index, 'html.parser')
        dates = [ a.text for a in soup_index.find_all('a') if a.has_attr('href') ]
        print("The following dump dates are available : ")
        for date in dates:
            print(f"-- {date}")
        exit()

    """
    Get all the files to download by extracting the information
    from the scraped html files
    """
    dump_url = base_url + dump_date
    dump_html = requests.get(dump_url).text
    soup_dump = BeautifulSoup(dump_html, 'html.parser')

    files = []
    for file in soup_dump.find_all('li', {'class': 'file'}):
        text = file.text
        files.append((text.split(' ')[0], text.split(' ')[1:]))

    if args.dumps:
        file_to_download = [ file[0] for file in files
                    if '.xml-p' in file[0] and 'pages-articles' in file[0] and 'multistream' in file[0]]
    elif args.abstract:
        pattern = re.compile(f'{project}-{dump_date}-abstract'+r'[0-9]{1,2}.xml.gz')
        file_to_download = [ file[0] for file in files if pattern.match(file[0])]

    """
    Download all the files.
    """
    data_paths = []
    dump_dir = f'{dataset_home}/{dump_dirname}'
    for file in file_to_download:
        path = f'{dump_dir}/{file}'
        if not os.path.exists(path):
            data_paths.append( tf.keras.utils.get_file(origin=f'{dump_url}/{file}', cache_dir=dataset_home, cache_subdir=dump_dirname) )
        else:
            data_paths.append(path)

