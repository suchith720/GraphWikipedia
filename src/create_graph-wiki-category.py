import os
import sys


"""
Adding paths to the configuration files and amazon graph packages.
"""
config_path = os.path.join(os.getcwd(), 'config')
package_path = os.path.join(os.getcwd(), 'wikipedia_handler')
sys.path.append(config_path)
sys.path.append(package_path)


from category_config import *
from wiki_category_handler import *


if __name__ == '__main__':
    """
    Check if the variable are properly defined in the config file.
    """
    paths = ['project', 'dump_date', 'dataset_home', 'dump_dirname', 'results_dir', 'combine_dir', 'xc_dir']
    for path in paths:
        if path not in vars():
            raise Exception(f'Variable {path} not defined in the config file.')


    """
    Collect all the raw dump paths using the regex expression.
    """
    dump_dir = f'{dataset_home}/{dump_dirname}'
    tag_extractor = re.compile(f'({project}-{dump_date})-'+r'pages-articles-multistream([0-9]{1,2}).xml-(p[0-9]+p[0-9]+).bz2')
    dump_paths = sorted([f'{dump_dir}/{file}' for file in os.listdir(f'{dump_dir}')
                         if tag_extractor.match(file)])
    print(f'-- Total number of partitions of the wikipedia dump : {len(dump_paths)}\n')


    """
    Combining redirects, id_to_title, wiki_content
    """
    combine_graph = WikiGraphCombine(dump_paths)
    combine_graph.combine_param(results_dir, param='id_to_title', tag_extractor=tag_extractor)
    combine_graph.combine_param(results_dir, param='label_id_to_title', tag_extractor=tag_extractor)
    combine_graph.combine_param(results_dir, param='redirects', tag_extractor=tag_extractor)
    combine_graph.combine_param(results_dir, param='label_redirects', tag_extractor=tag_extractor)

    combine_graph.save_idtotitle(combine_dir, tag=f'-{project}-{dump_date}')
    combine_graph.save_redirects(combine_dir, tag=f'-{project}-{dump_date}')


    """
    Resolving redirects in the graph
    """
    resolve_graph = ResolveGraph(dump_paths)

    resolve_graph.change_maps(combine_graph.parameters['id_to_title'], combine_graph.parameters['redirects'])
    resolve_graph.resolve(results_dir, graph_type='article', tag_extractor=tag_extractor)

    resolve_graph.change_maps(combine_graph.parameters['label_id_to_title'],
                                                        combine_graph.parameters['label_redirects'])
    resolve_graph.resolve(results_dir, graph_type='classification', tag_extractor=tag_extractor)
    resolve_graph.resolve(results_dir, graph_type='label', tag_extractor=tag_extractor)


    """
    Combining the graphs
    """
    combine_graph.combine_param(results_dir, param='classification_graph', tag_extractor=tag_extractor)
    combine_graph.combine_param(results_dir, param='article_graph', tag_extractor=tag_extractor)
    combine_graph.combine_param(results_dir, param='label_graph', tag_extractor=tag_extractor)

    combine_graph.save_graph(combine_dir, tag=f'-{project}-{dump_date}', graph_type='classification')
    combine_graph.save_graph(combine_dir, tag=f'-{project}-{dump_date}', graph_type='article')
    combine_graph.save_graph(combine_dir, tag=f'-{project}-{dump_date}', graph_type='label')


    """
    Save XC data
    """
    xc_data = XCDataset()
    xc_data.create_XCData(combine_dir, xc_dir, tag=f'-{project}-{dump_date}')

