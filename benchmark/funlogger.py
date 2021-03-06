import logging


class Funlogger:
    def __init__(self, log_name=None):
        self.log_name = log_name
        if log_name is not None:
            logging.basicConfig(filename=log_name, level=logging.DEBUG)
            self.clear_log()

    def log(self, msg):
        if self.log_name is None:
            print(msg)
        else:
            logging.info(msg)

    def log_fun(self, f):
        def tmp(*args):
            result = f(*args)
            self.log(f.__name__ + str(args) + " = " + str(result))
            return result

        return tmp

    def clear_log(self):
        with open(self.log_name, "w"):
            pass
