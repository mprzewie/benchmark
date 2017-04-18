import signal


class NotEnoughMeasurePointsException(Exception):
    pass


class TimeoutException(Exception):
    pass


def with_timeout(timeout):
    def handler(signum, frame):
        raise TimeoutException(timeout)

    def timeout_canceller(f):
        def tmp(*args):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            if type(args) is list:
                return f(args)
            else:
                return f(*args)

        return tmp

    return timeout_canceller
