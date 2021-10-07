import re
import copy


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


class SimplexTable:
    def __init__(self, Ax, F):
        self.Ax = Ax
        self.F = F

        self.table = self.get_simplex_table()
        self.variables = len(self.F.get_vector())
        self.base = [1, 2, 3]
        self.free = [i for i in range(1, self.variables * 2 + 1) if i not in self.base]

    def get_simplex_table(self):
        simplex_table = []
        for i in range(len(self.Ax)):
            row = [-self.Ax[i].get_free() * self.Ax[i].get_sign()] + [-val * self.Ax[i].get_sign() for val in
                                                                      self.Ax[i].get_vector()]
            simplex_table.append(row)
        simplex_table.append([self.F.get_free()] + [-val for val in self.F.get_vector()])
        return simplex_table

    def find_pivot_optimise(self):
        max_abs, support_column = -1, -1
        for i in range(1, len(self.table[len(self.table) - 1])):
            if self.table[len(self.table) - 1][i] < 0 and abs(self.table[len(self.table) - 1][i]) > max_abs:
                max_abs = abs(self.table[len(self.table) - 1][i])
                support_column = i

        min_div, support_row = 10 ** 8, -1
        for j in range(len(self.table) - 1):
            if self.table[j][support_column] != 0:
                if abs(self.table[j][0] / self.table[j][support_column]) < min_div:
                    min_div = abs(self.table[j][0] / self.table[j][support_column])
                    support_row = j

        # print(support_column, self.base.index(support_column), self.base)
        self.base[support_column - 1], self.free[support_row] = self.free[support_row], self.base[support_column - 1]
        return support_row, support_column

    def find_pivot(self):
        support_row = -1
        for i in range(len(self.table)):
            if self.table[i][0] < 0:
                support_row = i
                break

        support_column = -1
        for j in range(1, len(self.table[support_row])):
            if self.table[support_row][j] < 0:
                support_column = j
                break

        self.base[support_column - 1], self.free[support_row] = self.free[support_row], self.base[support_column - 1]
        return support_row, support_column

    def jordan_exception(self, support_row, support_column):
        pivot = self.table[support_row][support_column]
        print(pivot)
        simplex_table_iter = copy.deepcopy(self.table)
        for i in range(len(simplex_table_iter)):  # rows
            for j in range(len(simplex_table_iter[0])):  # cols
                if i == support_row and j != support_column:
                    simplex_table_iter[i][j] = round(self.table[i][j] / pivot, 3)
                elif i != support_row and j == support_column:
                    simplex_table_iter[i][j] = round(-self.table[i][j] / pivot, 3)
                elif i == support_row and j == support_column:
                    simplex_table_iter[i][j] = round(1 / pivot, 3)
                else:
                    simplex_table_iter[i][j] = round(self.table[i][j] - (
                            self.table[support_row][j] * self.table[i][support_column]) / pivot, 3)
        return simplex_table_iter

    def solve(self):
        while True:
            print(self)
            if min([i[0] for i in self.table[:len(self.table) - 1]]) < 0:
                row, column = self.find_pivot()
                self.table = copy.deepcopy(self.jordan_exception(support_column=column, support_row=row))
                continue
            if -self.F.get_goal() * min(self.table[len(self.table) - 1][1:]) < 0:
                row, column = self.find_pivot_optimise()
                self.table = copy.deepcopy(self.jordan_exception(support_column=column, support_row=row))
                continue
            break

        return [i[0] for i in self.table[:len(self.table[0]) - 1]], self.table[len(self.table) - 1][0]

    def __repr__(self):
        rows = [f'x{str(i)}' for i in self.free] + ['F']
        output = '\t\tC\t\t' + '\t\t'.join([f'x{i}' for i in self.base]) + '\n'
        for i in range(len(self.table)):
            output += f'{rows[i]}\t\t'
            for j in range(len(self.table[i])):
                output += '%5.3f\t'
            output = output % tuple(self.table[i])
            output += '\n'
        return output

