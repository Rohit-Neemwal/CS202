import argparse
import csv
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Solves sudoku pair puzzles.')
    parser.add_argument('-k', '--k', type=int, default=3, help='k value for k-sudoku')
    parser.add_argument('-p', '--path', type=str, default="TestCases/test_case3.csv",
                        help='Path to sudoku puzzle csv file.')
    parser.add_argument('-d', '--use_diag_constraints', type=int, default=1,
                        help='Use diagonal constraints (1) or not (0).')
    parser.add_argument('-o', '--outputformat', type=int, default=0,
                        help='0: output numbers with lines separating them, 1: output only numbers'
                        "2: output result in a csv file named 'sudoku_soln.csv'")
    return parser.parse_args()


def read_csv(path):
    """Reads and returns data from csv file"""
    rows = []
    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            rows.append(row)
    return rows


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


def get_assumptions(k, rows, soln, start=0):
    """Fix the positions that have given values"""
    assumptions = []
    for i in range(k*k):
        for j in range(k*k):
            if rows[i][j] != '0':
                assumptions.append(start + i*(k**4) + j*(k**2) + int(rows[i][j]))
                soln[i][j] = int(rows[i][j])
    return assumptions


def print_soln(k, soln, format=0):
    """Prints the final solution"""
    if format != 2:
        for i in range(k*k):
            for j in range(k*k):
                print(soln[i][j], end=" ")
                if not format and (j+1) % k == 0 and j != k*k-1:
                    print("|", end=" ")
            print()
            if not format and (i+1) % k == 0 and i != k*k-1:
                rng = 2*k*k+2*k-3 + (k>3)*(k*k)
                for j in range(rng):
                    print('-', end="")
                print()
    else:
        with open('sudoku_soln.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerows(soln)


args = parse_args()
k = args.k
solver = Solver()

# list to store solved sudoku - start with 0s
sol1 = [[0 for _ in range(k*k)] for _ in range(k*k)]
sol2 = [[0 for _ in range(k*k)] for _ in range(k*k)]

# add constraints
add_value_constraints(k, solver)
add_value_constraints(k, solver, start=k**6)
add_horl_and_vert_constraints(k, solver)
add_horl_and_vert_constraints(k, solver, start=k**6)
add_block_constraints(k, solver)
add_block_constraints(k, solver, start=k**6)
if args.use_diag_constraints:
    add_diag_constraints(k, solver)
    add_diag_constraints(k, solver, start=k**6)
add_index_pair_constraints(k, solver)

# get assumptions by reading from given file
rows = read_csv(args.path)
assumptions1 = get_assumptions(k, rows[:k*k], sol1)
assumptions2 = get_assumptions(k, rows[k*k:], sol2, start=(k**6))

# solve the encoded problem
if solver.solve(assumptions=assumptions1 + assumptions2):
    # get the value of each box
    for val in solver.get_model():
        if val > 0:
            a = int((val-1) / (k**6))     # 0 for sud1 and 1 for sud2
            i = int((val-1) % (k**6) / (k**4))
            j = int((val-1) % (k**6) % (k**4) / (k**2))
            m = int((val-1) % (k**6) % (k**4) % (k**2) + 1)
            if a:
                if k > 3 and m < 10:
                    sol2[i][j] = ' ' + str(m)
                else:
                    sol2[i][j] = str(m)
            else:
                if k > 3 and m < 10:
                    sol1[i][j] = ' ' + str(m)
                else:
                    sol1[i][j] = str(m)
    if args.outputformat == 2:
        open('sudoku_soln.csv', 'w').close()  # clear/create the file first
    print_soln(k, sol1, format=args.outputformat)
    print()
    print_soln(k, sol2, format=args.outputformat)
else:
    print("None")

# delete the solver after use
solver.delete()