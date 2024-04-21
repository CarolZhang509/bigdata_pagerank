'''
Author: qmj
'''

import networkx as nx
import os

file_path = './Data.txt'
teleport_parameter = 0.85
tol = 1e-8

def read_data(file_path):
    graph = nx.DiGraph()
    with open(file_path, 'r') as file:
        for line in file:
            from_node, to_node = map(int, line.strip().split())
            graph.add_edge(from_node, to_node)
    return graph

def top_nodes(pr, num_top_nodes = 100):
    sorted_nodes = sorted(pr.items(), key = lambda x:x[1], reverse = True)
    return sorted_nodes[:num_top_nodes]

def write_result(file_path, data):
    directory = os.path.dirname(file_path)
    # 如果目录不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 写入结果到文件
    with open(file_path, 'w') as file:
        for node, score in data:
            file.write("{} {}\n".format(node, score))


def main():
    graph = read_data(file_path)
    pr = nx.pagerank(graph, alpha=teleport_parameter, tol=tol)
    top_100_nodes = top_nodes(pr)
    print(f'Top 100 Nodes with their PageRank scores (teleport parameter = {teleport_parameter}):')
    # for node, rank in top_100_nodes:
    #     print(f'NodeID: {node}, PageRank: {rank}')
    write_result('.\\networkx_result_{}.txt'.format(teleport_parameter), top_100_nodes)

if __name__ == '__main__':
    main()