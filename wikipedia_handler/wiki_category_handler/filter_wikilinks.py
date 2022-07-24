from .helper import *
import re
import mwparserfromhell


class FilterWikilinks:

    def __init__(self):
        """
        Removed category, cat from subject namespaces.
        """
        self.subject_namespaces = {'user', 'wikipedia', 'wp', 'project', 'file', 'image', 'mediawiki',
                                   'template', 't', 'help', 'h', 'portal', 'p',
                                   'draft', 'timedtext', 'module', 'special', 'media'}

        self.talk_namespaces = {'talk', 'user talk', 'wikipedia talk', 'wt', 'project talk', 'file talk',
                                'image talk','mediawiki talk', 'template talk', 'help talk', 'category talk',
                                'portal talk', 'draft talk', 'timedtext talk', 'module talk'}

        self.interwiki_links = {'wiktionary', 'wikt', 'wikinews', 'n', 'wikibooks', 'b', 'wikiquote','q',
                                'wikisource','s', 'oldwikisource', 'wikispecies', 'species',
                                'wikiversity', 'v', 'wikivoyage', 'voy', 'wikimedia','foundation', 'wmf',
                                'commons', 'c', 'metawiki', 'metawikimedia', 'metawikipedia', 'meta' , 'm',
                                'incubator', 'strategy', 'mediawikiwiki', 'mw', 'mediazilla', 'bugzilla'}

        self.language_code = re.compile(r'^[a-z][a-z]$')

    def remove_section_tags(self, link):
        hash_parts = link.split('#')
        if len(hash_parts) > 1:
            link = hash_parts[0].strip()
        return link

    def filter_special_tags(self, link):
        colon_parts = link.split(':')
        part_num = 0
        for part in colon_parts:
            part = part.lower()
            if (part == "w") or (part == "en") or (part_num == 0 and not part):
                part_num += 1
            elif (part in self.subject_namespaces) or (part in self.talk_namespaces) \
            or (part in self.interwiki_links) or self.language_code.match(part):
                return ''
            else:
                break
        return ':'.join(colon_parts[part_num:])

    def lower_wikilink(self, link):
        cat_link = is_category_link(link)
        if cat_link:
            return 'category:' + cat_link[0].lower() + cat_link[1:]
        elif link:
            link = link[0].lower() + link[1:]
        return link

    def remove_underscore(self, link):
        return link.replace('_', ' ')

    def fix_single_quotes(self, link):
        if '"' in link:
            link_split = link.split('"')
            for i in range(len(link_split)):
                if i == 0:
                    link_split[i] = link_split[i][:-1]
                elif i == len(link_split)-1:
                    link_split[i] = link_split[i][1:]
                else:
                    link_split[i] = link_split[i][1:-1]
            return '"'.join(link_split)
        return link

    def process_wikilink(self, link):
        link = self.remove_section_tags(link)
        link = self.filter_special_tags(link)
        link = self.lower_wikilink(link)
        link = self.remove_underscore(link)
        link = self.fix_single_quotes(link)
        return link

    def extract_wikilink_from_wikicode(self, wikicode):
        links = list( map(lambda link: (link.title).strip_code().strip(), wikicode.filter_wikilinks()) )
        return links

    """
    The main reason for this function is to seperate category and article links.
    'group_1' contains the category links
    'group_2' contains the article links.
    """
    def seggregate_links(self, links, seg_func):
        group_1, group_2 = list(), list()
        for link in links:
            processed_link = seg_func(link)
            if processed_link:
                group_1.append(processed_link)
            else:
                group_2.append(link)
        return group_1, group_2

