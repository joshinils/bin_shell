#!/usr/bin/env python3

from random import shuffle
from ortools.linear_solver import pywraplp
import sys
import os
from pathlib import Path


def create_data_model(folder: str):
    dirlist = os.listdir(folder)
    weights = []
    shuffle(dirlist)
    for file in dirlist:
        size = os.path.getsize(f"{folder}{os.sep}{file}") / 1073741824
        print(file, size)
        weights.append(size)

    data = {}
    # weights = [48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30]
    data['weights'] = weights
    data['items'] = list(range(len(weights)))
    data['bins'] = data['items']
    data['bin_capacity'] = 150
    data["names"] = dirlist
    return data


def main():
    folder = sys.argv[1]

    data = create_data_model(folder)

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    if not solver:
        return

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for filename, i in zip(data['names'], data['items']):
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, filename)

    # y[j] = 1 if bin j is used.
    y = {}
    for j in data['bins']:
        y[j] = solver.IntVar(0, 1, 'y[%i]' % j)

    # Constraints
    # Each item must be in exactly one bin.
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in data['bins']:
        solver.Add(
            sum(x[(i, j)] * data['weights'][i] for i in data['items']) <= y[j] *
            data['bin_capacity'])

    # Objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in data['bins']]))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        num_bins = 0.
        for j in data['bins']:
            if y[j].solution_value() == 1:
                bin_items = []
                bin_weight = 0
                for filename, i in zip(data["names"], data['items']):
                    if x[i, j].solution_value() > 0:
                        bin_items.append([filename, i])
                        bin_weight += data['weights'][i]
                if bin_weight > 0:
                    num_bins += 1
                    print('Bin number', j)
                    print('  Items packed:', bin_items)
                    print('  Total weight:', bin_weight)
                    print()
                    # move files to bin
                    bin_name = f"bin_{j:03}"
                    Path(f"{folder}{os.sep}{bin_name}").mkdir(exist_ok=True)
                    for filename, _ in bin_items:
                        os.rename(f"{folder}{os.sep}{filename}", f"{folder}{os.sep}{bin_name}{os.sep}{filename}")

        print()
        print('Number of bins used:', num_bins)
        print('Time = ', solver.WallTime(), ' milliseconds')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
