# Sudoku Pair: Solving & Generation
<br>

## Implementation

### Setting up Variables

First thing to do for encoding problems in propositional logic is to define variables. We define a variable by x<sub>a,i,j,m</sub>, which represents the boolean value of the cell at index *i* (0 to k<sup>2</sup>), *j* (0 to k<sup>2</sup>) of *ath* sudoku (0 or 1) having a number *m* (1 to k<sup>2</sup>).  Since PySAT uses single integer for a boolean variable, we use following function to convert a variable into an integer:
<center>f(x<sub>a,i,j,m</sub>) = a*k<sup>6</sup> + i*k<sup>4</sup> + j*k<sup>2</sup> + m</center>
Using these variables, we can apply the constraints to create the encoding for the problem.

<br>

### Applying Constraints

We have applied constraints for the k-sudoku pair by using **Cardnality Constraints** (CardEnc) provided by PySAT. Given below is the list of applied constraints -

1. Value Constraints - each cell of the sudoku should have exactly one value - for each a,i,j, varying m, summation (x<sub>a,i,j,m</sub>) = 1
2. Horizontal & Vertical Constraints - each row or column should have numbers ranging from 1 to k<sup>2</sup> exactly once - for a row, for each a,i,m, varying j, summation (x<sub>a,i,j,m</sub>) = 1 and for a column, for each a,j,m, varying i, summation (x<sub>a,i,j,m</sub>) = 1
3. Block Constraints - each block should have numbers ranging from 1 to k<sup>2</sup> exactly once - for a m, varying each cell in a block, summation (x<sub>a,i,j,m</sub>) = 1
4. Diagonal Constraints [optional] - both overall diagonals should have numbers ranging from 1 to k<sup>2</sup> exactly once - for a m, varying each cell in a diagonal, summation (x<sub>a,i,j,m</sub>) = 1

> Each of the above constraints are implemented using equal cardinality constraint with bound = 1 and pairwise encoding.

5. Index-Pair Constraints - for each cell, x<sub>0,i,j,m</sub> != x<sub>1,i,j,m</sub> - This was implemented using the clause (~a V ~b)

<br>

### Sudoku Pair Solver

The above constraints are applied to the solver. Now the program scans for filled entries and adds them in the assumptions list. This list is then given to the solver for solving the encoded problem.

```python
usage: sudoku_pair_solver.py [-h] [-k K] [-p PATH] [-d USE_DIAG_CONSTRAINTS] [-o OUTPUTFORMAT]

Solves sudoku pair puzzles.

optional arguments:
  -h, --help            show this help message and exit
  -k K, --k K           k value for k-sudoku
  -p PATH, --path PATH  Path to sudoku puzzle csv file.
  -d USE_DIAG_CONSTRAINTS, --use_diag_constraints USE_DIAG_CONSTRAINTS
                        Use diagonal constraints (1) or not (0).
  -o OUTPUTFORMAT, --outputformat OUTPUTFORMAT
                        0: output numbers with lines separating them, 
                        1: output only numbers separated by space,
                        2: output result in a csv file named 'sudoku_soln.csv'
```

### Sudoku Pair Generator

A SAT Solver is created first and the above constraints are applied to it. Now, the program randomly selects some positions and fills a random number in them (such that the number lies between 1 to k<sup>2</sup>). After that the solver solves the puzzle and gives a solution. It then creates a list of indices that have non-zero number (i.e. all indices) and shuffles it. Then for each index in this list, it removes the number and apply a constraint such that the number that was already in that cell can not be used for that cell. If a solution is found, then we don't remove that index, otherwise we remove it. After all the iterations, we get a sudoku pair puzzle that is maximal (has the largest number of holes possible) and has a unique solution. 


```python
usage: sudoku_pair_generator.py [-h] [-k K] [-d USE_DIAG_CONSTRAINTS] [-p PATH] [-s SOLNPATH]

Generates sudoku pair puzzles.

optional arguments:
  -h, --help            show this help message and exit
  -k K, --k K           k value for k-sudoku
  -d USE_DIAG_CONSTRAINTS, --use_diag_constraints USE_DIAG_CONSTRAINTS
                        Use diagonal constraints (1) or not (0).
  -p PATH, --path PATH  Path to store new sudoku puzzle csv file.
  -s SOLNPATH, --solnpath SOLNPATH
                        Path to store solution to sudoku puzzle csv file.
```

<br>

## Assumptions

1. The following packages should be installed before usage -
* pysat==3.0.1
* python_sat==0.1.7.dev15


2. In case of generating a puzzle in a csv file or writing a solution to a csv file, we assume that the folders present in the path provided are already present. If not, program will give a "no such file or directory" error.

<br>

## Limitations

1. It takes lot of time for generating a k-sudoku pair puzzle for k >= 5