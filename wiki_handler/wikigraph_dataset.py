from .wikilink_graph import *
import mwparserfromhell

class WikiGraphDataset:

    def __init__(self, matches=None):
        self.matches = matches

        self.seealso_graph = WikilinkGraph()
        self.article_graph = WikilinkGraph()

        self.id_to_title = {}
        self.wiki_content = {}
        self.redirects = {}

    def extract_article_info(self, article_title, article_text):
        wikicode = mwparserfromhell.parse(article_text, skip_style_tags=True)
        wikicode.remove_nodetype(inplace=True)

        match_sections, rest_sections = wikicode.split_sections(matches=self.matches, include_lead=True, flat=True)

        match_wikilinks = self.extract_section_wikilinks(match_sections, article_title)
        rest_wikilinks = self.extract_section_wikilinks(rest_sections, article_title)

        article_content = wikicode.strip_code().strip()

        return match_wikilinks, rest_wikilinks, article_content

    def extract_section_wikilinks(self, sections, article_title):
        wikilinks = list()

        for section in sections:
            links = list( map(lambda link: (link.title).strip_code().strip(), section.filter_wikilinks()) )
            wikilinks.extend(links)

        return wikilinks

    def add_article(self, article_title, article_text, article_id, article_ns):
        article_title, article_id = article_title.strip(), int(article_id.strip())
        if article_title in self.article_graph.doc_to_rowindex or article_title in self.seealso_graph.doc_to_rowindex:
            return
        seealso_wikilinks, article_wikilinks, article_content = self.extract_article_info(article_title,
                                                                                          article_text)

        if len(seealso_wikilinks) or len(article_wikilinks):
            self.id_to_title[article_id] = article_title

            if len(seealso_wikilinks):
                self.seealso_graph.update_lf_df(article_title, seealso_wikilinks)

            if len(article_wikilinks):
                self.article_graph.update_lf_df(article_title, article_wikilinks)

            if article_content:
                self.wiki_content[article_id] = article_content

    def add_redirect(self, article_title, target_title):
        self.redirects[article_title] = target_title

    def save_graph(self, save_dir, tag=''):
        self.seealso_graph.save_data(save_dir, tag=f'_seealso{tag}')
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

    def save_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        with open(content_file, 'wb') as f:
            pickle.dump(self.wiki_content, f)

    def save_redirects(self, save_dir, tag=''):
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        with open(redirect_file, 'wb') as f:
            pickle.dump(self.redirects, f)

    def load_graph(self, save_dir, tag=''):
        if not self.seealso_graph.load_data(save_dir, tag=f'_seealso{tag}'):
            raise Exception("Unable to load 'seealso graph'.")

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
            raise Exception("Unable to load 'id_to_title'.")

    def load_wikicontent(self, save_dir, tag=''):
        content_file = f'{save_dir}/wiki_content{tag}.pickle'
        if os.path.exists(content_file):
            with open(content_file, 'rb') as f:
                self.wiki_content = pickle.load(f)
        else:
            raise Exception("Unable to load 'wiki_content'.")

    def load_redirects(self, save_dir, tag=''):
        redirect_file = f'{save_dir}/redirects{tag}.pickle'
        if os.path.exists(redirect_file):
            with open(redirect_file, 'rb') as f:
                self.redirects = pickle.load(f)
        else:
            raise Exception("Unable to load 'redirects'.")
