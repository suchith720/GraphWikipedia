import re
import tqdm
import numpy as np
from functools import partial
from multiprocessing import Pool


def dict_head_random(dictionary, n=10):
    keys = np.random.choice(list(dictionary.keys()), size=n)
    for k in keys:
        print(f'{k} : {dictionary[k]}')


def multiprocessor_1(func, tasks, num_process=10):
    pool = Pool(processes=num_process)
    results = {}
    for x in tqdm.tqdm( pool.imap(func, tasks), total=len(tasks)):
        results.update(x)
    return results


def extract_filetag(data_path, tag_extractor=None):
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
    return file_tag


def multiprocessor_2(func, tasks, num_process=10):
    pool = Pool(processes=num_process)
    results = []
    for x in tqdm.tqdm( pool.imap(func, tasks), total=len(tasks)):
        results.append(x)
    return results

