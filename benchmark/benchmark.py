from math import log, factorial
from random import randrange
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from benchmark.funlogger import Funlogger
from benchmark.util import NotEnoughMeasurePointsException, TimeoutException, with_timeout, contextify


class Benchmark:
    def __init__(self, context_manager, to_measure, log_name=None, measurement_timeout=30):
        self.logger = Funlogger(log_name=log_name)
        self.measurement_timeout = measurement_timeout
        self.measurements = []
        self.context_manager = contextify(context_manager)
        self.to_measure = to_measure
        self.predicted_complexity_name = None
        self.predicted_complexity_fun = None
        self.predicted_complexity_const = None
        self.predicted_complexity_certainty = None

    def execution_time(self, size):
        with self.context_manager(size) as to_measure_args:
            start = timer()
            if type(to_measure_args) is list:
                self.to_measure(to_measure_args)
            else:
                self.to_measure(*to_measure_args)
            end = timer()
        return end - start

    def make_measurements(self, sizes):

        @with_timeout(self.measurement_timeout)
        def make_measurements_():
            for size in sizes:
                self.measurements.append((size, self.execution_time(size)))

        try:
            sizes = sorted(sizes)
            make_measurements_()
            return self.measurements
        except TimeoutException as ex:
            self.logger.log("The maximal measurement time (" + ex.timeout_to_str() + ") has been exceeded!\n"
                                                                                     "Made only " +
                            str(len(self.measurements)) + " measurements")

    def make_random_measurements(self, count=256, min_s=1, max_s=100):
        sizes = [randrange(min_s, max_s) for _ in range(count)]
        return self.make_measurements(sizes)

    def predict_complexity(self):
        @self.logger.log_fun
        def predict_complexity_(_):
            self.predicted_complexity_name, self.predicted_complexity_fun, self.predicted_complexity_const, \
              self.predicted_complexity_certainty = ComplexMatcher().match(self.measurements)
            return "O( " + self.predicted_complexity_name + " )"

        try:
            return predict_complexity_(self.to_measure.__name__)
        except NotEnoughMeasurePointsException:
            self.logger.log("Failure! Only one or no measurements of " + self.to_measure.__name__)
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
        predicted_times = list(map(lambda s: self.time_for_size(s, to_log=False), sizes))
        plt.plot(sizes, times, 'ro', markersize=2)
        plt.plot(sizes, predicted_times, 'b')
        red_data = patches.Patch(color='red', label='Measured time')
        blue_data = patches.Patch(color='blue', label='Predicted time')
        plt.legend(handles=[red_data, blue_data])
        plt.xlabel('problem size')
        plt.ylabel('time of solution [s]')
        plt.title('Function: ' + self.to_measure.__name__ +
                  '\nPredicted complexity: O(' +
                  self.predicted_complexity_name + '), ' +
                  'certainty of prediction: ' +
                  "{0:.2f}".format(100 * self.predicted_complexity_certainty) + '%')
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
        for complexity in self.complexities:
            divisions = list(
                map(lambda m: (log(m[1], 10) - log(self.complexities[complexity](m[0]), 10)),
                    measurements))
            variances.append((complexity, 10 ** np.mean(divisions), np.var(divisions)))
        variances.sort(key=lambda x: x[2])

        best_name = variances[0][0]
        best_const = variances[0][1]
        best_variance = variances[0][2]
        best_fun = self.complexities[best_name]
        certainty = 1 / (best_variance * sum(list(map(lambda v: 1 / v[2], variances))))
        return best_name, best_fun, best_const, certainty
