import os
# 获取最大节点值
def get_max_index():
    max_index = 0
    nodeset = set()
    with open("Data.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            From ,To = map(int, line.split())
            temp = max(From,To)
            if temp > max_index:
                max_index = temp
    return max_index


# 参数
teleport_parameters = [0.75, 0.85, 0.9]
max_iter = 100  # 最大迭代次数
THRESHOLD = 1e-8  # 收敛范围
max_node_index = get_max_index()
node_num = max_node_index + 1


# 读数据，并以邻接表的方式存储图
def load_file():
    adj_list = [[i,0,[]] for i in range(node_num)] # 0:source node 1:出度 2:目的点集
    with open("Data.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            From ,To = map(int, line.split())
            adj_list[From][1] += 1
            if To not in adj_list[From][2]:
                adj_list[From][2].append(To)
    return adj_list


# 计算PageRank
def pagerank(teleport_parameter, adjlist):
    r_old = [1 / node_num for i in range(node_num)]  # 初始化为全1/n
    count = 0  # 迭代次数
    while count < max_iter:
        # 计算M*r_old
        temp1 = [0 for i in range(node_num)]
        for node in adjlist:
            for dest in node[2]:
                temp1[dest] += r_old[node[0]] / node[1]
        # 计算r_new = beta * M * r_old +(1-bata/N)
        r_new = [teleport_parameter * temp1[i] + (1 - teleport_parameter) * (1 / node_num) for i in range(node_num)]
        # 比较是否收敛
        score = 0
        for i in range(node_num):
            score += abs(r_old[i] - r_new[i])
        print("iter:{0} score:{1}".format(count, score))
        if score <= THRESHOLD:
            print("达到收敛。")
            return r_new
        count += 1
        r_old = r_new


# 输出结果
def report(teleport_parameter, r):
    nodes = [[i,r[i]] for i in range(node_num)]
    nodes.sort(key=lambda x: x[1], reverse=True)
    result_output_file_path = '.\\basic_pagerank_result'
    if not os.path.exists(result_output_file_path):
        os.makedirs(result_output_file_path)
    with open(os.path.join(result_output_file_path,"basic_result_{}.txt".format(teleport_parameter)), "w") as f:
        for key, value in nodes[:100]:
            print("[{0}]\t[{1}]".format(key,value))
            f.write("[{0}]\t[{1}]\n".format(key, value))


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    adjlist = load_file()
    for teleport_parameter in teleport_parameters:
        r = pagerank(teleport_parameter, adjlist)
        report(teleport_parameter, r)



