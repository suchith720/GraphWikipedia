import xml.sax

class AbstractXmlHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._article_count = 0

        self._abstract = {}

    def characters(self, content):
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        if name in ('title','abstract'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)
            self._current_tag = None

        elif name == 'doc':
            self._article_count += 1
            cat, title = self._values['title'].split(':', maxsplit=1)
            title = title.strip()
            title = title[0].lower() + title[1:]
            self._abstract[title.strip()] = self._values['abstract'].strip()

