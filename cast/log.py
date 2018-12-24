#  @author   Dmitri Dolzhenko
#  @brief    

import os, sys

def tab(level):
    return '  ' * level

tabulate = lambda x: '    {}'.format(x)
notab = lambda x: x

_logFile = None

def init_file(path, *paths):
    global _logFile
    fpath = os.path.join(path, *paths)
    _logFile = open(fpath, 'w')
    return _logFile


def log_to_file(what):
    global _logFile
    if _logFile:
        _logFile.write(what)


verbosity = 100
tab_level = 0

class levelup:
    def __enter__(self):
        global tab_level
        tab_level += 1

    def __exit__(self, *args):
        global tab_level
        tab_level -= 1


def log_level(level, what, data):
    log_to_file('{}: {}\n'.format(what, data))

    global verbosity
    global tab_level
    # verbosity = 1
    if verbosity > level:
        t = tab(tab_level)
        print(what + ': ' +  t + str(data).replace('\n', '\n'))

def message(data):
    log_level(0, 'message', data)

def critical_error(data):
    log_level(0, 'CRITICAL_ERROR', data)
    sys.exit(1)

def error(data):
    log_level(0, 'error', data)

def warning(data):
    log_level(1, 'warning', data)

def checkpoint(data):
    log_level(2, 'checkpoint', data)

def verbose(data):
    log_level(5, 'verbose', data)

def debug(data):
    log_level(10, 'debug', data)

class Status:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def is_failed(self):
        return self.errors

    def warning(self, warning):
        self.warnings += [warning]

    def error(self, text):
        self.errors += [text]

    def dump(self):
        message('found {} errors'.format(len(self.errors)))
        message('found {} warnings'.format(len(self.warnings)))

        for e in map(tabulate, self.errors):
            error(e)

        for w in map(tabulate, self.warnings):
            warning(w)

    def __str__(self):
        return 'found {} errors'.format(len(self.errors))

