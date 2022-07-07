import os
import pickle
import numpy as np
from scipy.sparse import csr_matrix

class WikilinkGraph:

    def __init__(self):
        self.num_docs = 0
        self.doc_to_rowindex = {}

        """
        document link frequency
        """
        self.lf_indptr = [0]
        self.lf_indices = []
        self.lf = []

        """
        link document frequency
        """
        self.link_doc_cnt = {}

        self.wikilinks = {}

    def update_lf_df(self, page_title, links):
        if page_title in self.doc_to_rowindex:
            return

        self.doc_to_rowindex[page_title] = self.num_docs
        self.num_docs += 1

        """
        number of links of a particular type present in a document.
        """
        doc_link_cnt = {}
        for link in links:
            #please check this again, index here is strange.
            index = self.wikilinks.setdefault(link, len(self.wikilinks))
            doc_link_cnt[link] = doc_link_cnt.get(link, 0) + 1

        """
        document link frequecy matrix
        """
        for link, cnt in doc_link_cnt.items():
            self.lf_indices.append(self.wikilinks[link])
            self.lf.append(cnt)
            self.link_doc_cnt[link] = self.link_doc_cnt.get(link, 0) + 1
        self.lf_indptr.append(len(self.lf_indices))

    def get_doc_link_freq(self):
        """
        document link frequency
        """
        doc_lf = csr_matrix((self.lf, self.lf_indices, self.lf_indptr),
                            shape=(self.num_docs, len(self.wikilinks)),dtype=int)
        return doc_lf

    def get_link_doc_freq(self):
        """
        link document frequency
        """
        df_indptr = [0]
        df_indices = []
        df = []

        for link, cnt in self.link_doc_cnt.items():
            df_indices.append(self.wikilinks[link])
            df.append(cnt)
        df_indptr.append(len(df_indices))

        link_df = csr_matrix((df, df_indices, df_indptr),
                             shape=(1, len(self.wikilinks)),
                             dtype=int)
        return link_df

    def save_data(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)

        doc_lf = self.get_doc_link_freq()
        link_df = self.get_link_doc_freq()

        stat = (self.doc_to_rowindex, doc_lf, link_df,
                self.num_docs, self.wikilinks)

        with open(f'{save_dir}/link_graph{tag}.pickle', 'wb') as f:
            pickle.dump(stat, f)

    def load_data(self, save_dir, tag=''):
        filename = f'{save_dir}/link_graph{tag}.pickle'

        if os.path.exists(filename):

            with open(filename, 'rb') as f:
                stat = pickle.load(f)

            self.doc_to_rowindex, doc_lf, link_df, self.num_docs, self.wikilinks = stat

            self.lf = list(doc_lf.data)
            self.lf_indptr = list(doc_lf.indptr)
            self.lf_indices = list(doc_lf.indices)

            rev_wikilinks = {v:k for k, v in self.wikilinks.items()}
            self.link_doc_cnt = {rev_wikilinks[idx]:cnt for idx, cnt in zip(link_df.indices, link_df.data)}

            return True
        return False
