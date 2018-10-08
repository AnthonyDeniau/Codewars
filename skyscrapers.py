import itertools
import cProfile
from functools import reduce
import copy


COLUMN = 1
ROW = 2
NORMAL = 1
REVERSED = 2


class Cell(object):
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.candidates = set(range(1, size + 1))
    
    def is_resolved(self):
        return len(self.candidates) == 1

    @property
    def value(self):
        return list(self.candidates)[0]

class TheGrid(object):
    """
    The grid is composed of Cell of $size width and $size height
    Calculate all the possible solution for each line following clues
    Dedu
    """
    size = 7
    line_candidates_by_clue = []
    line_reverse_candidates_by_clue = []
    def __init__(self, size):
        self.get_line_candidates_by_clue()
        self.get_line_reverse_candidates_by_clue()
        self.cells = [[Cell(row, col, self.size) for col in range(self.size)] for row in range(self.size)]
        self.row_candidates = [set(itertools.permutations(range(1, self.size + 1), self.size)) for i in range(self.size)]
        self.col_candidates = [set(itertools.permutations(range(1, self.size + 1), self.size)) for i in range(self.size)]
    
    @classmethod
    def get_line_candidates_by_clue(cls):
        if len(cls.line_candidates_by_clue) != 0:
            print("retrieve cache for get_line_candidates_by_clue")
            return
        else:

            print("process get_line_candidates_by_clue")
            cls.line_candidates_by_clue = list(map(cls.get_candidates_for_line, range(0, cls.size + 1)))

    @classmethod
    def get_line_reverse_candidates_by_clue(cls):
        if len(cls.line_reverse_candidates_by_clue) != 0:
            return
        else:
            cls.line_reverse_candidates_by_clue = list(map(lambda u: list(map(lambda v: tuple(reversed(v)), u)), cls.line_candidates_by_clue))

    def convert_clockwise_position(self, clockwise_position):
        if clockwise_position < self.size:
            return COLUMN, clockwise_position, NORMAL
        elif clockwise_position >= self.size and clockwise_position < (self.size * 2):
            return ROW, clockwise_position - self.size, REVERSED
        elif clockwise_position >= (self.size * 2) and clockwise_position < (self.size * 3):
            return COLUMN, (self.size - 1) - (clockwise_position - (self.size * 2)), REVERSED
        else:
            return ROW, (self.size - 1) - (clockwise_position - (self.size * 3)), NORMAL

    def get_line_candidates(self, clue, direction):
        if direction == NORMAL:
            return copy.copy(self.line_candidates_by_clue[clue])
        else:
            return copy.copy(self.line_reverse_candidates_by_clue[clue])
    
    @staticmethod
    def get_clue(values):
        """ 
        calculate the number of visible skyscrapper
        """
        # store is [higher_building_seen, number_of_skyscrapper_visible]
        return reduce(
            lambda store, val: 
                [store[0] if val < store[0] else val,  # update the higher building if this one is higher
                store[1] + 1 if val > store[0] else store[1]],
            values,
            [0, 0])[1]

    @classmethod
    def get_candidates_for_line(cls, clue=0):
        """
        calculate all the possibility for a line (Row or Column) that satifies the given clue
        """
        if clue == 0:
            return list(itertools.permutations(range(1, cls.size + 1), cls.size))
        else:
            return list(filter(lambda vals: TheGrid.get_clue(vals) == clue, itertools.permutations(range(1, cls.size + 1), cls.size)))


    def _update_cells_candidates(self, typeOfLine, number):
        cells_candidates = self._get_cells_candidate(typeOfLine, number)
        for i in range(0, self.size):
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
        for number in range(self.size):
            self._update_cells_candidates(ROW, number)
            self._update_cells_candidates(COLUMN, number)
        self._backprogration_lines_candidates()
    
    def get_result(self):
        return [[cell.value for cell in row] for row in self.cells]
    
    def get_result_tuple(self):
        result = ()
        for row in self.cells:
            row_result = ()
            for cell in row:
                row_result += (cell.value,)
            result += (row_result,)
        return result
    
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
    return grid.get_result()


print(
    solve_puzzle([7,0,0,0,2,2,3, 0,0,3,0,0,0,0, 3,0,3,0,0,5,0, 0,0,0,0,5,0,4])
    ==
    [[1, 5, 6, 7, 4, 3, 2], [2, 7, 4, 5, 3, 1, 6], [3, 4, 5, 6, 7, 2, 1], [4, 6, 3, 1, 2, 7, 5], [5, 3, 1, 2, 6, 4, 7], [6, 2, 7, 3, 1, 5, 4], [7, 1, 2, 4, 5, 6, 3]]
    )

cProfile.run('''solve_puzzle([7,0,0,0,2,2,3, 0,0,3,0,0,0,0, 3,0,3,0,0,5,0, 0,0,0,0,5,0,4])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])
solve_puzzle([0,2,3,0,2,0,0, 5,0,4,5,0,4,0, 0,4,2,0,0,0,6, 5,2,2,2,2,4,1])''')
#print(list(grid.cells[2][0].candidates))