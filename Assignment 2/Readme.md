

<br>

## Implementation

We have used the DPLL algorithm to solve the SAT problem. The algorithm is as follows:

> SAT (Formula F, Interpreation I):
> 1.    if ( I ⇒ F ) return true
> 2.    if ( I ⇒ ¬F ) return false
> 3.    F,I = unit_propagation(F,I)
> 4.    if I is inconsistent return false
> 5.    F,I = pure_literal(F,I)
> 6.    if F = ∅ return true
> 7.    choose the best xi that I does not assign
> 8.    if sat(F, I ∪ { xi=true }) return true
> 9.    if sat(F, I ∪ { xi=false }) return true
> 10.   return false.

<br>

For implementation, we did some changes to the algorithm. Our program runs like this:
1. Before calling sat(), we first find the best xi. we first assign the xi to true. If no model is found, then we assign xi to false and call sat() again.
2. Now on execution of sat(), it calls simplify_and_check() function. The function simplifies the formula F by using xi. If xi is present in a clause, It removes that clause from F. Otherwise, It removes the literal from the clause. After that, it checks if F is satisfied now or not.
3. Next sat() calls the unit_propagation() function. The function checks if F has a clause with one literal or not. If yes, then it assigns the literal to I and calls simplify_and_check(). Then it checks again if F still contains a unit clause.
4. Next sat() calls the pure_literal() function. The function checks if there is a literal that has only one form, only xi or only ~xi. If yes, then it assigns the literal to I and calls simplify_and_check(). Then it checks again if F still contains a pure literal.
5. Finally, it finds the best xi that I does not assign. It then sets xi to true and calls sat() again. If no model is found, then it sets xi to false and calls sat() again. If no model is found, then it returns false.

> To find the best xi, we have used the following heuristic:
>
> Choose the variable xi that maximizes 1024*n*p + n + p, where n is the number of clauses containing xi and p is the number of clauses containing ~xi.

<br>

## Assumptions

1. The program can only find the cnf file if absolute path is given.
2. We have assumed that the cnf file has an empty line at the end.

<br>

## Limitations

1. The SAT solver works only for the propositional logic set up in CNF form.