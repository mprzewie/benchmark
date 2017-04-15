import logging


class Funlogger:
    def __init__(self, log_name=""):
        self.log_name = log_name
        logging.basicConfig(filename=log_name, level=logging.DEBUG)
        self.clear_log()

    def log(self, msg):
        if (self.log_name == ""):
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
