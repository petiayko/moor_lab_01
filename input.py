import re


class Line:
    def __init__(self, line, variables):
        self.line = line
        self.variables = variables

    def check_validation(self):
        line = self.line
        if ('>' in line and '<' not in line) or ('>' not in line and '<' in line):
            if line[line.find('=') + 1:].isdigit():
                pattern = re.compile(r'-?\S*x\d+|-?\S+x?|-?x')
                line = line[:line.find('<=' * ('<=' in line) + '>=' * ('>=' in line))]
                if re.match(pattern, line):
                    return
        raise Exception('Wrong format of input data')

    def get_sign(self):
        self.check_validation()
        line = self.line
        if ('>=' in line and '<=' not in line) or ('>=' not in line and '<=' in line):
            return 1 - 2 * ('<=' in line)

    def get_free(self):
        self.check_validation()
        line = self.line
        return int(line[line.find('<=' * ('<=' in line) + '>=' * ('>=' in line)) + 2:])

    def get_vector(self):
        self.check_validation()
        pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
        line = self.line.replace(',', '')
        line = line.replace('.', '')
        line = line[:line.find('<=' * ('<=' in line) + '>=' * ('>=' in line))]
        line = pattern.findall(line)

        vector = [0 for i in range(self.variables)]
        for term in line:
            if not term[:term.find('x')] or term[:term.find('x')] == '+':
                vector[int(term[term.find('x') + 1:]) - 1] = 1
            else:
                if term[:term.find('x')] == '-':
                    vector[int(term[term.find('x') + 1:]) - 1] = -1
                elif term[:term.find('x')][0] == '0':
                    vector[int(term[term.find('x') + 1:]) - 1] = int(term[:term.find('x')]) / 10
                else:
                    vector[int(term[term.find('x') + 1:]) - 1] = int(term[:term.find('x')])

        return vector


class Target:
    def __init__(self, line, variables):
        self.line = line
        self.variables = variables

    def check_validation(self):
        line = self.line
        if '->' in line:
            if ('min' in line and 'max' not in line) or ('min' not in line and 'max' in line):
                if line.find('m') > line.find('->'):
                    return
        raise Exception('Wrong format of input data')

    def get_goal(self):
        self.check_validation()
        line = self.line
        return 1 - 2 * int('max' in line)

    def get_free(self):
        self.check_validation()
        line = self.line
        pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
        line = pattern.findall(line[line.find('=') + 1:line.find('->')])
        for term in line:
            if 'x' not in term:
                return int(term)
        return 0

    def get_vector(self):
        line = self.line
        pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
        line = pattern.findall(line[line.find('=') + 1:line.find('->')])

        vector = [0 for i in range(self.variables)]
        for term in line:
            if 'x' in term:
                if not term[:term.find('x')] or term[:term.find('x')] == '+':
                    vector[int(term[term.find('x') + 1:]) - 1] = 1
                elif term[:term.find('x')] == '-':
                    vector[int(term[term.find('x') + 1:]) - 1] = -1
                else:
                    vector[int(term[term.find('x') + 1:]) - 1] = int(term[:term.find('x')])

        return vector


def get_vectors(path):
    file = open(path, 'r')
    Ax = []
    F = None
    lines = [line.replace('\n', '') for line in file]
    for line in lines:
        if 'F=' not in line:
            row = Line(line=line, variables=len(lines) - 1)
            Ax.append(row)
        else:
            F = Target(line=line, variables=len(lines) - 1)

    return get_simplex_table(Ax, F)


def get_simplex_table(Ax, F):
    table = []
    for i in range(len(Ax)):
        row = [-Ax[i].get_free() * Ax[i].get_sign()] + [val * Ax[i].get_sign() for val in Ax[i].get_vector()]
        table.append(row)
    table.append([F.get_free()] + [val * F.get_goal() for val in F.get_vector()])

    solve(table)
    return table


def solve(s_t):
    max_abs, tar_col = -1, -1
    for i in range(len(s_t[len(s_t) - 1])):
        if abs(s_t[len(s_t) - 1][i]) > max_abs:
            max_abs = abs(s_t[len(s_t) - 1][i])
            tar_col = i

    min_div, tar_row = 10**8, -1
    for j in range(len(s_t) - 1):
        if abs(s_t[j][0] / s_t[j][tar_col]) < min_div:
            min_div = abs(s_t[j][0] / s_t[j][tar_col])
            tar_row = j

    print(f'Solving:\n\tCol: {tar_col}\n\tRow: {tar_row}\n\tEl: {s_t[tar_row][tar_col]}\n')

    zhord_exp(s_t, tar_col, tar_row)


def zhord_exp(s_t, col, row):
    el = s_t[row][col]
    # rot_s_t = swap(s_t, col, row)
    rot_s_t = s_t
    # prt(rot_s_t)
    for i in range(len(rot_s_t)):  # rows
        for j in range(len(rot_s_t[0])):  # cols
            if i == row and j != col:
                rot_s_t[i][j] = -s_t[i][j] / el
            elif i != row and j == col:
                rot_s_t[i][j] = s_t[i][j] / el
            elif i == row and j == col:
                rot_s_t[i][j] = 1 / el
            # else:
            #     rot_s_t[i][j] = s_t[i][j] - (s_t[i][row] * s_t[col][j]) / el
    prt(rot_s_t)


def swap(table, col, row):
    for i in range(len(table[col])):
        table[col][i], table[i][row] = table[i][row], table[col][i]
    return table


def prt(table):
    for i in table:
        print(i)
    print()


# def parse_line(s):
#     pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
#     target = 0
#     if 'F=' in s:
#     #     s = s[s.find('F=') + 2:]
#     #     if s[s.find('->') + 2:] == 'max':
#     #         target = -1
#     #     elif s[s.find('->') + 2:] == 'min':
#     #         target = 1
#     #     s = s[:s.find('->')]
#     #     matches = [i[:i.find('x')] if 'x' in i else i for i in pattern.findall(s)]
#     #     matches = [1 if not i else i for i in matches]
#     #     matches = [-1 if i == '-' else int(i) for i in matches]
#     #     print(matches)
#         return
#
#     if ('>=' in s and '<=' not in s) or ('>=' not in s and '<=' in s):
#         target = 1 - 2 * ('<=' in s)
#         limit = target * int(s[s.find('<=' * ('<=' in s) + '>=' * ('>=' in s)) + 2:])
#         s = s[:s.find('<=' * ('<=' in s) + '>=' * ('>=' in s))]
#
#     matches = pattern.findall(s)
#     # matches = [i[:i.find('x')] if 'x' in i else i for i in pattern.findall(s)]
#     # matches = [1 if not i else i for i in matches]
#     # matches = [-1 if i == '-' else int(i) for i in matches]
#
#     max_variable = max([int(i[i.find('x') + 1:]) for i in matches])
#
#     vec_of_coef = ['0' for i in range(max_variable)]
#     for term in matches:
#         vec_of_coef[int(term[term.find('x') + 1:]) - 1] = term[:term.find('x')]
#     vec_of_coef = [1 if not i else i for i in vec_of_coef]
#     vec_of_coef = [-1 if i == '-' else int(i) for i in vec_of_coef]
#
#     print(vec_of_coef)
#     return
#
#
# # def parse_line(s):
# #     limit = 0
# #     # target = -1
# #     if 'F' in s:
# #         # target = int(s[s.find('->') + 2:len(s)-1] == 'min')
# #         s = s[s.find('F=') + 2:]
# #     else:
# #         if '<=' in s:
# #             target = 0
# #             limit = int(s[s.find('<=') + 2:])
# #         elif '>=' in s:
# #             target = 1
# #             limit = int(s[s.find('>=') + 2:])
# #     coefs = []
# #     for i in range(1, 4):
# #         if f'x{i}' in s:
# #             coef = s[:s.find(f'x{i}')]
# #             if coef == '+' or not coef:
# #                 coef = 1
# #             elif coef == '-':
# #                 coef = -1
# #             coefs.append(coef)
# #             s = s[s.find(f'x{i}') + 2:]
# #         else:
# #             coefs.append(0)
# #
# #     # return [int(i) for i in koefs], target, limit
# #     return [int(i) for i in coefs], limit
#
#
# def simplex_table(A, C, free=None):
#     if free is None:
#         free = [1, 2, 3]
#
#     output = '\t\tC\t'
#     for i in free:
#         output += f'x{i}\t'
#     print(output)
#
#     count = len(free) + 1
#     for i in range(count - 1):
#         output = f'x{i + count}\t\t{C[i]}\t'
#         for j in range(len(free)):
#             output += str(-A[i][j]) + '\t'
#         print(output)
#
#     output = f'F\t\t{C[count - 1]}\t'
#     for j in range(len(free)):
#         output += str(-A[count - 1][j]) + '\t'
#     print(output)
#
#
# def read(path):
#     input_file = open(path, 'r')
#     A = []
#     C = []
#     for line in input_file:
#         parse_line(line.replace('\n', ''))
#         # parsed_line = parse_line(line)
#         # A.append(parsed_line[0])
#         # C.append(parsed_line[1])
#     input_file.close()
#
#     # print(A, C, sep='\n')
#
#     # simplex_table(A, C)
