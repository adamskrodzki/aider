#!/usr/bin/env python3
import json
import os
import sys

def read_results(path):
    with open(path, 'r') as file:
        return json.load(file)

def compare_benchmarks(benchmark1, benchmark2):
    tests1 = set(os.listdir(benchmark1))
    tests2 = set(os.listdir(benchmark2))

    if tests1 != tests2:
        raise ValueError("Benchmark directories do not have the same set of tests.")

    for test in sorted(tests1):
        result1_path = os.path.join(benchmark1, test, '.aider.results.json')
        result2_path = os.path.join(benchmark2, test, '.aider.results.json')

        result1_data = read_results(result1_path)
        result2_data = read_results(result2_path)

        if 'test_outcomes' not in result1_data or 'test_outcomes' not in result2_data:
            print(f"Warning: 'test_outcomes' key not found in the results for test '{test}'.")
            continue

        result1 = result1_data['test_outcomes']
        result2 = result2_data['test_outcomes']

        for outcome1, outcome2 in zip(result1, result2):
            if outcome1 and not outcome2:
                print(f"{test}: {benchmark1}")
                break
            elif outcome2 and not outcome1:
                print(f"{test}: {benchmark2}")
                break

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: diff.py /path/to/benchmark1 /path/to/benchmark2")
        sys.exit(1)

    benchmark1, benchmark2 = sys.argv[1], sys.argv[2]
    compare_benchmarks(benchmark1, benchmark2)
