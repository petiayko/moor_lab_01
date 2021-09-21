def read(path):
    data = open(path, 'r')
    table = []
    for line in data:
        if '|' in line:
            line_list = line.split(' ')
            table.append((
                [int(val) for val in line_list[:line_list.index('|')]],
                int(line_list[len(line_list) - 1].replace('\n', ''))
            ))
    objective = table[len(table) - 1]
    del table[len(table) - 1]

    return table, objective


if __name__ == '__main__':
    coef, obj = read('input.txt')
    for line in coef:
        print(line)
    print()
    # print(obj)
