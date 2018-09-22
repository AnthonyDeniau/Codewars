import itertools
from functools import reduce
import copy

def get_clue(values):
    # store is [higher_seen_building, number_of_skyscrapper_visible]
    return reduce(
        lambda store, val: 
            [store[0] if val < store[0] else val,  # update the higher building if this one is higher
            store[1] + 1 if val > store[0] else store[1]],
        values,
        [0, 0])[1]

def get_candidates_for_line(clue=0):
    if clue == 0:
        return list(itertools.permutations(range(1, 8), 7))
    else:
        return list(filter(lambda vals: get_clue(vals) == clue, itertools.permutations(range(1, 8), 7)))

def is_line_containing_values_in_cell(values, cell, line_candidate):
    return line_candidate[cell] in values

class Cell(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.candidates = set(range(1, 8))
    
    def is_resolved(self):
        return len(self.candidates) == 1

    @property
    def value(self):
        return list(self.candidates)[0]

COLUMN = 1
ROW = 2
NORMAL = 1
REVERSED = 2

line_candidates_by_clue = list(map(get_candidates_for_line, range(0, 8)))
line_reverse_candidates_by_clue = list(map(lambda u: list(map(lambda v: tuple(reversed(v)), u)), line_candidates_by_clue))

class TheGrid(object):
    def __init__(self, size):
        self.size = size
        self.cells = [[Cell(row, col) for col in range(size)] for row in range(size)]
        self.row_candidates = [set(itertools.permutations(range(1, 8), 7)) for i in range(7)]
        self.col_candidates = [set(itertools.permutations(range(1, 8), 7)) for i in range(7)]
    
    @staticmethod
    def convert_clockwise_position(clockwise_position):
        if clockwise_position < 7:
            return COLUMN, clockwise_position, NORMAL
        elif clockwise_position >= 7 and clockwise_position < 14:
            return ROW, clockwise_position - 7, REVERSED
        elif clockwise_position >= 14 and clockwise_position < 21:
            return COLUMN, 6 - (clockwise_position - 14), REVERSED
        else:
            return ROW, 6 - (clockwise_position - 21), NORMAL

    @staticmethod
    def get_line_candidates(clue, direction):
        if direction == NORMAL:
            return copy.deepcopy(line_candidates_by_clue[clue])
        else:
            return copy.deepcopy(line_reverse_candidates_by_clue[clue])

    def _update_cells_candidates(self, typeOfLine, number):
        cells_candidates = self._get_cells_candidate(typeOfLine, number)
        for i in range(0, 7):
            if typeOfLine == ROW:
                self.cells[number][i].candidates = self.cells[number][i].candidates.intersection(cells_candidates[i])
            else:
                self.cells[i][number].candidates = self.cells[i][number].candidates.intersection(cells_candidates[i])
    
    def _update_line_candidates(self, typeOfLine, number, line_candidates):
        if typeOfLine == ROW:
            self.row_candidates[number] = self.row_candidates[number].intersection(line_candidates)
        else:
            self.col_candidates[number] = self.col_candidates[number].intersection(line_candidates)

    def _get_cells_candidate(self, typeOfLine, number):
        if typeOfLine == ROW:
            return list(zip(*self.row_candidates[number]))
        else:
            return list(zip(*self.col_candidates[number]))

    def _backprogration_lines_candidates(self):
        for x, row in enumerate(self.cells):
            for y, cell in enumerate(row):
                #print("x: [%d] y:[%d] len row:[%d] len col: [%d]" % (x, y, len(self.row_candidates[x]), len(self.col_candidates[y])))
                self.row_candidates[x] = set(filter(lambda l: l[y] in cell.candidates, self.row_candidates[x]))
                self.col_candidates[y] = set(filter(lambda l: l[x] in cell.candidates, self.col_candidates[y]))
                #print("x: [%d] y:[%d] len row:[%d] len col: [%d]" % (x, y, len(self.row_candidates[x]), len(self.col_candidates[y])))

    def process_clue(self, clue, clockwise_position):
        typeOfLine, number, direction = self.convert_clockwise_position(clockwise_position)
        line_candidates = self.get_line_candidates(clue, direction)
        self._update_line_candidates(typeOfLine, number, line_candidates)

    def resolve(self):
        for number in range(7):
            self._update_cells_candidates(ROW, number)
            self._update_cells_candidates(COLUMN, number)
        self._backprogration_lines_candidates()
    
    def get_result(self):
        return [[cell.value for cell in row] for row in self.cells]
    
    def is_resolved(self):
        is_resolved = True
        for row in self.cells:
            for cell in row:
                is_resolved &= cell.is_resolved()
        return is_resolved

def print_result(grid):
    for x, row in enumerate(grid.cells):
        for y, cell in enumerate(row):
            print("x: %d, y: %d candidate: %d" % (x, y, len(cell.candidates)))

def solve_puzzle(clues):
    grid = TheGrid(7)
    for i, clue in enumerate(clues):
        grid.process_clue(clue, i)
    iterations = 0
    while grid.is_resolved() == False:
        iterations += 1
        grid.resolve()
    print(iterations)
    return grid.get_result()

grid = solve_puzzle([7,0,0,0,2,2,3, 0,0,3,0,0,0,0, 3,0,3,0,0,5,0, 0,0,0,0,5,0,4])
#print(list(grid.cells[2][0].candidates))