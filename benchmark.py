from funlogger import Funlogger
from math import log, factorial
import numpy as np


class Benchmark:
    def __init__(self, initializer, to_measure, cleanup=lambda *args: print(args), log_name=""):
        self.logger = Funlogger(log_name=log_name)

    def execution_time(self, size):
        pass

    def max_size(self, time):
        pass


class ComplexMatcher:
    complexities = {
        '1': lambda n: 1,
        'log(n)': lambda n: log(n + 1),
        'n': lambda n: n,
        'n log(n)': lambda n: n * log(n + 1),
        'n^2': lambda n: n ** 2,
        'n^3': lambda n: n ** 3,
        'n^4': lambda n: n ** 4,
        'n^5': lambda n: n ** 5,
        'n^6': lambda n: n ** 6,
        '2^n': lambda n: 2 ** n,
        'n!': lambda n: factorial(n)
    }

    def match(self, measurements):
        vars = []
        for compl in self.complexities:
            diffs = list(map(lambda m: (m[1] / self.complexities[compl](m[0])), measurements))
            vars.append((compl, np.mean(diffs), np.var(diffs)))
        vars.sort(key=lambda x: x[2])
        return vars[0]


measurements = [[1, 2], [2, 4], [3, 6], [4, 8]]
matcher = ComplexMatcher()
print(matcher.match(measurements))
