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
        for item, basic, block in items_values:
            file.write("item:{}\t basic_error:{}\t block_error:{}\n".format(item, basic, block))

def compare_with_lib():
    for teleport_parameter in teleport_parameters:
        block_nodes = read_nodes_from_file(f'./block-stripe_result/block-stripe_result_{teleport_parameter}.txt')  
        networkx_nodes = read_nodes(f'./networkx_result/networkx_result_{teleport_parameter}.txt')
        basic_nodes = read_nodes_from_file(f'./basic_pagerank_result/basic_result_{teleport_parameter}.txt')

        errors = []  # 用于存储错误信息
        for i, (basic_node, block_node, networkx_node) in enumerate(zip(basic_nodes, block_nodes, networkx_nodes), start=1):
            if (block_node[0] != networkx_node[0]) or (basic_node[0] != networkx_node[0]):
                print(f"Item {i} does not match.")
                errors.append((block_node[0], None, None))
            else:
                # print(block_node[0], '\t', type(block_node[0]))
                basic_error = block_node[1] - networkx_node[1]
                block_error = block_node[1] - networkx_node[1]
                errors.append((block_node[0], basic_error, block_error))

        # 将所有错误信息写入文件
        write_error(f'./__compare_result__/compare_result_{teleport_parameter}.txt', errors)

if __name__ == '__main__':
    compare_with_lib()
