import os
import pickle
import numpy as np
from scipy.sparse import csr_matrix


def prune_map(mapping, idxs):
    rev_mapping = {value:key for key, value in mapping.items()}
    pruned_mapping = {}
    for i, idx in enumerate(idxs):
        pruned_mapping[rev_mapping[idx]] = i
    return pruned_mapping


def split_count(num_samples, perc=0.7):
    num_train = int( np.ceil(num_samples*perc) )
    if num_train == num_samples and num_samples > 1:
        num_train -= 1
    return num_train


class WikipediaSplit:

    def __init__(self, graph=None):
        self.graph = None
        self.labels = None
        self.doc_to_rowindex = None

        if graph:
            _ = self.to_matrix(graph)

        self.train, self.test = None, None
        self.trn_tst_labels = None
        self.train_doc_to_rowindex, self.test_doc_to_rowindex = None, None

    def to_matrix(self, graph):
        indptr = [0]
        indices = []
        data = []

        self.doc_to_rowindex = {}

        self.labels = {}
        for i, (doc, edge_count) in enumerate(graph.items()):
            self.doc_to_rowindex[doc] = i

            for link, cnt in edge_count.items():
                index = self.labels.setdefault(link, len(self.labels))
                indices.append(index)
                data.append(cnt)
            indptr.append(len(indices))

        self.graph = csr_matrix((data, indices, indptr), dtype=int)
        return self.graph, self.labels, self.doc_to_rowindex

    def clean_matrix(self, clean_type=0):
        if clean_type == 0:
            self.graph, self.labels, self.doc_to_rowindex = self.remove_single_labels(self.graph,
                                                                                      self.labels,
                                                                                      self.doc_to_rowindex)
        elif clean_type == 1:
            pruned_rows = self.get_pruned_row(self.graph)
            self.graph, self.doc_to_rowindex = self.prune_graph_rows(self.graph,
                                                                     self.doc_to_rowindex,
                                                                     pruned_rows)
        else:
            pruned_cols = self.get_pruned_cols(self.graph)
            self.graph, self.labels = self.prune_graph_cols(self.graph,
                                                           self.labels,
                                                           pruned_cols)

    """
    def get_split_idx(self):
        train_rowidx = []
        test_rowidx = []

        num_rows, num_cols = self.graph.shape
        row_available_flag = np.ones(num_rows, dtype=bool)

        label_cnt = np.array(self.graph.sum(axis=0)).reshape(-1)
        uni_label_cnt = np.unique(label_cnt)

        for lcnt in uni_label_cnt:
            if lcnt > upper_threshold:
                break

            label_pos = np.where(label_cnt == lcnt)[0]
            row_numlabels = np.array(self.graph[:, label_pos].sum(axis=1)).reshape(-1)

            row_idx = np.where(row_numlabels > 0)[0]
            row_available_flag[row_idx] = False
            num_train = split_count(row_idx.shape[0], perc=0.7)
            row_idx = list(np.random.permutation(row_idx))

            train_rowidx.extend(row_idx[:num_train])
            test_rowidx.extend(row_idx[num_train:])

        row_idx = np.where(row_available_flag == True)[0]
        num_train = split_count(row_idx.shape[0], perc=0.7)
        row_idx = list(np.random.permutation(row_idx))
        train_rowidx.extend(row_idx[:num_train])
        test_rowidx.extend(row_idx[num_train:])

        return train_rowidx, test_rowidx
        """

    def get_split_idx(self, upper_threshold=10, perc=0.7):
        train_rowidx = []
        test_rowidx = []

        row_idxs, col_idxs = self.graph.nonzero()
        sort_idx = np.argsort(col_idxs)
        row_idxs = row_idxs[sort_idx]
        col_idxs = col_idxs[sort_idx]

        num_rows = self.graph.shape[0]
        row_inserted_flag = np.zeros(num_rows, dtype=bool)

        label_cnt = np.array(self.graph.sum(axis=0)).reshape(-1)
        uni_label_cnt = np.unique(label_cnt)

        cnt = 0
        for lcnt in uni_label_cnt:
            if cnt == num_rows or lcnt >= upper_threshold:
                break

            pos_ptr, col_ptr = 0, 0
            pos_idxs = np.where(label_cnt == lcnt)[0]
            pos_idxs.sort()

            while col_ptr < len(col_idxs) and pos_ptr < len(pos_idxs) and cnt < num_rows:
                if pos_idxs[pos_ptr] != col_idxs[col_ptr]:
                    col_ptr += 1
                else:
                    sample_row_idxs = []
                    while col_ptr < len(col_idxs) and pos_ptr < len(pos_idxs) and cnt < num_rows and pos_idxs[pos_ptr] == col_idxs[col_ptr]:
                        rn = row_idxs[col_ptr]
                        if not row_inserted_flag[rn]:
                            sample_row_idxs.append(rn)
                            row_inserted_flag[rn] = True
                            cnt += 1
                        col_ptr += 1
                    pos_ptr += 1

                    num_train = split_count(len(sample_row_idxs), perc=0.7)
                    sample_row_idxs = list(np.random.permutation(sample_row_idxs))
                    train_rowidx.extend(sample_row_idxs[:num_train])
                    test_rowidx.extend(sample_row_idxs[num_train:])

        sample_row_idxs = np.where(row_inserted_flag == False)[0]
        num_train = split_count(num_rows, perc=0.7)
        num_train -= len(train_rowidx)

        sample_row_idxs = list(np.random.permutation(sample_row_idxs))
        train_rowidx.extend(sample_row_idxs[:num_train])
        test_rowidx.extend(sample_row_idxs[num_train:])

        return train_rowidx, test_rowidx

    def get_split_bylabel(self, upper_threshold=10, perc=0.7):
        """
        splitting data into train-test
        """
        train_idx, test_idx = self.get_split_idx(upper_threshold, perc)

        self.train = self.graph[train_idx, :]
        self.test = self.graph[test_idx, :]
        self.trn_tst_labels = self.labels

        rowindex_to_doc = {row_idx:doc for doc, row_idx in self.doc_to_rowindex.items()}

        self.train_doc_to_rowindex = {rowindex_to_doc[idx]:i for i, idx in enumerate(train_idx)}
        self.test_doc_to_rowindex = {rowindex_to_doc[idx]:i for i, idx in enumerate(test_idx)}

        """
        pruning the columns
        """
        trn_pruned_cols = self.get_pruned_cols(self.train)
        tst_pruned_cols = self.get_pruned_cols(self.test)
        pruned_cols = np.intersect1d(trn_pruned_cols, tst_pruned_cols)
        self.train = self.train[:, pruned_cols]
        self.test = self.test[:, pruned_cols]
        self.trn_tst_labels = prune_map(self.trn_tst_labels, pruned_cols)

        """
        prunning the rows
        """
        pruned_rows = self.get_pruned_row(self.train)
        self.train, self.train_doc_to_rowindex = self.prune_graph_rows(self.train,
                                                                       self.train_doc_to_rowindex, pruned_rows)
        pruned_rows = self.get_pruned_row(self.test)
        self.test, self.test_doc_to_rowindex = self.prune_graph_rows(self.test,
                                                                     self.test_doc_to_rowindex, pruned_rows)

    def get_random_split_idx(self, perc=0.7):
        n_docs = self.graph.shape[0]
        n_trn = int(perc * n_docs)
        rand_idx = np.random.permutation(n_docs)
        return rand_idx[:n_trn], rand_idx[n_trn:]

    def get_pruned_cols(self, graph, count=0):
        label_cnt = np.array(graph.sum(axis=0)).reshape(-1)
        pruned_cols = np.where(label_cnt > count)[0]
        return pruned_cols

    def get_pruned_row(self, graph, count=0):
        pruned_rows = np.where( np.array(graph.sum(axis=1)).reshape(-1) > count )[0]
        return pruned_rows

    def prune_graph_cols(self, graph, labels, pruned_cols):
        graph = graph[:, pruned_cols]
        labels = prune_map(labels, pruned_cols)
        return graph, labels

    def prune_graph_rows(self, graph, doc_to_rowindex, pruned_rows):
        graph = graph[pruned_rows, :]
        doc_to_rowindex = prune_map(doc_to_rowindex, pruned_rows)
        return graph, doc_to_rowindex

    def remove_single_labels(self, graph, labels, doc_to_rowindex):
        pruned_cols = self.get_pruned_cols(graph, count=1)
        graph, labels = self.prune_graph_cols(graph, labels, pruned_cols)

        pruned_rows = self.get_pruned_row(graph)
        graph, doc_to_rowindex = self.prune_graph_rows(graph, doc_to_rowindex, pruned_rows)

        return graph, labels, doc_to_rowindex

    def get_split_byrandom(self, perc=0.7):
        train_idx, test_idx = self.get_random_split_idx(perc)

        self.train = self.graph[train_idx, :]
        self.test = self.graph[test_idx, :]
        rowindex_to_doc = {row_idx:doc for doc, row_idx in self.doc_to_rowindex.items()}
        self.train_doc_to_rowindex = {rowindex_to_doc[idx]:i for i, idx in enumerate(train_idx)}
        self.test_doc_to_rowindex = {rowindex_to_doc[idx]:i for i, idx in enumerate(test_idx)}

        train_pruned_cols = self.get_pruned_cols(self.train)
        test_pruned_cols = self.get_pruned_cols(self.test)
        pruned_cols = np.intersect1d(train_pruned_cols, test_pruned_cols)

        self.train = self.train[:, pruned_cols]
        self.test = self.test[:, pruned_cols]
        self.trn_tst_labels = prune_map(self.labels, pruned_cols)

        pruned_rows = self.get_pruned_row(self.train)
        self.train, self.train_doc_to_rowindex = self.prune_graph_rows(self.train,
                                                                       self.train_doc_to_rowindex,
                                                                       pruned_rows)
        pruned_rows = self.get_pruned_row(self.test)
        self.test, self.test_doc_to_rowindex = self.prune_graph_rows(self.test,
                                                                     self.test_doc_to_rowindex,
                                                                     pruned_rows)

    def save_data(self, save_dir, tag='seealso'):
        train_file = f'{save_dir}/{tag}_train.pkl'
        with open(train_file, 'wb') as fout:
            train = (self.trn_tst_labels, self.train_doc_to_rowindex, self.train)
            pickle.dump(train, fout)

        test_file = f'{save_dir}/{tag}_test.pkl'
        with open(test_file, 'wb') as fout:
            test = (self.trn_tst_labels, self.test_doc_to_rowindex, self.test)
            pickle.dump(test, fout)

    def load_data(self, save_dir, tag='seealso'):
        train_file = f'{save_dir}/{tag}_train.pkl'
        with open(train_file, 'rb') as fout:
            train = pickle.load(fout)
            self.trn_tst_labels, self.train_doc_to_rowindex, self.train = train

        test_file = f'{save_dir}/{tag}_test.pkl'
        with open(test_file, 'rb') as fout:
            test = pickle.load(fout)
            _, self.test_doc_to_rowindex, self.test = test

