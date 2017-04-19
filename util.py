import signal


class NotEnoughMeasurePointsException(Exception):
    pass


class TimeoutException(Exception):
    def __init__(self, timeout):
        self.timeout = timeout

    def timeout_to_str(self):
        return str(self.timeout) + " seconds"


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
