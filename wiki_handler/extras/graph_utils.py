import os
import bz2
import xml.sax
import subprocess
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt

import gc
import re
import json

import mwparserfromhell


wiki_prefix = {'user', 'file', 'mediawiki', 'template', 'help', 'category', 
                  'portal', 'draft', 'timedtext', 'module', 'special', 'media', 
                  'cat', 'h', 'mos', 'p', 't', 'project', 'image', 'wikipedia',
               'wp', 'ru', 'wikt', 's', 'fr', 'el', 'es', 'c', 'commons'
              }

def filter_wikilink(link, page_title):
    link = (link.title).strip_code()
    if not link:
        return None

    """
    link starting with :
    """
    if link[0] == ':':
        link = link[1:]

    """
    filter links based on prefixes
    """ 
    link_sections = link.split(':', 1)
    while len(link_sections) > 1 and link_sections[0] in ["w", "en"]:
        link_sections = link_sections[1].split(':', 1)
    link = link_sections[0] if len(link_sections) == 1 else ':'.join(link_sections)

    if ':' in link:
        prefix, suffix = link.split(':', 1)
        if prefix.lower().strip() in wiki_prefix:
            return None

    """
    removing section link
    """
    if '#' in link:
        link, _ = link.split('#', 1)
        link = link.strip()
        if not link:
            link = page_title

    """
    '_' is equivalent to ' ' in the link.
    first letter of link is case insensitive
    """
    link = link.replace('_', ' ')
    
    if not link:
        return None
    
    return link[0].lower() + link[1:]


def get_filtered_wikilinks(sections, page_title):
    wikilinks = list()
    
    for section in sections:
        for link in section.filter_wikilinks():
            f_link = filter_wikilink(link, page_title)
            if f_link:
                wikilinks.append(f_link)
            
    return wikilinks


def process_article(page_title, page_text, page_id, page_ns, matches):

    wikicode = mwparserfromhell.parse(page_text, skip_style_tags=True)
    wikicode.remove_nodetype(inplace=True)

    match_sections, all_sections = wikicode.split_sections(matches=matches, include_lead=True)

    match_sec_wikilinks = get_filtered_wikilinks(match_sections, page_title)
    all_sec_wikilinks = get_filtered_wikilinks(all_sections, page_title)

    text_content = wikicode.strip_code().strip()

    return (page_title.strip(), match_sec_wikilinks, all_sec_wikilinks, text_content, int(page_id.strip()))



class WikiXmlHandler(xml.sax.handler.ContentHandler):

    def __init__(self, matches=None):
        xml.sax.handler.ContentHandler.__init__(self)
        self.matches = matches
        """
        basic storage for on-the-fly processing
        """
        self._buffer = None
        self._values = {}
        self._current_tag = None
        """
        flags for handling special cases.
        """
        self._add_page = True
        self._is_pageid = True
        """
        dump statistics
        """
        self._total_edges = 0
        self._article_count = 0
        """
        output information
        """
        self.graph = {}
        self.seealso = {}
        self.redirects = {}
        self.id_to_title = {}
        self.page_content = {}

    def characters(self, content):
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        if name in ('title', 'text', 'ns'):
            self._current_tag = name
            self._buffer = []
        elif name == 'id' and self._is_pageid:
            self._is_pageid = False
            self._current_tag = name
            self._buffer = []
        elif name == 'redirect':
            self.redirects[self._values['page_title'].strip()] = attrs.getValue('title').strip()
            self._add_page = False

    def endElement(self, name):
        if name == self._current_tag:
            self._values[f'page_{name}'] = ' '.join(self._buffer)
            self._current_tag = None
        elif name == 'page':
            if int(self._values['page_ns']):
                self._add_page = False

            if self._add_page:
                self._article_count += 1
                """
                text processing
                """
                proc_output = process_article(**self._values, matches=self.matches)
                self.graph_processing(*proc_output)

            self._add_page = True
            self._is_pageid = True

    def graph_processing(self, title, seealso_wikilinks, page_wikilinks, text_content, page_id):
        if len(seealso_wikilinks) or len(page_wikilinks):
            self.id_to_title[page_id] = title
            if len(seealso_wikilinks):
                links, count = np.unique(seealso_wikilinks, return_counts=True)
                self.seealso[page_id] = (links.tolist(), count.tolist())
            if len(page_wikilinks):
                self._total_edges += len(page_wikilinks)
                links, count = np.unique(page_wikilinks, return_counts=True)
                self.graph[page_id] = (links.tolist(), count.tolist())
            if text_content:
                self.page_content[page_id] = text_content



def save_graph(save_prefix, graph, seealso, redirects, id_to_title, page_content):

    with open(f'{save_prefix}_graph.ndjson', 'w') as fout:
        fout.write(json.dumps(graph))

    with open(f'{save_prefix}_seealso.ndjson', 'w') as fout:
        fout.write(json.dumps(seealso))

    with open(f'{save_prefix}_redirects.ndjson', 'w') as fout:
        fout.write(json.dumps(redirects))

    with open(f'{save_prefix}_id-to-title.ndjson', 'w') as fout:
        fout.write(json.dumps(id_to_title))

    with open(f'{save_prefix}_page-content.ndjson', 'w') as fout:
        fout.write(json.dumps(page_content))



def create_graph(data_path, matches=None, limit=None, save=True, prefix=None):

    handler = WikiXmlHandler(matches)

    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    for i, line in enumerate(subprocess.Popen(['bzcat'],
                                             stdin = open(data_path),
                                             stdout = subprocess.PIPE).stdout):
        try:
            parser.feed(line)
        except StopIteration:
            break

        if limit is not None and len(handler.seealso) >= limit:
            return handler.graph, handler.seealso, handler.redirects, handler.id_to_title, handler.page_content

    if save:
       	partition_dir = '/home/cse/phd/anz198717/scratch/suchith_data/wikipedia/wikipedia-data-science/partition_2/'
        os.makedirs(partition_dir, exist_ok=True)
        p_str = prefix.match(os.path.basename(data_path))
        save_prefix = f'{partition_dir}/{p_str.group(1)}-{p_str.group(2)}-{p_str.group(3)}'

        save_graph(save_prefix, handler.graph, handler.seealso, handler.redirects,
                   handler.id_to_title, handler.page_content)

        print(f"{len(os.listdir(partition_dir))} file processed.", end='\r')

    del handler
    del parser
    gc.collect()

    return None
