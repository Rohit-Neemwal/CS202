import argparse
import csv
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
import random


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generates sudoku pair puzzles.')
    parser.add_argument('-k', '--k', type=int, default=3, help='k value for k-sudoku')
    parser.add_argument('-d', '--use_diag_constraints', type=int, default=0,
                        help='Use diagonal constraints (1) or not (0).')
    parser.add_argument('-p', '--path', type=str, default="TestCases/test_case.csv",
                        help='Path to store new sudoku puzzle csv file.')
    parser.add_argument('-s', '--solnpath', type=str, default="TestCases/sol_test_case.csv",
                        help='Path to store solution to sudoku puzzle csv file.')
    return parser.parse_args()


def add_value_constraints(k, solver, start=0):
    """Adds constraints that each box should have exactly one value"""
    for i in range(k*k):
        for j in range(k*k):
            box_lits = []
            for m in range(1, k*k+1):
                box_lits.append(start + i*(k**4) + j*(k**2) + m)
            cnf = CardEnc.equals(lits=box_lits, bound=1, encoding=EncType.pairwise)
            solver.append_formula(cnf)


def add_horl_and_vert_constraints(k, solver, start=0):
    """Adds horizontal and vertical constraints"""
    for i in range(k*k):
        for m in range(1,k*k+1):
            hor_lits, ver_lits = [], []
            for j in range(k*k):
                hor_lits.append(start + i*(k**4) + j*(k**2) + m)
                ver_lits.append(start + j*(k**4) + i*(k**2) + m)

            cnf1 = CardEnc.equals(lits=hor_lits, bound=1, encoding=EncType.pairwise)
            cnf2 = CardEnc.equals(lits=ver_lits, bound=1, encoding=EncType.pairwise)
            solver.append_formula(cnf1)
            solver.append_formula(cnf2)


def add_block_constraints(k, solver, start=0):
    """Adds block constraints"""
    for I in range(k):
        for J in range(k):
            for m in range(1,k*k+1):
                block_lits = []
                for i in range(k):
                    for j in range(k):
                        block_lits.append(start + (I*k+i)*(k**4) + (J*k+j)*(k**2) + m)

                cnf = CardEnc.equals(lits=block_lits, bound=1, encoding=EncType.pairwise)
                solver.append_formula(cnf)


def add_diag_constraints(k, solver, start=0):
    """Adds diagonal constraints"""
    for m in range(1,k*k+1):
        diag_lits_1 = []
        diag_lits_2 = []
        for i in range(k*k):
            diag_lits_1.append(start + i*(k**4) + i*(k**2) + m)
            diag_lits_2.append(start + i*(k**4) + (k*k-1-i)*(k**2) + m)
        cnf1 = CardEnc.equals(lits=diag_lits_1, bound=1, encoding=EncType.pairwise)
        cnf2 = CardEnc.equals(lits=diag_lits_2, bound=1, encoding=EncType.pairwise)
        solver.append_formula(cnf1)
        solver.append_formula(cnf2)


def add_index_pair_constraints(k, solver):
    """Adds index-pair constraints"""
    for i in range(k*k):
        for j in range(k*k):
            for m in range(1,k*k+1):
                clause = [-(i*(k**4) + j*(k**2) + m), -((k**6) + i*(k**4) + j*(k**2) + m)]
                solver.add_clause(clause)


def add_constraints(k, solver, use_diag):
    """Adds all constraints"""
    add_value_constraints(k, solver)
    add_value_constraints(k, solver, start=k**6)
    add_horl_and_vert_constraints(k, solver)
    add_horl_and_vert_constraints(k, solver, start=k**6)
    add_block_constraints(k, solver)
    add_block_constraints(k, solver, start=k**6)
    if use_diag:
        add_diag_constraints(k, solver)
        add_diag_constraints(k, solver, start=k**6)
    add_index_pair_constraints(k, solver)


def fill_random(k, puzzle):
    """Give some random positions a random value"""
    num_random_values = random.randint(k*k, 2*k*k)
    rx = [random.randint(0, 2*k*k-1) for _ in range(num_random_values)]
    ry = [random.randint(0, k*k-1) for _ in range(num_random_values)]
    rval = [random.randint(1, k*k) for _ in range(num_random_values)]
    assumptions = []
    for i in range(num_random_values):
        puzzle[rx[i]][ry[i]] = rval[i]
        if rx[i] > k*k-1:
            x, a = rx[i] - k*k, 1
        else:
            x, a = rx[i], 0
        assumptions.append(a*(k**6) + x*(k**4) + ry[i]*(k**2) + rval[i])
    return assumptions


def decrypt_model_values(k, model, puzzle):
    """Get the value of each box"""
    for val in model:
        if val > 0:
            a = int((val-1) / (k**6))
            i = int((val-1) % (k**6) / (k**4))
            j = int((val-1) % (k**6) % (k**4) / (k**2))
            m = int((val-1) % (k**6) % (k**4) % (k**2) + 1)
            puzzle[i + a*k*k][j] = m


def get_assumptions(k, puzzle):
    """Get the assumptions for the puzzle"""
    assumptions = []
    for i in range(2*k*k):
        for j in range(k*k):
            if puzzle[i][j] != 0:
                if i > k*k-1:
                    x, a = i - k*k, 1
                else:
                    x, a = i, 0
                assumptions.append(a*(k**6) + x*(k**4) + j*(k**2) + puzzle[i][j])
    return assumptions


def check_uniqueness(k, puzzle, solver, x, y, val):
    assumptions = get_assumptions(k, puzzle)
    if x > k*k-1:
        x, a = x - k*k, 1
    else:
        a = 0
    assumptions.append(-(a*(k**6) + x*(k**4) + y*(k**2) + val))
    if solver.solve(assumptions=assumptions):
        return False
    return True


def save_puzzle(path, puzzle):
    """Write the sudoku puzzle to a csv file"""
    with open(path, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(puzzle)



# parse arguments and create a solver
args = parse_args()
k = args.k
solver = Solver()

# list to store solved sudoku - start with 0s
puzzle = [[0 for _ in range(k*k)] for _ in range(2*k*k)]

# add constraints
add_constraints(k, solver, args.use_diag_constraints)

while(True):
    puzzle = [[0 for _ in range(k*k)] for _ in range(2*k*k)]
    # give some random positions a random value
    assumptions = fill_random(k, puzzle)
    # get a solved puzzle
    if solver.solve(assumptions = assumptions):
        puzzle_generated = True
        decrypt_model_values(k, solver.get_model(), puzzle)
        break

# save solution to puzzle
save_puzzle(args.solnpath, puzzle)

# store ids of non-empty
non_empty_cells = []
for i in range(2*k*k):
    for j in range(k*k):
        if puzzle[i][j] != 0:
            non_empty_cells.append((i, j))

# remove values from non-empty cells one by one until no unique soln exists
random.shuffle(non_empty_cells)
for x,y in non_empty_cells:
    val = puzzle[x][y]
    puzzle[x][y] = 0
    if not check_uniqueness(k, puzzle, solver, x, y, val):
        puzzle[x][y] = val

# write the puzzle to a csv file
save_puzzle(args.path, puzzle)

# delete the solver after use
solver.delete()