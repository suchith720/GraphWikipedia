import os
import re
import sys


"""
Adding paths to the configuration files and amazon graph packages.
"""
config_path = os.path.join(os.getcwd(), 'config')
package_path = os.path.join(os.getcwd(), 'wikipedia_handler')
sys.path.append(config_path)
sys.path.append(package_path)


from wikipedia_config import *
from abstract_handler import *


if __name__ == '__main__':
    """
    Check if the variable are properly defined in the config file.
    """
    paths = ['project', 'dump_date', 'dataset_home', 'dump_dirname', 'abstract_dir']
    for path in paths:
        if path not in vars():
            raise Exception(f'Variable {path} not defined in the config file.')


    """
    Collect all the abstract path using the regex expression.
    """
    dump_dir = f'{dataset_home}/{dump_dirname}'
    prog = re.compile(f'({project}-{dump_date})-'+r'abstract([0-9]{1,2}).xml.gz')
    abstract_paths = sorted([f'{dump_dir}/{file}' for file in os.listdir(f'{dump_dir}')
                     if prog.match(file)])
    print(f'-- Total number of partitions of the wikipedia dump : {len(abstract_paths)}\n')


    """
    Process all the abstract files.
    """
    abstract = WikiAbstract(abstract_paths)
    abstract.create_abstract()
    abstract.save_abstract(abstract_dir, tag=f'-{project}-{dump_date}')
