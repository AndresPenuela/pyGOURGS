# This code is derived from the DEAP project
# https://github.com/DEAP/deap/blob/master/examples/gp/parity.py

import random
import operator
import numpy
import sys,os
sys.path.append(os.path.join('..', 'pyGOURGS'))
import pyGOURGS as pg

# Initialize Parity problem input and output matrices
PARITY_FANIN_M = 6
PARITY_SIZE_M = 2**PARITY_FANIN_M

inputs = [None] * PARITY_SIZE_M
outputs = [None] * PARITY_SIZE_M

for i in range(PARITY_SIZE_M):
    inputs[i] = [None] * PARITY_FANIN_M
    value = i
    dividor = PARITY_SIZE_M
    parity = 1
    for j in range(PARITY_FANIN_M):
        dividor /= 2
        if value >= dividor:
            inputs[i][j] = 1
            parity = int(not parity)
            value -= dividor
        else:
            inputs[i][j] = 0
    outputs[i] = parity

pset = pg.PrimitiveSet()
pset.add_operator("operator.and_", 2)
pset.add_operator("operator.or_", 2)
pset.add_operator("operator.xor", 2)
pset.add_operator("operator.not_", 1)
for i in range(0,PARITY_FANIN_M):
    pset.add_variable("BOOL"+str(i))
enum = pg.Enumerator(pset)

def compile(expr, pset):
    """
    Compiles the `expr` expression

    Parameters
    ----------

    expr: a string of Python code or any object that when
             converted into string produced a valid Python code
             expression.                 

    pset: Primitive set against which the expression is compiled
        
    Returns
    -------
        a function if the primitive set has 1 or more arguments,
         or return the results produced by evaluating the tree
    """    
    code = str(expr)
    if len(pset._variables) > 0:
        args = ",".join(arg for arg in pset._variables)
        code = "lambda {args}: {code}".format(args=args, code=code)
    try:
        return eval(code)
    except MemoryError:
        _, _, traceback = sys.exc_info()
        raise MemoryError("Tree is too long.", traceback)

def evalParity(individual, pset):
    func = compile(individual,pset)
    return sum(func(*in_) == out for in_, out in zip(inputs, outputs)),


if __name__ == "__main__":
    args = sys.argv[1:]
    output_db = args[0]
    n_iters = int(args[1])
    max_score = 0
    iter = 0
    for soln in enum.uniform_random_global_search(10000, n_iters):
        iter = iter + 1 
        score = evalParity(soln, pset)[0]
        pg.save_result_to_db(output_db, score, soln)
        if score > max_score:
            max_score = score
        if iter % 10 == 0:
            print(score, max_score, iter)
