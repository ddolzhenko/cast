import os
import yaml, dirutil
from cast import log

class Path:
    def __init__(self):
        self._path = []

    def extend_file(self, x):
        self._path.append('file:' + x)
        return self

    def extend_dir(self, x):
        self._path.append('dir:' + x)
        return self

    def extend_feature(self, x):
        sel._path.append('feature:' + x)
        return self

    def __str__(self):
        return '/'.join(self._path)


class Requirement:
    @staticmethod
    def from_file(filename, force):
        with open(filename, 'r') as f:
            db = yaml.load(f)
            return Requirement(db, force)

    def __init__(self, db, force):
        self._db = db
        self._force = force

class Force:
    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            db = yaml.load(f)
            return Force(db)

    def __init__(self, force=dict()):
        self._restrictions = force

    def restricted_with(self, other):
        pass # TODO

specext = '.yml'
keywords = set(['feature', 'fid', 'force', 'requirement', 'origin', 'acceptance', 'rid'])
keyfiles = {word+specext for word in keywords}

def update_restrictions(force):
    forcefile = 'force.yml'
    if dirutil.exists(forcefile):
        update = Force.from_file(forcefile)
        return force.restricted_with(update)
    return force

def read_file_list_representation(path):
    log.debug('chaos.read_file_list_representation({})'.format(path))

def read_dir_tree_representation(path):
    log.debug('chaos.read_dir_tree_representation({})'.format(path))

    def spec_iterator(spec, path=Path(), force=Force()):
        if not dirutil.exists(spec):
            log.critical_error('object not found. path={}, object={}'.format(path, spec))
        elif dirutil.isfile(spec):
            if spec.endswith(specext) and spec not in keyfiles:
                log.debug('+reading spec: {} from: {}'.format(spec, path))
                yield path.extend_file(spec), Requirement.from_file(spec, force)
            else:
                log.debug('-skipping: {} from: {}'.format(spec, path))
        elif dirutil.isdir(spec):
            dirpath = dirutil.abspath(spec)
            log.debug('+reading feature: {} from: {}'.format(spec, path))
            with dirutil.work_dir(dirpath), log.levelup():
                force = update_restrictions(force)
                for fsitem in os.listdir(dirpath):
                    yield from spec_iterator(fsitem, path.extend_dir(spec), force)
    
    with log.levelup():
        result = {rid : req for rid, req in spec_iterator(path)}
    return result

def read(path):
    log.debug('chaos.read({})'.format(path))

    with log.levelup():
        if dirutil.isfile(path):
            return read_file_list_representation(path)
        elif dirutil.isdir(path):
            return read_dir_tree_representation(path)
        else:
            log.critical_error('unknown chaos representation: {}'.format(path))


