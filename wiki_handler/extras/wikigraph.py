from graph_utils import *

from timeit import default_timer as timer
from multiprocessing import Pool
from functools import partial
import tqdm


project = 'enwiki'
dump_date = "20220420"
dataset_home = '/home/cse/phd/anz198717/scratch/suchith_data/wikipedia/wikipedia-data-science/' 

matches = r'^([Ss]ee[ ]*|[Ss]ee[ ]*([Aa]lso|[Mm]ore|[Aa]ll)|[Ss]ee[ ]*[Aa]lso[ ]*\(.+\))$'
prog = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')

partitions = [f'{dataset_home}/datasets/{file}' for file in os.listdir(f'{dataset_home}/datasets')
                if prog.match(file)]

generate_graph = partial(create_graph, matches=matches, prefix=prog)


"""
run code parallel on partitions
"""
start = timer()
pool = Pool(processes = 24)
results = []

for x in tqdm.tqdm(pool.imap_unordered(generate_graph, partitions), total = len(partitions)):
    results.append(x)

pool.close()
pool.join()

end = timer()
print(f'{end - start} seconds elapsed.')
