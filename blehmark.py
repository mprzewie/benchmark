import argparse
import importlib
from benchmark.benchmark import Benchmark

parser = argparse.ArgumentParser(description=
                                 'An ugly script for measuring complexities. Usage of Benchmark class recommended.')

parser.add_argument('-im', dest='initializer_module_name', type=str, default='builtins',
                    help="Name of the module (as if used in 'import') in which the "
                         "initializing context manager (or function) can be found")
parser.add_argument('-fm', dest='fun_module_name', type=str, default='builtins',
                    help="Name of the module (as if used in 'import') in which the "
                         "measured function can be found")
parser.add_argument('-i', dest='context_name', type=str,
                    help="Name of the initializing context manager (or function)")
parser.add_argument('-f', dest='fun_name', type=str,
                    help="Name of the measured function")
parser.add_argument('-l', dest='log_name', type=str, default=None,
                    help="Name of the file with logs. If unspecified, the output will be logged into "
                         "standard output")
parser.add_argument('-t', dest='timeout', type=int, default=30,
                    help="Timeout of measurements (in seconds)")
parser.add_argument('-c', dest='measure_count', type=int, default=256,
                    help="Count of measurements to be made")
parser.add_argument('-mins', dest='min_s', type=int, default=1,
                    help="Minimal size of the problem to be measured")
parser.add_argument('-maxs', dest='max_s',type=int, default=1000,
                    help="Maximal size of the problem to be measured")

args = parser.parse_args()

# Seriously, you could do a lot more if you wrote your own script and used Benchmarker's functions

init_src_module = importlib.import_module(args.initializer_module_name)
fun_src_module= importlib.import_module(args.fun_module_name)

context_manager = getattr(init_src_module, args.context_name)
to_measure = getattr(fun_src_module, args.fun_name)

# What a waste of a good module

benchmarker = Benchmark(context_manager=context_manager,
                        to_measure=to_measure,
                        log_name=args.log_name,
                        measurement_timeout=args.timeout)

# You probably use Windows, too - don't you?

benchmarker.make_random_measurements(count=args.measure_count,
                                     min_s=args.min_s,
                                     max_s=args.max_s)
benchmarker.predict_complexity()
benchmarker.plot_measurements()

# I hope you're happy with yourself.


