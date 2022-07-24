from .helper import *
from .graph import *


class ResolveGraph:

    def __init__(self, partition_files):
        self.partition_files = partition_files
        self.id_to_title, self.redirects = None, None

    def change_maps(self, id_to_title, redirects):
        self.id_to_title = id_to_title
        self.redirects = redirects

        self.title_to_id = {article_title:article_id for article_id, article_title in id_to_title.items()}

    def resolver(self, data_path, save_dir, graph_type='article', tag_extractor=None):
        if graph_type != 'classification' and graph_type != 'article' and graph_type != "label":
            raise Exception("graph_type can only take values in ['classification', 'article', 'label']")

        graph = WikilinkGraph()
        tag = extract_filetag(data_path, tag_extractor)

        tag=f'_{graph_type}{tag}'
        graph.load_data(save_dir, tag)

        graph.replace_redirects(self.redirects)
        graph.remove_dead(self.title_to_id)

        tag = f'{tag}_resolved'
        graph.save_data(save_dir, tag)

    def resolve(self, save_dir, graph_type='article', tag_extractor=None):
        resolve_helper = partial(self.resolver, save_dir=save_dir, graph_type=graph_type,
                                 tag_extractor=tag_extractor)
        multiprocessor_2(resolve_helper, self.partition_files)

