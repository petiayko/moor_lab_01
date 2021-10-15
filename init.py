import re
import copy


# класс "неравенство системы"
class Line:
    def __init__(self, line, variables):
        # строка неравенства, прочитанная из файла
        self.line = line
        # число переменных в данной задаче
        self.variables = variables

    # метод проверки корректоности введенных данных
    def check_validation(self):
        line = self.line
        if ('>' in line and '<' not in line) or ('>' not in line and '<' in line):
            if line[line.find('=') + 1:].isdigit():
                pattern = re.compile(r'-?\S*x\d+|-?\S+x?|-?x')
                line = line[:line.find('<=' * ('<=' in line) + '>=' * ('>=' in line))]
                if re.match(pattern, line):
                    return
        raise Exception('Wrong format of input data')

    # метод определения знака неравенства
    def get_sign(self):
        self.check_validation()
        line = self.line
        if ('>=' in line and '<=' not in line) or ('>=' not in line and '<=' in line):
            return 1 - 2 * ('<=' in line)

    # метод определения свободного члена неравенства
    def get_free(self):
        self.check_validation()
        line = self.line
        return int(line[line.find('<=' * ('<=' in line) + '>=' * ('>=' in line)) + 2:])

    # метод получения списка коэффициентов неравенства
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


# класса "целевая функция"
class Target:
    def __init__(self, line):
        # строка целевой функции, прочитанная из файла
        self.line = line
        # число переменных в данной задаче
        self.variables = len(self.get_vector())

    # метод поверки корректности введенных данных
    def check_validation(self):
        line = self.line
        if '->' in line:
            if ('min' in line and 'max' not in line) or ('min' not in line and 'max' in line):
                if line.find('m') > line.find('->'):
                    return
        raise Exception('Wrong format of input data')

    # метод определения стремления целевой функции (минимум или максимум)
    def get_goal(self):
        self.check_validation()
        line = self.line
        return 1 - 2 * int('max' in line)

    # метод определения свободного члена целевой фцнкции
    def get_free(self):
        self.check_validation()
        line = self.line
        pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
        line = pattern.findall(line[line.find('=') + 1:line.find('->')])
        for term in line:
            if 'x' not in term:
                return int(term)
        return 0

    # метод получения списка коэффициентов целевой функции
    def get_vector(self):
        line = self.line
        pattern = re.compile(r'-?\d*x\d+|-?\d+x?|-?x')
        line = pattern.findall(line[line.find('=') + 1:line.find('->')])
        self.variables = len(line)

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


# класс "симплекс-таблица"
class SimplexTable:
    def __init__(self, A, c):
        # A - список объектов класса "неравенство системы" - неравенства системы
        self.A = A
        # объект класса "целевая функция" - целевая функция
        self.c = c

        # симплекс-таблица
        self.table = self.get_simplex_table()
        # число переменных в данной задаче
        self.variables = len(self.c.get_vector())
        # список индексов свободных переменных (необходимо для вывода симплекс-таблицы на экран)
        self.free = [1, 2, 3]
        # список индексов базисных переменных (необходимо для вывода симплекс-таблицы на экран)
        self.base = [i for i in range(1, self.variables * 2 + 1) if i not in self.free]

    # метод заполнения симплекс-таблицы
    def get_simplex_table(self):
        simplex_table = []
        for i in range(len(self.A)):
            row = [-self.A[i].get_free() * self.A[i].get_sign()] + [-val * self.A[i].get_sign() for val in
                                                                    self.A[i].get_vector()]
            simplex_table.append(row)
        simplex_table.append([self.c.get_free()] + [-val for val in self.c.get_vector()])
        return simplex_table

    # метод нахождения разрешающего столбца и строки для поиска оптимального решения
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
        print(f'Pivot column: x{self.free[support_column - 1]}\n'
              f'Pivot row: x{self.base[support_row]}\n'
              f'Pivot element: {round(self.table[support_row][support_column], 3)}\n\n')
        self.free[support_column - 1], self.base[support_row] = self.base[support_row], self.free[support_column - 1]
        return support_row, support_column

    # метод нахождения разрешающего столбца и строки для поиска допустимого решения
    def find_pivot(self):
        support_row = [i[0] for i in self.table].index(-max([abs(i[0]) for i in self.table if i[0] < 0]))
        support_column = self.table[support_row].index(min(self.table[support_row][1:]))
        print(f'Pivot column: x{self.free[support_column - 1]}\n'
              f'Pivot row: x{self.base[support_row]}\n'
              f'Pivot element: {round(self.table[support_row][support_column], 3)}\n\n')
        self.free[support_column - 1], self.base[support_row] = self.base[support_row], self.free[support_column - 1]
        return support_row, support_column

    # метод жорданового исключения
    def jordan_exception(self, support_row, support_column):
        pivot = self.table[support_row][support_column]
        simplex_table_iter = copy.deepcopy(self.table)
        for i in range(len(simplex_table_iter)):  # rows
            for j in range(len(simplex_table_iter[0])):  # cols
                if i == support_row and j != support_column:
                    simplex_table_iter[i][j] = self.table[i][j] / pivot
                elif i != support_row and j == support_column:
                    simplex_table_iter[i][j] = -self.table[i][j] / pivot
                elif i == support_row and j == support_column:
                    simplex_table_iter[i][j] = 1 / pivot
                else:
                    simplex_table_iter[i][j] = self.table[i][j] - (
                            self.table[support_row][j] * self.table[i][support_column]) / pivot
        return simplex_table_iter

    # метод решения задачи (на выходе допустимое оптимальное решение)
    def solve(self):
        repetition = 0
        while True:
            print(f'Iteration number {repetition}')
            repetition += 1
            print(self)
            if min([i[0] for i in self.table[:len(self.table) - 1]]) < 0:
                row, column = self.find_pivot()
                self.table = copy.deepcopy(self.jordan_exception(support_column=column, support_row=row))
                continue
            # if min(self.table[len(self.table) - 1][1:]) < 0:
            if -self.c.get_goal() * min(self.table[len(self.table) - 1][1:]) < 0:
                row, column = self.find_pivot_optimise()
                self.table = copy.deepcopy(self.jordan_exception(support_column=column, support_row=row))
                continue
            break

        return [round(i[0], 3) for i in self.table[:len(self.table[0]) - 1]], round(self.table[len(self.table) - 1][0],
                                                                                    3)

    # метод печати симплекс-таблицы
    def __repr__(self):
        rows = [f'x{str(i)}' for i in self.base] + ['F']
        output = '\t\tC\t\t' + '\t\t'.join([f'x{i}' for i in self.free]) + '\n'
        for i in range(len(self.table)):
            output += f'{rows[i]}\t\t'
            for j in range(len(self.table[i])):
                output += '%5.3f\t'
            output = output % tuple(self.table[i])
            output += '\n'
        return output
