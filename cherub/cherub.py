from frogcherub import menus
    
import logging
import logging.handlers
import sys
import argparse

_log = logging.getLogger('frogcherub')
_log.setLevel(logging.DEBUG)


def main():
    _setup_console_logger()

    # noinspection PyBroadException
    try:
        _parse_cli_and_run()
    except KeyboardInterrupt:
        pass
    except Exception:
        _log.exception("Problem during execution")
        sys.exit(1)
    sys.exit(0)
    
    
def _parse_cli_and_run():
    parser = argparse.ArgumentParser(description='Cherub Data Entry Tool')
    parser.add_argument('-d', '--datafile', help="A file of datapoints to load with")
    
    args = parser.parse_args()
    
    menus.show_main_menu(start_file=args.datafile)
    
    
class _ExactLevelFilter(object):
    """
    Only allows log records through that are particular levels.
    """

    def __init__(self, levels):
        """
        Creates a new exact level filter.
        :type levels: ``list[int|str]``
        :param levels: The levels that should pass through the filter; all others are filtered out. Each item is either
        one of the predefined level names or an integer level.
        """
        self._levels = set()
        for lev in levels:
            is_int = False
            try:
                lev = lev.upper()
            except AttributeError:
                is_int = True
            if not is_int:
                if lev == 'DEBUG':
                    self._levels.add(logging.DEBUG)
                elif lev == 'INFO':
                    self._levels.add(logging.INFO)
                elif lev == 'WARNING' or lev == 'WARN':
                    self._levels.add(logging.WARNING)
                elif lev == 'ERROR':
                    self._levels.add(logging.ERROR)
                elif lev == 'CRITICAL':
                    self._levels.add(logging.CRITICAL)
                else:
                    raise ValueError("bad level name in levels list: " + lev)
            else:
                self._levels.add(int(lev))

    def num_levels(self):
        """
        Gets the number of levels that are allowed through the filter.
        :rtype: ``int``
        :return: The number of levels.
        """
        return len(self._levels)

    def min_level(self):
        """
        Gets the minimum level that is allowed through the filter.
        :rtype: ``int``
        :return: The minimum leel
        """
        return min(self._levels)

    def filter(self, record):
        """
        Check whether to include the given log record in the output.
        :type record: ``logging.LogRecord``
        :param record: The record to check.
        :rtype: ``int``
        :return: 0 indicates the log record should be discarded; non-zero indicates that the record should be
        logged.
        """
        if record.levelno in self._levels:
            return 1
        else:
            return 0


def _setup_console_logger():
    file_handler = logging.handlers.RotatingFileHandler('cherub.log', maxBytes=25*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
    logging.getLogger().addHandler(file_handler)

    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.getLogger().addHandler(stderr_handler)

    lev_filter = _ExactLevelFilter(['INFO'])
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(lev_filter.min_level())
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))
    stdout_handler.addFilter(lev_filter)
    logging.getLogger().addHandler(stdout_handler)


if __name__ == "__main__":
    main()
