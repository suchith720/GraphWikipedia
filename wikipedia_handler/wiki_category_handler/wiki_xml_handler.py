from .helper import *
from .graph_container import *
import xml.sax


class WikiXmlHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)

        """
        PARSING VARIABLES: these variables will be useful
        while parsing the wikipedia dumps.
        """
        #basic storage for on-the-fly processing
        self._buffer = None
        self._values = {}
        self._current_tag = None

        #flags for handling special cases.
        self._add_page = True
        self._is_pageid = True

        """
        STORAGE VARIABLES: these variable will be used for
        storing the graph and content of the wikipedia dump.
        """
        self.wikidataset = WikiGraphDataset()

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
            article_title = self._values['article_title'].strip()
            target_title = attrs.getValue('title').strip()
            article_ns = int(self._values['article_ns'])
            if article_ns == 0 or article_ns == 14 :
                self.wikidataset.add_redirect(article_title, target_title, article_ns)
            self._add_page = False

    def endElement(self, name):
        if name == self._current_tag:
            self._values[f'article_{name}'] = ' '.join(self._buffer)
            self._current_tag = None

        elif name == 'page':
            article_ns = int(self._values['article_ns'])
            if article_ns != 0 and article_ns != 14:
                self._add_page = False

            """
            EXTRACT_DATA : The following code stores the data
            """
            if self._add_page:
                self.wikidataset.add_article(**self._values)
            """
            EXTRACT_DATA
            """

            self._add_page = True
            self._is_pageid = True
