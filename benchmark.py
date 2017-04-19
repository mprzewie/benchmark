from funlogger import Funlogger
from math import log, factorial
from util import NotEnoughMeasurePointsException, TimeoutException, with_timeout
from timeit import default_timer as timer
from random import randrange
import numpy as np
import matplotlib.pyplot as plt


class Benchmark:
    def __init__(self, initializer, to_measure, cleanup=lambda *args: None, log_name="", measurement_timeout=30):
        self.logger = Funlogger(log_name=log_name)
        self.measurement_timeout = measurement_timeout
        self.measurements = []
        self.initializer = initializer
        self.to_measure = to_measure
        self.cleanup = cleanup
        self.predicted_complexity_name = None
        self.predicted_complexity = None
        self.predicted_complexity_const = None

    def execution_time(self, size):
        # TODO - use a context manager?
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
        def measures(s):
            return list(map(lambda size: (size, self.execution_time(size)), s))

        try:
            self.measurements.extend(measures(sizes))
        except TimeoutException as ex:
            self.logger.log("The maximal measurement time (" + ex.timeout_to_str() + ") has been exceeded!")
        return self.measurements

    def make_random_measurements(self, count=256, min=1, max=100):
        sizes = [randrange(min, max) for _ in range(count)]
        return self.make_measurements(sizes)

    def predict_complexity(self):
        @self.logger.log_fun
        def predict():
            return ComplexMatcher().match(self.measurements)

        self.logger.log("Predicting complexity of " + self.to_measure.__name__)
        self.predicted_complexity_name, self.predicted_complexity, self.predicted_complexity_const, _ = predict()
        return self.predicted_complexity_name

    def time_for_size(self, size):
        return self.predicted_complexity(size) * self.predicted_complexity_const

    def size_for_time(self, time):
        def bin_search(min_n, max_n):
            if max_n - min_n < 1:
                return max_n
            vertex = (min_n + max_n) / 2
            time_for_vertex = self.time_for_size(vertex)
            if time_for_vertex < time:
                return bin_search(vertex, max_n)
            else:
                return bin_search(min_n, vertex)

        max_size = 1
        while self.time_for_size(max_size) < time:
            max_size *= 2
        return bin_search(max_size / 2, max_size)

    def plot_measurements(self):
        sizes = list(map(lambda x: x[0], self.measurements))
        times = list(map(lambda x: x[1], self.measurements))
        plt.plot(sizes, times, 'ro')
        plt.show()


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
            diffs = list(map(lambda m: (log(m[1], 10) - log(self.complexities[compl](m[0]), 10)), measurements))
            vars.append((compl, self.complexities[compl], 10 ** np.mean(diffs), np.var(diffs)))
        vars.sort(key=lambda x: x[3])
        return vars[0]
