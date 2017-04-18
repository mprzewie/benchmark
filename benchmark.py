from funlogger import Funlogger
from math import log, factorial
from util import NotEnoughMeasurePointsException, TimeoutException, with_timeout
from timeit import default_timer as timer
from random import randrange
import numpy as np


class Benchmark:
    def __init__(self, initializer, to_measure, cleanup=lambda *args: None, log_name="", measurement_timeout=30):
        self.logger = Funlogger(log_name=log_name)
        self.measurement_timeout = measurement_timeout
        self.measurements = []
        self.initializer = initializer
        self.to_measure = to_measure
        self.cleanup = cleanup

    def execution_time(self, size):
        to_measure_args = self.initializer(size)
        start = timer()
        if type(to_measure_args) is list:
            result = self.to_measure(to_measure_args)
        else:
            result = self.to_measure(*to_measure_args)
        end = timer()
        self.cleanup(result)
        return end - start

    def make_measurements(self, sizes):
        @with_timeout(self.measurement_timeout)
        @self.logger.log_fun
        def measures(s):
            return list(map(lambda size: (size, self.execution_time(size)), s))

        try:
            self.measurements.extend(measures(sizes))
        except TimeoutException:
            print("The maximal measurement time (" + str(self.measurement_timeout) + ") has been exceeded!")
        return self.measurements

    def make_random_measurements(self, count=256, min=1, max=100):
        sizes = [randrange(min, max) for _ in range(count)]
        return self.make_measurements(sizes)


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
        if len(measurements) < 2:
            raise NotEnoughMeasurePointsException(len(measurements))
        vars = []
        for compl in self.complexities:
            diffs = list(map(lambda m: (m[1] / self.complexities[compl](m[0])), measurements))
            vars.append((compl, np.mean(diffs), np.var(diffs)))
        vars.sort(key=lambda x: x[2])
        return vars[0]
