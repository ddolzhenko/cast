import os, sys
import yaml, dirutil
from cast import log

specext = '.yml'
keywords = set(['feature', 'fid', 'force', 'requirement', 'origin', 'acceptance', 'rid'])
keyfiles = {word+specext for word in keywords}

class Path:
    def __init__(self, path=[]):
        self._path = path

    def as_fs_path(self):
        extract = lambda what, data: data+specext if what == 'file' else data
        return [extract(*x.split(':')) for x in self._path]

    def extended_file(self, x):
        result = Path(self._path.copy())
        assert x.endswith(specext)
        x = x[:-len(specext)]
        result._path.append('file:' + x)
        return result

    def extended_dir(self, x):
        result = Path(self._path.copy())
        result._path.append('dir:' + x)
        return result

    def extended_feature(self, x):
        result = Path(self._path.copy())
        result._path.append('feature:' + x)
        return result

    def __str__(self):
        return '/'.join((x.split(':')[-1] for x in self._path))

    def __hash__(self):
        return hash(str(self))

class Requirement:
    @staticmethod
    def from_file(filename, force):
        with open(filename, 'r') as f:
            db = yaml.load(f)
            return Requirement(db, force)

    def __init__(self, db, force):
        self._db = db.copy()
        self._force = force
        self._patch_required_fields()

    @property
    def db(self):
        return self._db

    def _patch_required_fields(self):
        self._db['origin'] = self._db.get('origin', '')
        self._db['text'] = self._db.get('text', '')
        self._db['tags'] = self._db.get('text', [])

class Force:
    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            db = yaml.load(f)
            return Force(db)

    def __init__(self, force=dict()):
        self._restrictions = force

    def restricted_with(self, other):
        # TODO
        return Force(other._restrictions.copy())
        

    def as_dict(self):
        return self._restrictions

class DB:
    def __init_(self, db):
        self._db = db
        self._origin_index = self._generate_origin_index()
        self._text_index = self._generate_text_index()
        self._origin_index  = {hash(r.db['origin']): req for rid, req in self._db.items()}
        self._text_index    = {hash(r.db['text']): req for rid, req in self._db.items()}

    @property
    def db(self):
        return self._db

    @property
    def origin_hash_index(self):
        return self._origin_index
    
    @property
    def text_hash_index(self):
        return self._text_index
     


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
                log.debug('+adding spec: {} from: {}'.format(spec, path))
                yield path.extended_file(spec), Requirement.from_file(spec, force)
            elif spec == 'force.yml':
                yield path.extended_file(spec), force
            else: 
                log.debug('-skipping: {} from: {}'.format(spec, path))
        elif dirutil.isdir(spec):
            dirpath = dirutil.abspath(spec)
            log.debug('reading feature: {} from: {}'.format(spec, path))
            with dirutil.work_dir(dirpath), log.levelup():
                force = update_restrictions(force)
                for fsitem in os.listdir(dirpath):
                    yield from spec_iterator(fsitem, path.extended_dir(spec), force)
        else:
            critical_error('strange object {} detected in: {}'.format(spec, path))
    
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


def update(db, patch):
    added = 0
    changed = 0


    def try_update_req(what, patch):
        if patch is None:
            return what
        if not isinstance(what, dict) or not isinstance(patch, dict):
            return patch
        keys = set(what.keys()) | set(patch.keys())
        return {k:try_update_req(what.get(k), patch.get(k)) for k in keys}

    old_db = db.copy()
    for rid, req in patch.items():
        if rid not in old_db:
            print ('update-added:{}:::'.format(rid))
            db[rid] = req
            added += 1
        else:
            db[rid] = try_uodate_req(db[rid], req.db)


    return db
