project = 'enwiki'
dump_date = "20220420"

#root directory of the repository
dataset_home = '/home/scai/phd/aiz218323/scratch/XML/wikipedia-data-science_2'

#saving the dumps using the download scripts
dump_dirname = 'raw_data'

#this is where datasets GraphWikiSeealso and GraphWikiCategory will be stored.
dataset_dir = f'{dataset_home}/datasets/'

#to the combined abstract information
abstract_dir = f'{dataset_dir}/Abstract/'

#to save the GraphWikiSeeAlso information
limit = None
category_dir = f'{dataset_dir}/WikiSeeAlso'
results_dir = f'{category_dir}/results'
combine_dir = f'{category_dir}/combined'
xc_dir = f'{category_dir}/XCData'
