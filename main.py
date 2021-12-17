# Copyright 2021 Peter p.makretskii@gmail.com
from simplex_table import SimplexTable
from input import print_answer

# точка входа в программу
if __name__ == '__main__':
    filename = 'input/input2.txt'
    # чтение данных из файла, запись их в список
    data = [line.replace('\n', '') for line in open(filename)]
    # вызов метода print_answer для печати решения задачи
    print_answer(SimplexTable(data).solve())
