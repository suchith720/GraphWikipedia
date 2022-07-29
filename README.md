# GraphWikipedia Dataset.
This is a code base for creating GraphWikiCategory and GraphWikiSeeAlso dataset which was created from the wikipedia dumps, these datasets were primarily created for using Extreme classification with graphs. 

Run all you code from the root directory of the repository, the steps to download the dataset are as follows:
1. Provide the following variables in the configurate file present at `config/download_config.py`
```
project = 'enwiki'
dump_date = "20220420"

#root directory of the repository
dataset_home = '/home/scai/phd/aiz218323/scratch/XML/wikipedia-data-science_2'
```
2. Run the download script with any of the following option:
* To get the dates of the wikipedia dumps
`python download.py --dates`
* To download the wikipedia xml dumps
`python download.py --dumps`
* To download the abstract dumps
`python download.py --abstract`

For creating datasets from the dumps, we will need to process the wikitext present in the XML dumps for which we will be using the `mwparserfromhell_2` library, which I have modified to accomodate few of our requirements. So add the path to this folder provided in the repository to `$PYTHONPATH` as follows :<br>
`PYTHONPATH='/path/to/GraphWikipedia/mwparserfromhell_2/src/:$PYTHONPATH`

## GraphWikiSeeAlso
This is article-to-article recommendation datasets, the classification task is given an article we need to predict the articles present in its `Seealso` section. Click [here](https://drive.google.com/file/d/1QcL_jqSkR393krMBpjpOQP1hD0DMAUSM/view?usp=sharing) to download the dataset.

To create the dataset do the following:
1. Provide the following variables in the configurate file present at `config/seealso_config.py`
```
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
```

2. Run the following commands:
```
$ python src/generate_seealso_graph.py
$ python src/process_abstract_dumps.py
$ python src/create_graph-wiki-seealso.py
```

### Dataset statistics

properties | no. of labels | no. of train | no. of test | points per label | labels per point
--- | --- | --- | --- | --- | ---
GraphWikiSeeAlso | 333,411 | 668,400 | 293,023 | 4.215 | 2.10220

### Graph statistics

properties | values
--- | ---
Number of nodes | 6,162,086
Number of edges | 165,199,765
Average in-degree | 30.194
Average out-degree | 26.809

### Baselines
Here are some of the Extreme classification baselines:

Algorithm | P1 | P3 | P5 | N1 | N3 | N5 | PSP1 | PSP3 | PSP5 | PSN1 | PSN3 | PSN5 | MODELSIZE | TRNTIME | PREDTIME
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Parabel | 23.18 | 13.53 | 9.66 | 23.18 | 23.63 | 24.48 | 12.51 | 14.51 | 15.91 | 12.51 | 14.27 | 15.24 | 0.64 | 0.08 | 1.31
Bonsai | 24.14 | 14.28 | 10.27 | 24.14 | 24.75 | 25.72 | 13.65 | 16.15 | 17.84 | 13.65 | 15.79 | 16.94 | 385.57 | 1466.05 | 22.47
PfastreXML | 19.45 | 12.05 | 8.79 | 19.45 | 20.73 | 21.76 | 13.86 | 15.41 | 16.66 | 13.86 | 15.33 | 16.25 | 7.11 | 0.96 | 6.67
AnneXML | 0.03 | 0.02 | 0.02 | 0.03 | 0.04 | 0.04 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 4449.60 | 1262.65 | 0.30
XT | 22.14 | 13.19 | 9.55 | 22.14 | 22.88 | 23.89 | 12.01 | 14.28 | 15.95 | 12.01 | 13.95 | 15.09 | 2.1 | 12430.00 | 15.68


## GraphWikiCategory
The classification task here is to tag a wikipedia article with the categories it belongs to. Wikipedia have special pages called category pages, when a wikilink to these pages is present in an article, the article is considered to belong to that particular category. Click [here](https://drive.google.com/file/d/1f1bTz3Gk9ikmCOEIPdVD7-qekPoC6Vkh/view?usp=sharing) to download the dataset.

Here are the steps to create this dataset :
1. Provide the following variables in the configurate file present at `config/category_config.py` 
```
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

#to save the GraphWikiCategory information
limit = None
category_dir = f'{dataset_dir}/WikiCategory'
results_dir = f'{category_dir}/results'
combine_dir = f'{category_dir}/combined'
xc_dir = f'{category_dir}/XCData'
```

2. Run the following commands:
```
$ python src/generate_category_graph.py
$ python src/process_abstract_dumps.py
$ python src/create_graph-wiki-category.py
```

### Dataset statistics

properties | no. of labels | no. of train | no. of test | points per label | labels per point
--- | --- | --- | --- | --- | ---
GraphWikiCategory | 1,080,148 | 4,245,310 | 1,830,068 | 26.387 | 4.698


### Graph statistics

#### Article graph

properties | values
--- | ---
Number of nodes | 6,471,181
Number of edges | 206,162,248
Average in-degree | 34.745
Average out-degree | 31.858

#### Category graph

properties | values
--- | ---
Number of nodes | 1,627,757
Number of edges | 4,097,826
Average in-degree | 5.5262
Average out-degree | 2.5174

### Baselines

Algorithm | P1 | P3 | P5 | N1 | N3 | N5 | PSP1 | PSP3 | PSP5 | PSN1 | PSN3 | PSN5 | MODELSIZE | TRNTIME | PREDTIME
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Parabel | 42.70 | 23.57 | 16.59 | 42.70 | 32.82 | 31.05 | 16.07 | 15.66 | 15.68 | 16.07 | 17.32 | 18.57 | 5.85 | 1.10 | 1.21
Bonsai | 43.08 | 23.67 | 16.63 | 43.08 | 33.04 | 31.27 | 17.05 | 16.56 | 16.57 | 17.05 | 18.29 | 19.60 | 3492.86 | 29153.10 | 29.26
PfastreXML | 36.24 | 19.62 | 13.90 | 36.24 | 27.83 | 26.54 | 18.52 | 15.22 | 14.80 | 18.52 | 17.66 | 18.59 | 48.73 | 10.16 | 12.22
AnneXML | 42.19 | 22.54 | 15.83 | 42.19 | 31.86 | 30.12 | 15.28 | 14.25 | 14.41 | 15.28 | 16.16 | 17.44 | 27467.19 | 27704.24 | 0.12
XT | 40.17 | 22.14 | 15.76 | 40.17 | 30.71 | 29.17 | 14.20 | 14.01 | 14.27 | 14.20 | 15.44 | 16.76 | 6.5 | 57169.00 | 8.77
