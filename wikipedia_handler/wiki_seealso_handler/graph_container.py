from .graph import *
from .filter_wikilinks import *
import mwparserfromhell


class WikiGraphDataset:

    def __init__(self, matches=None):
        self.matches = matches

        self.seealso_graph = WikilinkGraph()
        self.article_graph = WikilinkGraph()

        self.id_to_title = {}
        self.wiki_content = {}
        self.redirects = {}

        self.filter_links = FilterWikilinks()

    """
    Add articles to graph dataset.
    """
    def extract_article_info(self, article_text):
        wikicode = mwparserfromhell.parse(article_text, skip_style_tags=True)
        wikicode.remove_nodetype(inplace=True)

        match_sections, rest_sections = wikicode.split_sections(matches=self.matches, include_lead=True, flat=True)

        match_wikilinks = self.extract_section_wikilinks(match_sections)
        rest_wikilinks = self.extract_section_wikilinks(rest_sections)

        article_content = wikicode.strip_code().strip()

        return match_wikilinks, rest_wikilinks, article_content

    def extract_section_wikilinks(self, sections):
        wikilinks = list()

        for section in sections:
            links = list( map(lambda link: (link.title).strip_code().strip(), section.filter_wikilinks()) )
            for link in links:
                processed_link = self.filter_links.process_wikilink(link)
                if processed_link:
                    wikilinks.append(processed_link)

        return wikilinks

    def add_article(self, article_title, article_text, article_id, article_ns):

        article_title, article_id = article_title.strip(), int(article_id.strip())
        article_title = self.filter_links.process_wikilink(article_title)

        if not article_title or article_title in self.article_graph.graph or article_title in self.seealso_graph.graph:
            return
        seealso_wikilinks, article_wikilinks, article_content = self.extract_article_info(article_text)

        if len(seealso_wikilinks) or len(article_wikilinks):
            self.id_to_title[article_id] = article_title

            if len(seealso_wikilinks):
                self.seealso_graph.add_article(article_id, seealso_wikilinks)

            if len(article_wikilinks):
                self.article_graph.add_article(article_id, article_wikilinks)

            if article_content:
                self.wiki_content[article_id] = article_content

    """
    Add redirect
    """
    def add_redirect(self, article_title, target_title):
        article_title = self.filter_links.process_wikilink(article_title)
        target_title = self.filter_links.process_wikilink(target_title)

        if article_title and target_title:
            self.redirects[article_title] = target_title

    """
    Save content
    """
    def save_graph(self, save_dir, tag='', graph_type='both'):
        if graph_type == 'seealso' or graph_type == 'both':
            self.seealso_graph.save_data(save_dir, tag=f'_seealso{tag}')

        if graph_type == 'articles' or graph_type == 'both':
            self.article_graph.save_data(save_dir, tag=f'_articles{tag}')

    def save_data(self, save_dir, tag=''):
        os.makedirs(save_dir, exist_ok=True)

        self.save_graph(save_dir, tag)
        self.save_idtotitle(save_dir, tag)
        self.save_wikicontent(save_dir, tag)
        self.save_redirects(save_dir, tag)

    def save_idtotitle(self, save_dir, tag=''):
        map_file = f'{save_dir}/id_to_title{tag}.pickle'
        with open(map_file, 'wb') as f:
            pickle.dump(self.id_to_title, f)
        del self.id_to_title
        gc.collect()

    def save_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'wb') as f:
            pickle.dump(self.wiki_content, f)
        del self.wiki_content
        gc.collect()

    def save_redirects(self, save_dir, tag=''):
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        with open(redirect_file, 'wb') as f:
            pickle.dump(self.redirects, f)
        del self.redirects
        gc.collect()

    def load_graph(self, save_dir, tag='', graph_type='both'):
        if graph_type == 'seealso' or graph_type == 'both':
            if not self.seealso_graph.load_data(save_dir, tag=f'_seealso{tag}'):
                raise Exception("Unable to load 'seealso graph'.")

        if graph_type == 'articles' or graph_type == 'both':
            if not self.article_graph.load_data(save_dir, tag=f'_articles{tag}'):
                raise Exception("Unable to load 'article graph'.")

    def load_data(self, save_dir, tag=''):
        self.load_graph(save_dir, tag)
        self.load_idtotitle(save_dir, tag)
        self.load_wikicontent(save_dir, tag)
        self.load_redirects(save_dir, tag)

    def load_idtotitle(self, save_dir, tag=''):
        map_file = f'{save_dir}/id_to_title{tag}.pickle'
        if os.path.exists(map_file):
            with open(map_file, 'rb') as f:
                self.id_to_title = pickle.load(f)
        else:
            raise Exception(f"Unable to load 'id_to_title' from {map_file}.")

    def load_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        if os.path.exists(content_file):
            with open(content_file, 'rb') as f:
                self.wiki_content = pickle.load(f)
        else:
            raise Exception(f"Unable to load 'wiki_content' from {content_file}.")

    def load_redirects(self, save_dir, tag=''):
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        if os.path.exists(redirect_file):
            with open(redirect_file, 'rb') as f:
                self.redirects = pickle.load(f)
        else:
            raise Exception(f"Unable to load 'redirects' from {redirect_file}.")

