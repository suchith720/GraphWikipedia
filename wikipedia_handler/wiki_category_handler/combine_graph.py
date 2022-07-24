from .helper import *
from .graph_container import *


class WikiGraphCombine:

    def __init__(self, partition_files=None):
        self.partition_files = partition_files

        self.parameters = {}
        self.parameters['id_to_title'] = {}
        self.parameters['redirects'] = {}

        self.parameters['label_id_to_title'] = {}
        self.parameters['label_redirects'] = {}

        self.parameters['wiki_content'] = {}

        self.parameters['label_graph'] = {}
        self.parameters['article_graph'] = {}
        self.parameters['classification_graph'] = {}

    def load_param(self, data_path, save_dir, param='id_to_title', graph_resolved=True, tag_extractor=None):
        wikidataset = WikiGraphDataset()
        tag = extract_filetag(data_path, tag_extractor)

        if param == 'id_to_title':
            wikidataset.load_idtotitle(save_dir=save_dir, tag=tag, id_type="article")
            return wikidataset.id_to_title
        elif param == 'label_id_to_title':
            wikidataset.load_idtotitle(save_dir=save_dir, tag=tag, id_type="label")
            return wikidataset.label_id_to_title
        elif param == 'redirects':
            wikidataset.load_redirects(save_dir=save_dir, tag=tag, redirect_type="article")
            return wikidataset.redirects
        elif param == 'label_redirects':
            wikidataset.load_redirects(save_dir=save_dir, tag=tag, redirect_type="label")
            return wikidataset.label_redirects
        elif param == 'wiki_content':
            wikidataset.load_wikicontent(save_dir=save_dir, tag=tag)
            return wikidataset.wiki_content
        elif param == 'article_graph':
            if graph_resolved:
                tag = f'{tag}_resolved'
            wikidataset.load_graph(save_dir=save_dir, tag=tag, graph_type='article')
            self.convert_graph(wikidataset.article_graph.graph)
            return wikidataset.article_graph.graph
        elif param == 'label_graph':
            if graph_resolved:
                tag = f'{tag}_resolved'
            wikidataset.load_graph(save_dir=save_dir, tag=tag, graph_type='label')
            self.convert_graph(wikidataset.label_graph.graph)
            return wikidataset.label_graph.graph
        elif param == 'classification_graph':
            if graph_resolved:
                tag = f'{tag}_resolved'
            wikidataset.load_graph(save_dir=save_dir, tag=tag, graph_type='classification')
            self.convert_graph(wikidataset.classification_graph.graph)
            return wikidataset.classification_graph.graph
        else:
            raise Exception(f'Invalid value of param : {param}')

    def combine_param(self, save_dir, param='id_to_title', graph_resolved=True, tag_extractor=None):
        combine_helper = partial(self.load_param, param=param, save_dir=save_dir, graph_resolved=graph_resolved,
                                 tag_extractor=tag_extractor)
        self.parameters[param] = multiprocessor_1(combine_helper, self.partition_files)

    def convert_graph(self, graph):
        if len(graph) and isinstance(graph, dict):
            key = list(graph.keys())[0]
            if isinstance(graph[key], tuple):
                for doc, (edges, counts) in graph.items():
                    graph[doc] = {e:c for e, c in zip(edges, counts)}
            elif isinstance(graph[key], dict):
                for doc, edge_count in graph.items():
                    graph[doc] = (list(edge_count.keys()), list(edge_count.values()))
            else:
                raise Exception("Invalid graph format.")

    def save_idtotitle(self, save_dir, tag='', id_type="all"):
        if id_type == "article" or id_type == "all":
            os.makedirs(save_dir, exist_ok=True)
            map_file = f'{save_dir}/id_to_title{tag}.pickle'
            with open(map_file, 'wb') as f:
                pickle.dump(self.parameters['id_to_title'], f)
        if id_type == "label" or id_type == "all":
            os.makedirs(save_dir, exist_ok=True)
            map_file = f'{save_dir}/label_id_to_title{tag}.pickle'
            with open(map_file, 'wb') as f:
                pickle.dump(self.parameters['label_id_to_title'], f)

    def load_idtotitle(self, save_dir, tag='', id_type="all"):
        if id_type == "article" or id_type == "all":
            map_file = f'{save_dir}/id_to_title{tag}.pickle'
            with open(map_file, 'rb') as f:
                self.parameters['id_to_title'] = pickle.load(f)
        if id_type == "label" or id_type == "all":
            map_file = f'{save_dir}/label_id_to_title{tag}.pickle'
            with open(map_file, 'rb') as f:
                self.parameters['label_id_to_title'] = pickle.load(f)

    def save_wikicontent(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'wb') as f:
            pickle.dump(self.parameters['wiki_content'], f)

    def load_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'rb') as f:
            self.parameters['wiki_content'] = pickle.load(f)

    def save_redirects(self, save_dir, tag='', redirect_type="all"):
        if redirect_type == "article" or redirect_type == "all":
            os.makedirs(save_dir, exist_ok=True)
            redirect_file = f'{save_dir}/redirects{tag}.pickle'
            with open(redirect_file, 'wb') as f:
                pickle.dump(self.parameters['redirects'], f)
        if redirect_type == "label" or redirect_type == "all":
            os.makedirs(save_dir, exist_ok=True)
            redirect_file = f'{save_dir}/label_redirects{tag}.pickle'
            with open(redirect_file, 'wb') as f:
                pickle.dump(self.parameters['label_redirects'], f)

    def load_redirects(self, save_dir, tag='', redirect_type="all"):
        if redirect_type == "article" or redirect_type == "all":
            redirect_file = f'{save_dir}/redirects{tag}.pickle'
            with open(redirect_file, 'rb') as f:
                self.parameters['redirects'] = pickle.load(f)
        if redirect_type == "label" or redirect_type == "all":
            redirect_file = f'{save_dir}/label_redirects{tag}.pickle'
            with open(redirect_file, 'rb') as f:
                self.parameters['label_redirects'] = pickle.load(f)

    def save_graph(self, save_dir, tag='', graph_type='classification'):
        if graph_type != 'classification' and graph_type != 'article' and graph_type != "label":
            raise Exception("graph_type can only take values in ['classification', 'article', 'label']")

        os.makedirs(save_dir, exist_ok=True)
        graph_file = f'{save_dir}/link_graph_{graph_type}{tag}.pickle'
        with open(graph_file, 'wb') as f:
            pickle.dump(self.parameters[f'{graph_type}_graph'], f)

    def load_graph(self, save_dir, tag='', graph_type='classification'):
        if graph_type != 'classification' and graph_type != 'article' and graph_type != "label":
            raise Exception("graph_type can only take values in ['classification', 'article', 'label']")

        graph_file = f'{save_dir}/link_graph_{graph_type}{tag}.pickle'
        with open(graph_file, 'rb') as f:
            self.parameters[f'{graph_type}_graph'] = pickle.load(f)

    def remove_nodes_from_articles(self, nodes):
        articles = self.parameters['article_graph']
        if not articles:
            raise Exception('Article graph is empty.')

        for node in tqdm.tqdm( list(articles.keys()) ):
            if node in nodes:
                del articles[node]
            else:
                for edge in list(articles[node].keys()):
                    if edge in nodes:
                        del articles[node][edge]

