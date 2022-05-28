def find_ancestors_of_evidence(evidence_nodes, bayes_nets, n):
    is_ancestor = [False] * n
    ancestors = evidence_nodes.copy()
    while len(ancestors) != 0:
        ancestor = ancestors.pop()
        if not is_ancestor[ancestor]:
            is_ancestor[ancestor] = True
            ancestors = ancestors + bayes_nets[ancestor][0]
    return is_ancestor


def find_dependence(bayes_net, is_ancestor, evidence, start_node, end_node, n):
    path = [[start_node, True]]
    dependent_nodes = [False] * n
    visited = [False] * (2 * n)
    while len(path) != 0:
        node, direction = path.pop()
        if node == end_node:
            dependent_nodes[node] = True
            return dependent_nodes, True
        if direction:
            visited_index = node * 2 + 1
        else:
            visited_index = node * 2
        if not visited[visited_index]:
            visited[visited_index] = True
            dependent_nodes[node] = (evidence[node] == -1)
            if direction and (evidence[node] == -1):
                parents = list(map(lambda x: [x, True], bayes_net[node][0]))
                children = list(map(lambda x: [x, False], bayes_net[node][1]))
                if (end_node in parents) or (end_node in children):
                    dependent_nodes[end_node] = True
                    return dependent_nodes, True
                path += parents + children
            if not direction:
                parents = []
                children = []
                if evidence[node] == -1:
                    children = list(map(lambda x: [x, False], bayes_net[node][1]))
                if is_ancestor[node]:
                    parents = list(map(lambda x: [x, True], bayes_net[node][0]))
                if (end_node in parents) or (end_node in children):
                    dependent_nodes[end_node] = True
                    return dependent_nodes, True
                path += parents + children
    return dependent_nodes, dependent_nodes[end_node]


def increase_binary(number):
    counter = 0
    while True:
        if number[counter] == 0:
            number[counter] = 1
            return number
        else:
            number[counter] = 0
            counter += 1


def update_cpt(node, value, cpt):
    new_cpt = []
    for row in cpt:
        if row[node] == value:
            new_cpt.append(row)
    return new_cpt


def find_distribution(first_variable, second_variable, cpts, n, evidence_nodes):
    order = [i for i in range(n)]
    order.remove(first_variable)
    order.remove(second_variable)
    for evidence in evidence_nodes:
        order.remove(evidence)
    for node in order:
        cpts, joint_cpts = find_cpts_with_node(node, cpts)
        joint_cpt = find_joint(joint_cpts)
        eliminated_cpt = eliminate(node, joint_cpt)
        cpts.append(eliminated_cpt)
    return cpts


def eliminate(node, joint_cpt):
    dict = {}
    new_cpt = []
    for row in joint_cpt:
        token = ""
        for key in row.keys():
            if key != node and key != 'P':
                if row[key]:
                    token = token + '1'
                else:
                    token = token + '0'
        if row[node]:
            token = '1' + token
        else:
            token = '0' + token
        row["token"] = token
        dict[token] = row
    for row in joint_cpt:
        token = row["token"]
        if dict[token] != 'N':
            sum = 0
            if token[0] == '0':
                sum = dict['1' + token[1:]]['P']
                dict['1' + token[1:]] = 'N'
            else:
                sum = dict['0' + token[1:]]['P']
                dict['0' + token[1:]] = 'N'
            row['P'] = row['P'] + sum
            del row[node]
            del row["token"]
            new_cpt.append(row.copy())
    return new_cpt


def find_cpts_with_node(node, cpts):
    new_cpts = []
    joint_cpts = []
    for cpt in cpts:
        if node in cpt[0].keys():
            joint_cpts.append(cpt)
        else:
            new_cpts.append(cpt)
    return new_cpts, joint_cpts


def find_joint(cpts):
    if len(cpts) == 1:
        return cpts[0]
    for i in range(1, len(cpts)):
        cpts[0] = multipy_table(cpts[0], cpts[i])
    return cpts[0]


def multipy_table(first, second):
    new_cpt = []
    first_keys = first[0].keys()
    second_keys = second[0].keys()
    join_keys = []
    nonjoint_keys = []
    for key in second_keys:
        if key in first_keys and key != 'P':
            join_keys.append(key)
        else:
            nonjoint_keys.append(key)
    for second_row in second:
        for first_row in first:
            flag = True
            for key in join_keys:
                if first_row[key] != second_row[key]:
                    flag = False
            if flag:
                new_row = first_row.copy()
                for key in nonjoint_keys:
                    if key != 'P':
                        new_row[key] = second_row[key]
                    else:
                        new_row['P'] = first_row['P'] * second_row['P']
                new_cpt.append(new_row)
    return new_cpt


def find_probability(var_to_compute, var_to_eliminate, cpts):
    new_cpts, joint_cpts = find_cpts_with_node(var_to_eliminate, cpts)
    joint_cpt = find_joint(joint_cpts)
    eliminated_cpt = eliminate(var_to_eliminate, joint_cpt)
    new_cpts.append(eliminated_cpt)
    final_joint = find_joint(new_cpts)
    if final_joint[0][var_to_compute]:
        true_p = final_joint[0]['P']
        false_p = final_joint[1]['P']
    else:
        true_p = final_joint[1]['P']
        false_p = final_joint[0]['P']
    print(round((true_p / (true_p + false_p)), 2))


n = int(input())
bayes_net = [[[], []] for _ in range(n)]
cpts = []
for i in range(n):
    bayes_net[i][0] = list(map(lambda x: int(x) - 1, input().split()))
    for parent in bayes_net[i][0]:
        bayes_net[parent][1].append(i)
    probability = list(map(float, input().split()))
    parents = bayes_net[i][0].copy()
    parents.reverse()
    cpt = []
    number = [0] * (len(parents) + 2)
    counter = 0
    while True:
        row = {}
        for k in range(len(parents)):
            if number[k] == 0:
                row[parents[k]] = True
            else:
                row[parents[k]] = False
        row[i] = number[len(parents)] == 0
        number = increase_binary(number)
        cpt.append(row)
        if counter < len(probability):
            row['P'] = probability[counter]
        else:
            row['P'] = 1 - probability[counter - len(probability)]
        counter += 1
        if number[len(parents) + 1] == 1:
            break
    cpts.append(cpt)
evidence = [-1] * n
evidence_nodes = []
lst = input().split(',')
if lst[0] != '':
    for evi in lst:
        if len(evi) > 4:
            node = int(evi[0:2]) - 1
            val = (evi[4] == '1')
        else:
            node = int(evi[0]) - 1
            val = (evi[3] == '1')
        evidence[node] = val
        evidence_nodes.append(node)
        for child in bayes_net[node][1]:
            cpts[child] = update_cpt(node, val, cpts[child])
        cpts[node] = update_cpt(node, val, cpts[node])

first_variable, second_variable = (map(lambda x: int(x) - 1, input().split()))
is_ancestor = find_ancestors_of_evidence(evidence_nodes, bayes_net, n)
dependent_nodes, is_dependent = find_dependence(bayes_net, is_ancestor, evidence, first_variable, second_variable, n)
if is_dependent:
    print("dependent")
else:
    print("independent")
cpts = find_distribution(first_variable, second_variable, cpts, n, evidence_nodes)
mycopy = []
for cpt in cpts:
    cpt_copy = []
    for row in cpt:
        cpt_copy.append(row.copy())
    mycopy.append(cpt_copy)
find_probability(first_variable, second_variable, cpts)
find_probability(second_variable, first_variable, mycopy)