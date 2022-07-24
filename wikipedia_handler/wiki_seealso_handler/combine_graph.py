from .helper import *
from .graph_container import *


class WikiGraphCombine:

    def __init__(self, partition_files=None):
        self.partition_files = partition_files

        self.parameters = {}
        self.parameters['id_to_title'] = {}
        self.parameters['redirects'] = {}
        self.parameters['wiki_content'] = {}

        self.parameters['seealso_graph'] = {}
        self.parameters['articles_graph'] = {}

    def load_param(self, data_path, save_dir, param='id_to_title', graph_resolved=True, tag_extractor=None):
        wikidataset = WikiGraphDataset()
        tag = extract_filetag(data_path, tag_extractor)

        if param == 'id_to_title':
            wikidataset.load_idtotitle(save_dir=save_dir, tag=tag)
            return wikidataset.id_to_title
        elif param == 'redirects':
            wikidataset.load_redirects(save_dir=save_dir, tag=tag)
            return wikidataset.redirects
        elif param == 'wiki_content':
            wikidataset.load_wikicontent(save_dir=save_dir, tag=tag)
            return wikidataset.wiki_content
        elif param == 'seealso_graph':
            if graph_resolved:
                tag = f'{tag}_resolved'
            wikidataset.load_graph(save_dir=save_dir, tag=tag, graph_type='seealso')
            self.convert_graph(wikidataset.seealso_graph.graph)
            return wikidataset.seealso_graph.graph
        elif param == 'articles_graph':
            if graph_resolved:
                tag = f'{tag}_resolved'
            wikidataset.load_graph(save_dir=save_dir, tag=tag, graph_type='articles')
            self.convert_graph(wikidataset.article_graph.graph)
            return wikidataset.article_graph.graph
        else:
            raise Exception(f'Invalid value of param : {param}')

    def combine_param(self, save_dir, param='id_to_title', tag_extractor=None):
        combine_helper = partial(self.load_param, param=param, save_dir=save_dir, tag_extractor=tag_extractor)
        self.parameters[param] = multiprocessor_1(combine_helper, self.partition_files)

    def remove_seealso_edges(self):
        seealso = self.parameters['seealso_graph']
        articles = self.parameters['articles_graph']

        if seealso and articles:
            for node_1, edge_count in seealso.items():
                for node_2 in edge_count:
                    if node_1 in articles and node_2 in articles[node_1]:
                        del articles[node_1][node_2]
                        if len(articles[node_1]) == 0:
                            del articles[node_1]
                    if node_2 in articles and node_1 in articles[node_2]:
                        del articles[node_2][node_1]
                        if len(articles[node_2]) == 0:
                            del articles[node_2]

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

    def save_idtotitle(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        map_file = f'{save_dir}/id_to_title{tag}.pickle'
        with open(map_file, 'wb') as f:
            pickle.dump(self.parameters['id_to_title'], f)

    def load_idtotitle(self, save_dir, tag=''):
        map_file = f'{save_dir}/id_to_title{tag}.pickle'
        with open(map_file, 'rb') as f:
            self.parameters['id_to_title'] = pickle.load(f)

    def save_wikicontent(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'wb') as f:
            pickle.dump(self.parameters['wiki_content'], f)

    def load_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'rb') as f:
            self.parameters['wiki_content'] = pickle.load(f)

    def save_redirects(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        with open(redirect_file, 'wb') as f:
            pickle.dump(self.parameters['redirects'], f)

    def load_redirects(self, save_dir, tag=''):
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        with open(redirect_file, 'rb') as f:
            self.parameters['redirects'] = pickle.load(f)

    def save_graph(self, save_dir, tag='', graph_type='seealso'):
        if graph_type != 'seealso' and graph_type != 'articles':
            raise Exception("graph_type can not take in ['seealso', 'articles']")

        os.makedirs(save_dir, exist_ok=True)
        graph_file = f'{save_dir}/link_graph_{graph_type}{tag}.pickle'
        with open(graph_file, 'wb') as f:
            pickle.dump(self.parameters[f'{graph_type}_graph'], f)

    def load_graph(self, save_dir, tag='', graph_type='seealso'):
        if graph_type != 'seealso' and graph_type != 'articles':
            raise Exception("graph_type can not take in ['seealso', 'articles']")

        graph_file = f'{save_dir}/link_graph_{graph_type}{tag}.pickle'
        with open(graph_file, 'rb') as f:
            self.parameters[f'{graph_type}_graph'] = pickle.load(f)

    def remove_nodes_from_articles(self, nodes):
        articles = self.parameters['articles_graph']
        if not articles:
            raise Exception('Article graph is empty.')

        for node in tqdm.tqdm( list(articles.keys()) ):
            if node in nodes:
                del articles[node]
            else:
                for edge in list(articles[node].keys()):
                    if edge in nodes:
                        del articles[node][edge]

