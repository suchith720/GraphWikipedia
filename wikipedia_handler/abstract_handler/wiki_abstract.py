from .abstract_xml_handler import *
import bz2
import tqdm
import pickle
import subprocess
from functools import partial
from multiprocessing import Pool

class WikiAbstract:

    def __init__(self, abstract_paths=None):
        self.abstract = {}
        self.abstract_paths = abstract_paths

    def parse_abstract(self, abstract_file):
        handler = AbstractXmlHandler()

        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        for i, line in enumerate( subprocess.Popen(['gzip','-cd'],
                                                  stdin=open(abstract_file),
                                                  stdout=subprocess.PIPE ).stdout ):
            try:
                parser.feed(line)
            except StopIteration:
                break

        return handler._abstract

    def create_abstract(self, processes=15):
        pool = Pool(processes=processes)
        if self.abstract_paths is None:
            raise Exception("Abstract paths are empty.")
        for abstract in tqdm.tqdm(pool.imap_unordered(self.parse_abstract, self.abstract_paths),
                                           total=len(self.abstract_paths)):
            self.abstract.update(abstract)

    def save_abstract(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        abstract_file = f'{save_dir}/abstract{tag}.pickle'
        with open(abstract_file, 'wb') as f:
            pickle.dump(self.abstract, f)

    def load_abstract(self, save_dir, tag=''):
        abstract_file = f'{save_dir}/abstract{tag}.pickle'
        if os.path.exists(abstract_file):
            with open(abstract_file, 'rb') as f:
                self.abstract = pickle.load(f)
        else:
            raise Exception(f"Unable to load abstract from '{abstract_file}'.")

