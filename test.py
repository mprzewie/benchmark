from random import randrange

from benchmark import Benchmark


def rand_list(size, min=0, max=100):
    return [randrange(min, max) for _ in range(size)], "kierwa"


def my_sorted(list, name):
    return sorted(list), name


b = Benchmark(rand_list, my_sorted, log_name="", measurement_timeout=5)

b.make_random_measurements(count=5)
print(b.measurements)
