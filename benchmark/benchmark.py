from math import log, factorial
from random import randrange
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np

from benchmark.funlogger import Funlogger
from benchmark.util import NotEnoughMeasurePointsException, TimeoutException, with_timeout


class Benchmark:
    def __init__(self, initializer, to_measure, cleanup=lambda *args: None, log_name="", measurement_timeout=30):
        self.logger = Funlogger(log_name=log_name)
        self.measurement_timeout = measurement_timeout
        self.measurements = []
        self.initializer = initializer
        self.to_measure = to_measure
        self.cleanup = cleanup
        self.predicted_complexity_name = None
        self.predicted_complexity_fun = None
        self.predicted_complexity_const = None
        self.predicted_complexity_certainty = None

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
        def make_measurements_():
            made = 0
            for size in sizes:
                self.measurements.append((size, self.execution_time(size)))
                made += 1

        try:
            make_measurements_()
        except TimeoutException as ex:
            self.logger.log("The maximal measurement time (" + ex.timeout_to_str() + ") has been exceeded!\nNot all "
                                                                                     "measurements have been made.")
        return self.measurements

    def make_random_measurements(self, count=256, min=1, max=100):
        sizes = [randrange(min, max) for _ in range(count)]
        return self.make_measurements(sizes)

    def predict_complexity(self):
        @self.logger.log_fun
        def predict_complexity_():
            self.predicted_complexity_name, self.predicted_complexity_fun, self.predicted_complexity_const, \
            self.predicted_complexity_certainty = ComplexMatcher().match(self.measurements)
            return self.predicted_complexity_name

        try:
            self.logger.log("Predict complexity of " + self.to_measure.__name__)

            return predict_complexity_()
        except NotEnoughMeasurePointsException:
            self.logger.log("Failure! No measurements of " + self.to_measure.__name__)
            return None

    def time_for_size(self, size, to_log=True):
        result = self.predicted_complexity_fun(size) * self.predicted_complexity_const
        if to_log:
            @self.logger.log_fun
            def time_for_size_(_):
                return result

            return time_for_size_(size)

        else:
            return result

    def size_for_time(self, time, to_log=True):
        def bin_search(min_n, max_n):
            if max_n - min_n < 1:
                return max_n
            vertex = (min_n + max_n) / 2
            time_for_vertex = self.time_for_size(vertex, to_log=False)
            if time_for_vertex < time:
                return bin_search(vertex, max_n)
            else:
                return bin_search(min_n, vertex)

        max_size = 1
        while self.time_for_size(max_size, to_log=False) < time:
            max_size *= 2
        result = bin_search(max_size / 2, max_size)

        @self.logger.log_fun
        def size_for_time_(_):
            return result

        if to_log:
            return size_for_time_(time)
        else:
            return result

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

    """The result tuple is:
    (name of the complexity,
    the actual complexity function object,
    the constant that the function needs to be multiplied by when calculating performance,
    certainty of measurement between 0 and 1
    )"""

    def match(self, measurements):
        if len(measurements) < 2:
            raise NotEnoughMeasurePointsException(len(measurements))
        variances = []
        for compl in self.complexities:
            divisions = list(map(lambda m: (log(m[1], 10) - log(self.complexities[compl](m[0]), 10)), measurements))
            variances.append((compl, 10 ** np.mean(divisions), np.var(divisions)))
        variances.sort(key=lambda x: x[2])

        best_name = variances[0][0]
        best_const = variances[0][1]
        best_variance = variances[0][2]
        best_fun = self.complexities[best_name]
        certainty = 1 / (best_variance * sum(list(map(lambda v: 1 / v[2], variances))))
        return best_name, best_fun, best_const, certainty
