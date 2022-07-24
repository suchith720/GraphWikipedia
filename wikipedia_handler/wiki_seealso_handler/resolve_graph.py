from .helper import *
from .graph import *


class ResolveGraph:

    def __init__(self, partition_files, id_to_title, redirects):
        self.partition_files = partition_files
        self.id_to_title = id_to_title
        self.redirects = redirects

        self.title_to_id = {article_title:article_id for article_id, article_title in id_to_title.items()}

    def resolver(self, data_path, save_dir, graph_type='seealso', tag_extractor=None):
        graph = WikilinkGraph()
        tag = extract_filetag(data_path, tag_extractor)

        tag=f'_{graph_type}{tag}'
        graph.load_data(save_dir, tag)

        graph.replace_redirects(self.redirects)
        graph.remove_dead(self.title_to_id)

        tag = f'{tag}_resolved'
        graph.save_data(save_dir, tag)

    def resolve(self, save_dir, graph_type='seealso', tag_extractor=None):
        resolve_helper = partial(self.resolver, save_dir=save_dir, graph_type=graph_type,
                                 tag_extractor=tag_extractor)
        multiprocessor_2(resolve_helper, self.partition_files)

