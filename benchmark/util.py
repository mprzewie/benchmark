import signal
import stopit


class NotEnoughMeasurePointsException(Exception):
    pass


class TimeoutException(Exception):
    def __init__(self, timeout):
        self.timeout = timeout

    def timeout_to_str(self):
        return str(self.timeout) + " seconds"


def with_timeout(timeout):
    def timeout_canceller(f):
        def tmp(*args):
            with stopit.ThreadingTimeout(timeout) as ctx_mgr:
                assert ctx_mgr.state == ctx_mgr.EXECUTING

                if type(args) is list:
                    result = f(args)
                else:
                    result = f(*args)

            if ctx_mgr.state in (ctx_mgr.EXECUTING,
                                 ctx_mgr.TIMED_OUT,
                                 ctx_mgr.INTERRUPTED,
                                 ctx_mgr.CANCELED):
                raise TimeoutException(timeout)
            else:
                return result

        return tmp

    return timeout_canceller
