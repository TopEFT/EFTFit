import logging

# Custom formatter, see: https://stackoverflow.com/a/8349076
class LvlFormatter(logging.Formatter):
    info_fmt = '[%(levelname)s] %(message)s'
    war_fmt  = '[%(levelname)s] %(message)s'
    err_fmt  = '[%(levelname)s] %(module)s - line %(lineno)d : %(message)s'
    dbg_fmt  = '[%(levelname)s] %(module)s - line %(lineno)d : %(message)s'

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = LvlFormatter.dbg_fmt
        elif record.levelno == logging.INFO:
            self._fmt = LvlFormatter.info_fmt
        elif record.levelno == logging.WARNING:
            self._fmt = LvlFormatter.war_fmt
        elif record.levelno == logging.ERROR:
            self._fmt = LvlFormatter.err_fmt
        else:
            self._fmt = format_orig

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result