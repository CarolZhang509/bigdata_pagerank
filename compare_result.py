import re

def read_top_nodes(filename):
    top_nodes = []
    with open(filename, 'r') as file:
        for line in file:
            node, value = map(float, line.split())
            top_nodes.append((int(node), value))
    return top_nodes

def print_line(filename):
    with open(filename, 'r') as file:
        for line in file:
            print(line.strip())
            print(type(line.strip()))

def extract_numbers(text):
    # 使用正则表达式匹配数字
    pattern = r'\[(-?\d+(\.\d+)?)\]'
    matches = re.findall(pattern, text)
    
    # 提取匹配到的数字
    numbers = [float(match[0]) for match in matches]
    return numbers


def read_top_nodes_(filename):
    top_nodes = []
    with open(filename, 'r') as file:
        for line in file:
            node, value = map(float, extract_numbers(line))
            top_nodes.append((int(node), value))
    return top_nodes

def compare_with_lib():
    # block_list_of_tuples = read_top_nodes('./block_result.txt')
    block_list_of_tuples = read_top_nodes_('./block_result(0.85).txt')  
    networkx_list_of_tuples = read_top_nodes('./networkx_result.txt')

    for i in range(0,100):
        if block_list_of_tuples[i][0]!= networkx_list_of_tuples[i][0]:
            print(f"Item {i+1} not match")
        else:
            print(f"Item {i+1} match, error value is {float(block_list_of_tuples[i][1] - networkx_list_of_tuples[i][1])}")

if __name__ == '__main__':
    compare_with_lib()
