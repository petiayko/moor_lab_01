from init import Target, Line, SimplexTable


def get_lines(file):
    A = []
    c = None
    lines = [line.replace('\n', '') for line in file]
    for line in lines:
        if 'F=' not in line:
            row = Line(line=line, variables=len(lines) - 1)
            A.append(row)
        else:
            c = Target(line=line, variables=len(lines) - 1)

    return A, c


def solve(path):
    A, c = get_lines(open(path, 'r'))
    simplex_table = SimplexTable(A, c)
    X, F_val = simplex_table.solve()
    ind = 0
    for i in simplex_table.free:
        print(f'x{i} = {X[ind]}')
        ind += 1
    print(f'F = {F_val}')
