from wiki_handler import *
import re
import tqdm
from functools import partial
from multiprocessing import Pool
from timeit import default_timer as timer


limit=None
project = 'enwiki'
dump_date = "20220420"
dataset_home = '/home/cse/phd/anz198717/scratch/suchith_data/wikipedia/wikipedia-data-science'


prog = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')
partitions = sorted([f'{dataset_home}/datasets/{file}' for file in os.listdir(f'{dataset_home}/datasets') 
                     if prog.match(file)])
print(f'** Total number of partitions of the wikipedia dump : {len(partitions)}')


save_dir = f'{dataset_home}/results'
tag_extractor = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')
matches = r'^([Ss]ee[ ]*|[Ss]ee[ ]*([Aa]lso|[Mm]ore|[Aa]ll)|[Ss]ee[ ]*[Aa]lso[ ]*\(.+\))$'


"""
Multiprocessing code.
"""
generate_graph = partial(create_graph, save_dir=save_dir, matches=matches, limit=limit, save=True, tag_extractor=tag_extractor, back=False)

start = timer()

pool = Pool(processes = 24)
results = []
for x in tqdm.tqdm(pool.imap_unordered(generate_graph, partitions), total = len(partitions)):
    results.append(x)
pool.close()
pool.join()

end = timer()

print(f'** Time taken to process the data : {(end - start)/3600:.3f} hours.')
