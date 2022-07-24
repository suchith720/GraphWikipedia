from .combine_graph import *
from .data_splitter import *
from ..abstract_handler import *


class XCDataset:

    def __init__(self):
        self.id_to_title = {}
        self.abstract = None

        self.data_splitter = {}

    def load_idtotitle(self, save_dir, tag='', verbose=True):
        """
        Loading id_to_title
        """
        if verbose:
            print("Loading Article and Category 'id_to_title'.")
        graph_data = WikiGraphCombine()
        graph_data.load_idtotitle(save_dir, tag=tag)

        self.id_to_title['article'] = graph_data.parameters['id_to_title']
        self.id_to_title['label'] = graph_data.parameters['label_id_to_title']

    def load_abstract(self, save_dir, tag='', verbose=True):
        """
        Loading abstract
        """
        if verbose:
            print("Loading Article 'abstracts'.")
        abstract = WikiAbstract()
        abstract.load_abstract(save_dir, tag=tag)
        self.abstract = abstract.abstract

    def save_sparse_file(self, matrix, save_file):
        matrix.sort_indices()
        rows, cols = matrix.nonzero()
        data = matrix.data

        with open(save_file, 'w') as fout:
            fout.write(f'{matrix.shape[0]} {matrix.shape[1]}\n')

            row_ctr = -1
            line = ''
            for r, c, d in zip(rows, cols, data):
                if row_ctr == r:
                    line = line+f' {c}:{d}'
                elif row_ctr+1 == r:
                    if line:
                        fout.write(f'{line}\n')
                    line = f'{c}:{d}'
                    row_ctr += 1
                else:
                    raise Exception("Row is missing.")
            if line:
                fout.write(f'{line}\n')

    def save_XY_text(self, save_dir, doc_to_rowindex, tag='', id_type='article'):
        os.makedirs(save_dir, exist_ok=True)

        if id_type == 'article':
            idtocontent_file = f'{save_dir}/{tag}_id_to_text.txt'
            self.save_XY_content(idtocontent_file, self.id_to_title[id_type], doc_to_rowindex, self.abstract)

        idtotitle_file = f'{save_dir}/{tag}_id_to_title.txt'
        self.save_XY_title(idtotitle_file, self.id_to_title[id_type], doc_to_rowindex)

    def save_XY_content(self, idtocontent_file, id_to_title, doc_to_rowindex, content):
        with open(idtocontent_file, 'w') as fout:
            for doc_id in sorted(doc_to_rowindex, key=lambda x : doc_to_rowindex[x]):
                if id_to_title[doc_id] in content:
                    fout.write(f'{doc_id}->{content[id_to_title[doc_id]]}\n')
                else:
                    fout.write(f'{doc_id}->\n')

    def save_XY_title(self, idtotitle_file, id_to_title, doc_to_rowindex):
        with open(idtotitle_file, 'w') as fout:
            for doc_id in sorted(doc_to_rowindex, key=lambda x : doc_to_rowindex[x]):
                fout.write(f'{doc_id}->{id_to_title[doc_id]}\n')

    def load_classification_data(self, save_dir, verbose=True):
        """
        Loading Classification train-test split
        """
        if verbose:
            print("Loading Classification train-test split.")
        self.data_splitter['classification'] = WikipediaSplit()
        self.data_splitter['classification'].load_data(save_dir, tag='wiki_category')

    def save_XCClassification_text(self, xc_dir, verbose=True):
        """
        Saving Classification XY - title and content(text)
        """
        if verbose:
            print("Saving Classification train X-article text")
        self.save_XY_text(xc_dir, self.data_splitter['classification'].train_doc_to_rowindex,
                                    tag='classification_train_X', id_type='article')
        if verbose:
            print("Saving Classification test X-article text")
        self.save_XY_text(xc_dir, self.data_splitter['classification'].test_doc_to_rowindex,
                                    tag='classification_test_X', id_type='article')
        if verbose:
            print("Saving Classification Y-label text")
        self.save_XY_text(xc_dir, self.data_splitter['classification'].trn_tst_labels,
                                    tag='classification_Y', id_type='label')

    def save_XCClassification_data(self, xc_dir, verbose=True):
        if verbose:
            print("Saving Classification train 'trn_X_Y.txt'.")
        train_file = f'{xc_dir}/trn_X_Y.txt'
        self.save_sparse_file(self.data_splitter['classification'].train, train_file)

        if verbose:
            print("Saving Classification test 'tst_X_Y.txt'.")
        test_file = f'{xc_dir}/tst_X_Y.txt'
        self.save_sparse_file(self.data_splitter['classification'].test, test_file)

    def save_XCClassification(self, save_dir, xc_dir, verbose=True):
        """
        XC Classification
        """
        self.load_classification_data(save_dir, verbose=verbose)
        self.save_XCClassification_text(xc_dir, verbose=verbose)
        self.save_XCClassification_data(xc_dir, verbose=verbose)

    def load_graph_data(self, save_dir, tag='', graph_type='article', verbose=True):
        """
        Loading Graph
        """
        if verbose:
            print(f"Loading {graph_type} graph.")
        graph_data = WikiGraphCombine()
        graph_data.load_graph(save_dir, tag=tag, graph_type=graph_type)

        self.data_splitter[graph_type] = WikipediaSplit(graph_data.parameters[f'{graph_type}_graph'])
        self.data_splitter[graph_type].clean_matrix(clean_type=1)

    def save_XCGraph_text(self, xc_dir, graph_type='article', verbose=True):
        """
        Saving XC-Graph text
        """
        if verbose:
            print(f"Saving {graph_type}_graph X-text.")
        self.save_XY_text(xc_dir, self.data_splitter[graph_type].doc_to_rowindex,
                          tag=f'{graph_type}_graph_X', id_type=graph_type)

        if verbose:
            print(f"Saving {graph_type}_graph Y-text.")
        self.save_XY_text(xc_dir, self.data_splitter[graph_type].labels,
                          tag=f'{graph_type}_graph_Y', id_type=graph_type)

    def save_XCGraph_data(self, xc_dir, graph_type='article', verbose=True):
        if verbose:
            print(f"Saving '{graph_type}_graph_trn_X_Y.txt'")
        graph_file = f'{xc_dir}/{graph_type}_graph_trn_X_Y.txt'
        self.save_sparse_file(self.data_splitter[graph_type].graph, graph_file)

    def save_XCGraph(self, save_dir, xc_dir, tag='', graph_type='article', verbose=True):
        """
        XC Graph
        """
        self.load_graph_data(save_dir, tag=tag, graph_type=graph_type, verbose=verbose)
        self.save_XCGraph_text(xc_dir, graph_type=graph_type, verbose=verbose)
        self.save_XCGraph_data(xc_dir, graph_type=graph_type, verbose=verbose)


    def create_XCData(self, save_dir, xc_dir, tag='', verbose=True):
        self.load_idtotitle(save_dir, tag=tag, verbose=verbose)
        self.load_abstract(save_dir, tag=tag, verbose=verbose)

        self.save_XCClassification(save_dir, xc_dir, verbose=verbose)
        self.save_XCGraph(save_dir, xc_dir, tag=tag, graph_type='article', verbose=verbose)
        self.save_XCGraph(save_dir, xc_dir, tag=tag, graph_type='label', verbose=verbose)

