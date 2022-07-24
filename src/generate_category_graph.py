import os
import sys


"""
Adding paths to the configuration files and amazon graph packages.
"""
config_path = os.path.join(os.getcwd(), 'config')
package_path = os.path.join(os.getcwd(), 'wikipedia_handler')
sys.path.append(config_path)
sys.path.append(package_path)


from category_config import *
from wiki_category_handler import *

import re
import gc
import bz2
import tqdm
import subprocess
from functools import partial
from multiprocessing import Pool
from timeit import default_timer as timer


def create_graph(data_path, save_dir, matches=None, limit=None, save=True, tag_extractor=None,
                 back=True, verbose=True):

    handler = WikiXmlHandler()

    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    for i, line in enumerate(subprocess.Popen(['bzcat'],
                                             stdin = open(data_path),
                                             stdout = subprocess.PIPE).stdout):
        try:
            parser.feed(line)
        except StopIteration:
            break

        if limit is not None and len(handler.wikidataset.id_to_title) >= limit:
            if back:
                return handler.wikidataset
            else:
                break

    if save:
        file_tag = ''
        if isinstance(tag_extractor, re.Pattern):
            parts_tag = tag_extractor.match(os.path.basename(data_path))
            if parts_tag:
                try:
                    file_tag = f'-{parts_tag.group(1)}-{parts_tag.group(2)}-{parts_tag.group(3)}'
                except:
                    file_tag = ''
        elif isinstance(tag_extractor, str):
            file_tag = tag_extractor

        handler.wikidataset.save_data(save_dir, tag=file_tag)
        if verbose:
            print(f"** Completed processing {os.path.basename(data_path)}.\n")

    del handler
    del parser
    gc.collect()

    return None


if __name__ == '__main__':
    """
    Check if the variable are properly defined in the config file.
    """
    paths = ['project', 'dump_date', 'dataset_home', 'dump_dirname', 'limit', 'results_dir']
    for path in paths:
        if path not in vars():
            raise Exception(f'Variable {path} not defined in the config file.')


    """
    Collect all the raw dump paths using the regex expression.
    """
    dump_dir = f'{dataset_home}/{dump_dirname}'
    prog = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')
    dump_paths = sorted([f'{dump_dir}/{file}' for file in os.listdir(f'{dump_dir}')
                         if prog.match(file)])
    print(f'-- Total number of partitions of the wikipedia dump : {len(dump_paths)}')



    """
    Multiprocessing code to process the dumps in parallel and extract graph information.
    """
    tag_extractor = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')
    generate_graph = partial(create_graph, save_dir=results_dir, limit=limit,
            save=True, tag_extractor=tag_extractor, back=False)

    start = timer()
    pool = Pool(processes = 24)
    results = []
    for x in tqdm.tqdm(pool.imap_unordered(generate_graph, dump_paths), total = len(dump_paths)):
        results.append(x)
    pool.close()
    pool.join()
    end = timer()

    print(f'-- Time taken to process the data : {(end - start)/3600:.3f} hours.')

