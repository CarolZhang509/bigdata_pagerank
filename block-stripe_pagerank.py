import pickle as pkl
import numpy as np
import json
import os


PRINT_NUM = 100
SAVE_CHECKPOINT_INTERVAL = 10
BLOCK_NUM = 10  # identify the num of block-stripes
THRESHOLD = 1e-8

teleport_parameters = [0.75, 0.85, 0.9] 

class IndexTransfer:
    def __init__(self, node_num):
        """
        初始化IndexTransfer类
        
        参数：
        node_num (int): 图中节点的总数
        """
        self.node_num = node_num  # 节点总数
        self.block_num = BLOCK_NUM  # 块的数量
        self.num_in_group = node_num // self.block_num + 1  # 每个块中的节点数
        self.num_in_last_group = node_num % self.num_in_group  # 最后一个块中的节点数（可能少于其他块）

    def calc_aim_block_index(self, aim):
        """
        计算给定节点的目标块索引
        """
        return aim // self.num_in_group

    def dest2stripedest(self, dest):
        """
        将目标节点索引转换为其在块内的索引
        """
        return dest % self.num_in_group


def dump_vector(transfer, block_index, r_, new=False):
    if block_index == BLOCK_NUM - 1:
        r_ = r_[:transfer.num_in_last_group]
    if new == False:
        file_name = os.path.join(block_stripe_data_path, 'vector_{}.vector'.format(block_index))
        file_name1 = os.path.join(block_stripe_data_path, 'vector_{}_read.json'.format(block_index))
    else:
        file_name = os.path.join(block_stripe_data_path, 'vector_{}_new.vector'.format(block_index))
        file_name1 = os.path.join(block_stripe_data_path, 'vector_{}_new.json'.format(block_index))
    with open(file_name, "wb") as wf:
        pkl.dump(r_, wf)
    with open(file_name1, "w") as wf:
        json.dump(str(r_), wf)

def load_vector(block_index, new=False):
    if new == False:
        file_name = os.path.join(block_stripe_data_path, 'vector_{}.vector'.format(block_index))
    else:
        file_name = os.path.join(block_stripe_data_path, 'vector_{}_new.vector'.format(block_index))
    with open(file_name, "rb") as f:
        r = pkl.load(f)

    return r


def load_matrix_stripe(index):
    file_name = os.path.join(block_stripe_data_path, 'link_matrix_{}.matrix'.format(index))
    f = open(file_name, "rb")
    stripe = pkl.load(f)
    return stripe


def read_graph(node_num):
    Link_Matrix = {}

    with open(data_path) as file:
        for line in file:
            fm, to = map(int, line.split())
            node_num = max(node_num, fm, to)

            if fm not in Link_Matrix:
                Link_Matrix[fm] = [1, [to]]
            else:
                Link_Matrix[fm][0] += 1
                Link_Matrix[fm][1].append(to)

    print("load data finish")
    return {k: v for k, v in sorted(Link_Matrix.items())}, node_num



def load_data():
    Node_Num = -1
    Link_Matrix, Node_Num = read_graph(Node_Num)
    Node_Num += 1  
    transfer = IndexTransfer(Node_Num)
    #将处理后的矩阵条带存储起来
    for i in range(0, BLOCK_NUM):
        Link_Matrix_List = {}
        for fm in Link_Matrix:
            Link_Matrix_List[fm] = [Link_Matrix[fm][0],
                                    [elem for elem in Link_Matrix[fm][1] if
                                     elem < (i + 1) * transfer.num_in_group and elem >= i * transfer.num_in_group]]
            if len(Link_Matrix_List[fm][1]) == 0:
                del Link_Matrix_List[fm]
        # 将给定的矩阵条带（stripe）以二进制写入模式打开一个文件，然后使用pickle模块将条带保存到该文件中
        f_name = os.path.join(block_stripe_data_path, 'link_matrix_{}.matrix'.format(i))
        f_name1 = os.path.join(block_stripe_data_path, 'link_matrix_{}.json'.format(i))
        f = open(f_name, "wb")
        pkl.dump(Link_Matrix_List, f)

        with open(f_name1, "w") as f:
            for link_matrix in Link_Matrix_List:
                f.write(str(Link_Matrix_List[link_matrix])+"\n")

    return transfer


def normalize_list_randomwalk2(vector_sum, r_random, transfer):
    flag = 1
    for block_index in range(0, BLOCK_NUM):
        r_new = load_vector(block_index, True)
        r_new = teleport_parameter * (r_new + (1 - vector_sum) / transfer.node_num) + r_random[:len(r_new)]
        r_old = load_vector(block_index)
        if flag == 1:
            flag = (np.abs(r_new - r_old)).sum() < THRESHOLD * len(r_old) # 判断块的相似性
        if block_index < BLOCK_NUM:
            dump_vector(transfer, block_index, r_new)
    return flag


def matrix_block_multiple(matrix_stripe, block_index, transfer, r_new):  # stripe和v的一块乘
    r_old = load_vector(block_index)

    # 相乘
    for i in dict(filter(
            lambda x: x[0] >= block_index * transfer.num_in_group and x[0] < (block_index + 1) * transfer.num_in_group,
            matrix_stripe.items())):  # 遍历转移矩阵stripe
        if i >= (block_index + 1) * transfer.num_in_group:
            break
        for to in matrix_stripe[i][1]:
            to_block_index = transfer.dest2stripedest(to)
            fm_block_index = transfer.dest2stripedest(i)
            r_new[to_block_index] += r_old[fm_block_index] / matrix_stripe[i][0]
    return r_new


def matrix_stripe_multiple(stripe_index, transfer):  # stripe和v乘
    matrix_stripe = load_matrix_stripe(stripe_index)
    r_new = np.zeros(transfer.num_in_group)
    for block_index in range(0, BLOCK_NUM):
        r_new = matrix_block_multiple(matrix_stripe, block_index, transfer, r_new)

    dump_vector(transfer, stripe_index, r_new, new=True)
    return r_new.sum()


def matrix_multiple(transfer):
    sum_list = np.zeros(BLOCK_NUM)
    for stripe_index in range(0, BLOCK_NUM):
        sum_list[stripe_index] = matrix_stripe_multiple(stripe_index, transfer)
    return sum_list.sum()


def initialize(transfer):
    if transfer.node_num == 0:
        return
    r = np.ones(transfer.num_in_group) / transfer.node_num
    for block_index in range(0, BLOCK_NUM):
        dump_vector(transfer, block_index, r)


def output_result_list(transfer):
    # 挑出每个文件的前100个
    print("start calculating final rank")
    results = {}
    for i in range(0, BLOCK_NUM):
        result = load_vector(i)
        sort_result = dict(zip(np.argsort(-result)[:PRINT_NUM] + i * transfer.num_in_group,
                               sorted(result, reverse=True)[:PRINT_NUM]))
        results.update(sort_result)
    results = dict(sorted(results.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))
    print("start output")
    with open(result_output_filename, "w") as f:
        for i, key in enumerate(results):
            f.write("[%s]\t[%s]\n" % (str(key), str(results[key])))
            if i == 99:
                break


def block_stripe_pagerank(transfer, teleport_parameter):
    print("block stripe pangerank")
    initialize(transfer)
    r_random = np.ones(transfer.num_in_group) / \
               transfer.node_num * (1 -teleport_parameter)
    print("initialize finish")
    flag = 0
    round = 0
    while not flag:  # 最后一组个数
        vector_sum = matrix_multiple(transfer)  # 函数要实现收敛判断
        flag = normalize_list_randomwalk2(vector_sum, r_random, transfer)
        round += 1

    print("multiple finish")


if __name__ == '__main__':
    data_path = '.\\Data.txt'
    block_stripe_data_path = '.\\block-stripe_data'
    if not os.path.exists(block_stripe_data_path):
        os.makedirs(block_stripe_data_path)
    result_output_file_path = '.\\block-stripe_result'
    if not os.path.exists(result_output_file_path):
        os.makedirs(result_output_file_path)
    for teleport_parameter in teleport_parameters:
        result_output_filename = os.path.join(result_output_file_path, "block-stripe_result_{}.txt".format(teleport_parameter))
        print('Block-Stripe Version running..', float(teleport_parameter))
        transfer = load_data()
        block_stripe_pagerank(transfer, teleport_parameter)
        output_result_list(transfer)