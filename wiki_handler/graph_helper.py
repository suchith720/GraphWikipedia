import re
import gc
import bz2
import subprocess
from .wiki_xml_handler import *


def create_graph(data_path, save_dir, matches=None, limit=None, save=True, tag_extractor=None, back=True):
    
    handler = WikiXmlHandler(matches=matches)
    
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    
    for i, line in enumerate(subprocess.Popen(['bzcat'],
                                             stdin = open(data_path),
                                             stdout = subprocess.PIPE).stdout):
        try:
            parser.feed(line)
        except StopIteration:
            break
            
        if limit is not None and len(handler.wikidataset.id_to_title) >= limit:
            if back:
                return handler.wikidataset
            else:
                break
    
    if save:
        file_tag = ''
        if isinstance(tag_extractor, re.Pattern):
            parts_tag = tag_extractor.match(os.path.basename(data_path))
            if parts_tag:
                try:
                    file_tag = f'-{parts_tag.group(1)}-{parts_tag.group(2)}-{parts_tag.group(3)}'
                except:
                    file_tag = ''
        elif isinstance(tag_extractor, str):
            file_tag = tag_extractor
            
        handler.wikidataset.save_data(save_dir, tag=file_tag)
        print(f"** Completed processing {os.path.basename(data_path)}.", end='\r')

    del handler
    del parser
    gc.collect()
    
    return None
