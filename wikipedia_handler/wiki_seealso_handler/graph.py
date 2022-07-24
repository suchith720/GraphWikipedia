import os
import gc
import pickle
import numpy as np


class WikilinkGraph:

    def __init__(self):
        self.graph = {}

    def add_article(self, article_id, wikilinks):
        links, count = np.unique(wikilinks, return_counts=True)
        self.graph[article_id] = (links.tolist(), count.tolist())

    def save_data(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)
        filename = f'{save_dir}/link_graph{tag}.pickle'
        with open(filename, 'wb') as f:
            pickle.dump(self.graph, f)

        del self.graph
        gc.collect()

    def load_data(self, save_dir, tag=''):
        filename = f'{save_dir}/link_graph{tag}.pickle'
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.graph = pickle.load(f)
            return True
        print(f"ERROR:: Unable to load the graph at '{filename}'")
        return False

    def replace_redirects(self, redirects):
        for edges, _ in self.graph.values():
            for i, edge in enumerate(edges):
                if edge:
                    edge = edge[0].lower()+edge[1:]
                    if edge in redirects:
                        edges[i] = redirects[edge]
        return None

    def remove_dead(self, title_to_id):
        for article_id, (edges, counts) in self.graph.items():
            active_edges = list()
            active_counts = list()

            while edges:
                edge = edges.pop()
                count = counts.pop()

                if edge:
                    edge = edge[0].lower()+edge[1:]
                    if edge in title_to_id:
                        active_edges.append(title_to_id[edge])
                        active_counts.append(count)
            self.graph[article_id] = (active_edges, active_counts)
        return None

