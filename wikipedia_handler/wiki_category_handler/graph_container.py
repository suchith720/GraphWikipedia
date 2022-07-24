from .graph import *
from .filter_wikilinks import *


class WikiGraphDataset:

    def __init__(self):
        self.article_graph = WikilinkGraph()
        self.label_graph = WikilinkGraph()
        self.classification_graph = WikilinkGraph()

        self.id_to_title = {}
        self.label_id_to_title = {}

        self.wiki_content = {}

        self.redirects = {}
        self.label_redirects = {}

        self.filter_links = FilterWikilinks()

    """
    Add articles to graph dataset.
    """
    def extract_article_info(self, article_text):
        wikicode = mwparserfromhell.parse(article_text, skip_style_tags=True)
        wikicode.remove_nodetype(inplace=True)

        """
        extract link
        """
        links = self.filter_links.extract_wikilink_from_wikicode(wikicode)

        wikilinks = list()
        for link in links:
            processed_link = self.filter_links.process_wikilink(link)
            if processed_link:
                wikilinks.append(processed_link)

        category_links, article_links = self.filter_links.seggregate_links(wikilinks, is_category_link)

        """
        extract content
        """
        article_content = wikicode.strip_code().strip()

        return category_links, article_links, article_content

    def add_article(self, article_title, article_text, article_id, article_ns):
        article_title, article_id, article_ns = article_title.strip(), int(article_id.strip()), int(article_ns.strip())

        article_title = self.filter_links.process_wikilink(article_title)
        cat_title = is_category_link(article_title)
        if cat_title:
            article_title = cat_title

        if not article_title or article_id in self.id_to_title or article_id in self.label_id_to_title:
            return

        category_links, article_links, article_content = self.extract_article_info(article_text)

        if len(category_links) or len(article_links):
            if article_ns == 0:
                self.id_to_title[article_id] = article_title
                if len(category_links):
                    self.classification_graph.add_article(article_id, category_links)
                if len(article_links):
                    self.article_graph.add_article(article_id, article_links)
                if article_content:
                    self.wiki_content[article_id] = article_content
            elif article_ns == 14:
                self.label_id_to_title[article_id] = article_title
                if len(category_links):
                    self.label_graph.add_article(article_id, category_links)

    """
    Add redirect
    """
    def add_redirect(self, article_title, target_title, article_ns):
        article_title = self.filter_links.process_wikilink(article_title)
        target_title = self.filter_links.process_wikilink(target_title)

        if article_title and target_title:
            if article_ns == 14:
                target_title = is_category_link(target_title)
                article_title = is_category_link(article_title)
                if target_title and article_title:
                    self.label_redirects[article_title] = target_title
            else:
                self.redirects[article_title] = target_title

    """
    Save content
    """
    def save_graph(self, save_dir, tag='', graph_type='all'):
        if graph_type == 'classification' or graph_type == 'all':
            self.classification_graph.save_data(save_dir, tag=f'_classification{tag}')

        if graph_type == 'article' or graph_type == 'all':
            self.article_graph.save_data(save_dir, tag=f'_article{tag}')

        if graph_type == 'label' or graph_type == 'all':
            self.label_graph.save_data(save_dir, tag=f'_label{tag}')

    def save_idtotitle(self, save_dir, tag='', id_type='all'):
        if id_type == "article" or id_type == "all":
            map_file = f'{save_dir}/id_to_title{tag}.pickle'
            with open(map_file, 'wb') as f:
                pickle.dump(self.id_to_title, f)
            del self.id_to_title

        if id_type == "label" or id_type == "all":
            map_file = f'{save_dir}/label_id_to_title{tag}.pickle'
            with open(map_file, 'wb') as f:
                pickle.dump(self.label_id_to_title, f)
            del self.label_id_to_title
        gc.collect()

    def save_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'wb') as f:
            pickle.dump(self.wiki_content, f)
        del self.wiki_content
        gc.collect()

    def save_redirects(self, save_dir, tag='', redirect_type='all'):
        if redirect_type == "article" or redirect_type == "all":
            redirect_file = f'{save_dir}/redirects{tag}.pickle'
            with open(redirect_file, 'wb') as f:
                pickle.dump(self.redirects, f)
            del self.redirects

        if redirect_type == "label" or redirect_type == "all":
            redirect_file = f'{save_dir}/label_redirects{tag}.pickle'
            with open(redirect_file, 'wb') as f:
                pickle.dump(self.label_redirects, f)
            del self.label_redirects
        gc.collect()

    def save_data(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)

        self.save_graph(save_dir, tag)
        self.save_idtotitle(save_dir, tag)
        self.save_redirects(save_dir, tag)
        self.save_wikicontent(save_dir, tag)

    def load_graph(self, save_dir, tag='', graph_type='all'):
        if graph_type == 'classification' or graph_type == 'all':
            if not self.classification_graph.load_data(save_dir, tag=f'_classification{tag}'):
                raise Exception("Unable to load 'classification graph'.")

        if graph_type == 'article' or graph_type == 'all':
            if not self.article_graph.load_data(save_dir, tag=f'_article{tag}'):
                raise Exception("Unable to load 'article graph'.")

        if graph_type == 'label' or graph_type == 'all':
            if not self.label_graph.load_data(save_dir, tag=f'_label{tag}'):
                raise Exception("Unable to load 'label graph'.")

    def load_idtotitle(self, save_dir, tag='', id_type='all'):
        if id_type == "article" or id_type == "all":
            map_file = f'{save_dir}/id_to_title{tag}.pickle'
            if os.path.exists(map_file):
                with open(map_file, 'rb') as f:
                    self.id_to_title = pickle.load(f)
            else:
                raise Exception(f"Unable to load 'id_to_title' from '{map_file}'.")

        if id_type == "label" or id_type == "all":
            map_file = f'{save_dir}/label_id_to_title{tag}.pickle'
            if os.path.exists(map_file):
                with open(map_file, 'rb') as f:
                    self.label_id_to_title = pickle.load(f)
            else:
                raise Exception(f"Unable to load 'label_id_to_title' from '{map_file}'.")

    def load_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        if os.path.exists(content_file):
            with open(content_file, 'rb') as f:
                self.wiki_content = pickle.load(f)
        else:
            raise Exception(f"Unable to load 'wiki_content' from '{content_file}'.")

    def load_redirects(self, save_dir, tag='', redirect_type='all'):
        if redirect_type == "article" or redirect_type == "all":
            redirect_file = f'{save_dir}/redirects{tag}.pickle'
            if os.path.exists(redirect_file):
                with open(redirect_file, 'rb') as f:
                    self.redirects = pickle.load(f)
            else:
                raise Exception(f"Unable to load 'redirects' from '{redirect_file}'.")

        if redirect_type == "label" or redirect_type == "all":
            redirect_file = f'{save_dir}/label_redirects{tag}.pickle'
            if os.path.exists(redirect_file):
                with open(redirect_file, 'rb') as f:
                    self.label_redirects = pickle.load(f)
            else:
                raise Exception(f"Unable to load 'label redirects' from '{redirect_file}'.")

    def load_data(self, save_dir, tag=''):
        self.load_graph(save_dir, tag)
        self.load_idtotitle(save_dir, tag)
        self.load_wikicontent(save_dir, tag)
        self.load_redirects(save_dir, tag)

