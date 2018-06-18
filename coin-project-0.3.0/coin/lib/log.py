# -*- coding: utf-8 -*-
from logging import StreamHandler, NullHandler
from logging.handlers import SysLogHandler
from logging import getLogger as _getLogger

root_logger = None
null_logger = None
logger_cache = {}
logger_filters = {}
_stdout = True
_root_logger_name = 'noapp'
_disabled_logger = []

def get_logger(name=''):
    global logger_cache
    if name not in logger_cache:
        logger_cache[name] = LoggerProxy(name)
    return logger_cache[name]

def setup(root='noapp', stdout=True, filters={}):
    global _stdout, _root_logger_name
    _stdout = stdout
    _root_logger_name = root
    add_filters(filters)


def add_filters(filters = {}):
    for k, v in filters.items():
        if k[0] == '.':
            k = '%s%s'%(_root_logger_name, k)
        logger_filters[k] = v
        if v.upper() == 'OFF':
            _disabled_logger.append(k)

def syslog_handlers(logger_name, address=('127.0.0.1', 514), facility=0, level= 'DEBUG'):
    global _root_logger_name, root_logger, _stdout
    logger_names = []
    loggers = []
    if type(logger_name) in [str, unicode]:
        logger_names = [logger_name]
    elif type(logger_name) in [list, tuple]:
        logger_names = logger_name
    else:
        return loggers
    for name in logger_names:
        logger = _getLogger(name)
        _level = logger_filters.get(name) or level
        _level = _level.upper()
        if _level == 'OFF':
            handler = NullHandler()
            logger.addHandler(handler)
        elif _level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            del logger.handlers[:]
            logger.setLevel(_level)
            handler = SysLogHandler(address=tuple(address), facility= SysLogHandler.LOG_LOCAL0 + facility)
            handler.setLevel(_level)
            logger.addHandler(handler)
            # if _stdout:
            #     handler = StdoutHandler()
            #     handler.setLevel(_level)
            #     logger.addHandler(handler)
        logger.propagate = 0
        if name == _root_logger_name:
            root_logger = logger
        loggers.append(logger)
    return loggers


class StdoutHandler(StreamHandler):
    def emit(self, record):
        global _stdout
        StreamHandler.emit(self, record) if _stdout else None

class LoggerProxy(object):
    def __init__(self, name):
        self.name = name
        self._logger = None

    @property
    def root_logger(self):
        global root_logger
        if root_logger is None:
            root_logger = syslog_handlers(_root_logger_name)[0]
        return root_logger

    @property
    def null_logger(self):
        global null_logger
        if null_logger is None:
            null_logger = syslog_handlers('null_logger', level='OFF')[0]
        return null_logger


    @property
    def logger(self):
        if self._logger is None:
            if self.name:
                full_name = '%s.%s'%(_root_logger_name, self.name)
                for disabled in _disabled_logger:
                    if full_name.startswith(disabled):
                        self._logger = self.null_logger
                if self._logger is None:
                    self._logger = self.root_logger.getChild(self.name)

                level = logger_filters.get(full_name)
                if level and level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    self._logger.setLevel(level.upper())
            else:
                self._logger = self.root_logger
        return self._logger

    def __getattr__(self, attrib):
        return getattr(self.logger, attrib)
