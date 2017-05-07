import stopit

from contextlib import contextmanager


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


def contextify(suppposed_context_manager):
    try:
        __init__ = getattr(suppposed_context_manager,
                           '__init__')
        __enter__ = getattr(suppposed_context_manager,
                            '__enter__')
        __exit__ = getattr(suppposed_context_manager,
                           '__exit__')
        if callable(__init__) and callable(__enter__) and callable(__exit__):
            return suppposed_context_manager
        else:
            raise Exception
    except Exception:
        @contextmanager
        def actual_context_manager(size):
            yield suppposed_context_manager(size)

        return actual_context_manager
