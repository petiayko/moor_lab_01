from init import Target, Line, SimplexTable


def get_lines(file):
    Ax = []
    F = None
    lines = [line.replace('\n', '') for line in file]
    for line in lines:
        if 'F=' not in line:
            row = Line(line=line, variables=len(lines) - 1)
            Ax.append(row)
        else:
            F = Target(line=line, variables=len(lines) - 1)

    return Ax, F


def solve(path):
    Ax, F = get_lines(open(path, 'r'))
    simplex_table = SimplexTable(Ax, F)
    X, F_val = simplex_table.solve()
    ind = 0
    for i in simplex_table.free:
        print(f'x{i} = {X[ind]}')
        ind += 1
    print(f'F = {F_val}')
