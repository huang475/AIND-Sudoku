import collections

assignments = []


def join_zip(collection_a, collection_b):
    """
    zip 2 collection and join each child tuple to string
    """
    return [''.join(combination)
            for combination in zip(collection_a, collection_b)]


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a+b for a in A for b in B]


ROWS = 'ABCDEFGHI'
COLS = '123456789'
FILLS = '123456789'
BOXES = cross(ROWS, COLS)

ROW_UNITS = [cross(row, COLS) for row in ROWS]
COL_UNITS = [cross(ROWS, col) for col in COLS]
SQUARE_UNITS = [
    cross(p_rows, p_cols)
    for p_rows in ['ABC', 'DEF', 'GHI']
    for p_cols in ['123', '456', '789']]
DIAG_UNITS = [join_zip(ROWS, COLS), join_zip(reversed(ROWS), COLS)]
UNIT_LIST = ROW_UNITS + COL_UNITS + SQUARE_UNITS + DIAG_UNITS

UNITS = dict((box, [unit for unit in UNIT_LIST if box in unit])
             for box in BOXES)
PEERS = dict((box, set(sum(UNITS[box], [])) - {box})
             for box in BOXES)


def flatten(_collections):
    return [value for collection in _collections for value in collection]


def unique_sorted_numeric_string(list_of_numeric_string):
    return sorted(set(''.join(list_of_numeric_string)))


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    if values[box] == value:
        return values
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def solved_values(values):
    return dict((box, value)
                for box, value in values.items() if len(value) == 1)


def solved(values):
    return len(solved_values(values)) == len(COLS) * len(ROWS)


def pick_box_with_least_values_larger_than_one(values):
    return min(dict((key, len(value))
                    for key, value in values.items() if len(value) > 1))


def find_twin_values_in_unit(unit, values):
    reversed_index = {}
    for box in unit:
        value = values[box]
        reversed_index[value] = (reversed_index.get(value) or []) + [box]
    twin_pairs = [(key, value) for key, value in reversed_index.items()
                  if (len(value) == len(key)) and (len(key) > 1)]
    return ''.join(pair[0] for pair in twin_pairs), \
           flatten([pair[1] for pair in twin_pairs])


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    _values = values.copy()
    for unit in UNIT_LIST:
        twin_values, twin_boxes = find_twin_values_in_unit(unit, _values)
        for twin_value in twin_values:
            for box in unit:
                if box not in twin_boxes:
                    _values = assign_value(
                        values,
                        box,
                        _values[box].replace(twin_value, ''))
    return _values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict([(box, '123456789' if value == '.' else value)
                 for box, value in zip(BOXES, grid)])


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in BOXES)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF':
            print(line)


def eliminate(values):
    _values = values.copy()
    for solved_box, solved_value in solved_values(_values).items():
        for box in PEERS[solved_box]:
            _values = assign_value(
                _values,
                box=box,
                value=_values[box].replace(solved_value, '')
            )
    return _values


def only_choice(values):
    _values = values.copy()
    for unit in UNIT_LIST:
        for box in unit:
            diff = set(values[box]).difference(''.join([values[key]
                                            for key in (set(unit) - {box})]))
            if len(diff) == 1:
                _values = assign_value(_values, box, list(diff)[0])
    return _values


def reduce_puzzle(values):
    while True:
        solved_values_before = solved_values(values)
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = solved_values(values)
        if len([box for box, value in values.items() if len(value) == 0]) > 0:
            return False
        if len(solved_values_before) == len(solved_values_after):
            return values


def search(values):
    values = values.copy()
    values = reduce_puzzle(values)
    if not values:
        return False
    if solved(values):
        return values
    box_to_be_searched = pick_box_with_least_values_larger_than_one(values)
    for value in values[box_to_be_searched]:
        new_values = values.copy()
        new_values[box_to_be_searched] = value
        result = search(new_values)
        if result:
            return result


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
