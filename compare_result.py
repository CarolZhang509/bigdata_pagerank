import re
import os

teleport_parameters = [0.75, 0.85, 0.9]

def read_nodes(filename):
    top_nodes = []
    with open(filename, 'r') as file:
        for line in file:
            node, value = map(float, line.split())
            top_nodes.append((int(node), value))
    return top_nodes

def extract_numbers(text):
    # 使用正则表达式匹配数字
    pattern = r'\[(-?\d+(\.\d+)?)\]'
    matches = re.findall(pattern, text)
    
    # 提取匹配到的数字
    numbers = [float(match[0]) for match in matches]
    return numbers

def read_nodes_from_file(filename):
    top_nodes = []
    with open(filename, 'r') as file:
        for line in file:
            node, value = map(float, extract_numbers(line))
            top_nodes.append((int(node), value))
    return top_nodes

def write_error(file_path, items_values):
    directory = os.path.dirname(file_path)
    # 如果目录不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 写入结果到文件
    with open(file_path, 'w') as file:
        for item, value in items_values:
            file.write("{} {}\n".format(item, value))

def compare_with_lib():
    for teleport_parameter in teleport_parameters:
        block_nodes = read_nodes_from_file(f'./block-stripe_result/block-stripe_result_{teleport_parameter}.txt')  
        networkx_nodes = read_nodes(f'./networkx_result/networkx_result_{teleport_parameter}.txt')

        errors = []  # 用于存储错误信息
        for i, (block_node, networkx_node) in enumerate(zip(block_nodes, networkx_nodes), start=1):
            if block_node[0] != networkx_node[0]:
                print(f"Item {i} does not match.")
            else:
                # print(block_node[0], '\t', type(block_node[0]))
                error_value = block_node[1] - networkx_node[1]
                errors.append((block_node[0], error_value))

        # 将所有错误信息写入文件
        write_error(f'./__compare_result/compare_result_{teleport_parameter}.txt', errors)

if __name__ == '__main__':
    compare_with_lib()
