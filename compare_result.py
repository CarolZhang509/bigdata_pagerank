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


def read_nodes_(filename):
    top_nodes = []
    with open(filename, 'r') as file:
        for line in file:
            node, value = map(float, extract_numbers(line))
            top_nodes.append((int(node), value))
    return top_nodes

def write_error(file_path, item, value):
    directory = os.path.dirname(file_path)
    # 如果目录不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 写入结果到文件
    with open(file_path, 'a') as file:
        file.write("{} {}\n".format(item, value))

def compare_with_lib():
    for teleport_parameter in teleport_parameters:
        block_list_of_tuples = read_nodes_('./block_result_{}.txt'.format(teleport_parameter))  
        networkx_list_of_tuples = read_nodes('./networkx_result_{}.txt'.format(teleport_parameter))

        for i in range(0,100):
            if block_list_of_tuples[i][0]!= networkx_list_of_tuples[i][0]:
                print(f"Item {i+1} not match")
            else:
                error_value = float(block_list_of_tuples[i][1] - networkx_list_of_tuples[i][1])
                write_error('./compare_result_{}.txt'.format(teleport_parameter), i+1, error_value)
                print(f"Item {i+1} match, error value is {error_value}")

if __name__ == '__main__':
    compare_with_lib()
