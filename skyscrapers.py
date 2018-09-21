import itertools
from functools import reduce

def get_clue(values):
    
    # store is [higher_seen_building, number_of_skyscrapper_visible]
    return reduce(
        lambda store, val: 
            [store[0] if val < store[0] else val,  # update the higher building if this one is higher
            store[1] + 1 if val > store[0] else store[1]],
        values,
        [0, 0])[1]

all_possibility = itertools.permutations(range(1, 8), 7)
line_clues_poss = map(lambda x: filter(lambda vals: get_clue(vals) == x, all_possibility), range(1, 8))

print(set(list(line_clues_poss[5])).intersection(list(line_clues_poss[6])))
