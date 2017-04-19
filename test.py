from random import randrange
import time
from decimal import Decimal

from benchmark import Benchmark


def rand_list(size, min=0, max=100):
    return [randrange(min, max) for _ in range(size)], "kierwa"


def my_sorted(list, name):
    # time.sleep(6)
    return sorted(list), name


log_name=""

b = Benchmark(rand_list, my_sorted, log_name=log_name, measurement_timeout=100)

b.make_random_measurements(count=50, max=10000)
x=b.predict_complexity()
# y=b.predicted_complexity(8)
# print(y)
time=b.time_for_size(1536)
print(time)
print(b.size_for_time(time))
b.plot_measurements()