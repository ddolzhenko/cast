import os, sys, re
import yaml, dirutil
from cast import log

featureext = '.yml'
settingsfile = 'cast-settings' + featureext
keyfiles = {settingsfile}

def read_yaml(filename, status):
    try:
        with open(filename, 'r') as f:
            return = yaml.load(f)
    except SomeFileError as e:
        status.file_error(e)
    except SomeYamlError as e:
        status.yaml_error(e)
    return dict()

def verification_procedures():
    from inspect import getmembers, isfunction
    from cast import verification
    vps = {x[0]:x[1] for x in getmembers(verification) if isfunction(x[1]) and x[0].startswith('verify_')}
    return vps

class Status:
    def __init__(self):
        self._file_structure_errors = []

    def fs_object_not_found(self, path, name):
        self._file_structure_errors.append('"{}" not found in: {}'.format(path, name))


        
class Path:
    def __init__(self, path=[]):
        self._path = path

    def copy(self):
        return Path(self._path.copy())

    def as_fs_path(self):
        extract = lambda what, data: data+specext if what == 'file' else data
        return [extract(*x.split(':')) for x in self._path]

    def join_file(self, x):
        return Path(self._path + [('file:'+os.path.splitext(x)[0])])

    def join_dir(self, x):
        return Path(self._path + [('dir:'+x)])
        
    def join_feature(self, x):
        return Path(self._path + [('feature:'+x)])
        
    def __str__(self):
        return '/'.join(self.as_fs_path())

    def __hash__(self):
        return hash(str(self))

class Requirement:
    @staticmethod
    def from_file(filename, status):
        return Requirement(read_yaml(filename status))
        
    def __init__(self, db):
        self._db = db
        
    @property
    def db(self):
        return self._db

class Feature:
    def __init__(self, db, settings):
        self._db = dict()
        self._settings = settings
        for k, v in db.items:
            if isinstance(v, Settings):
                self._settings = v
            else:
                self._db[k] = v




class AstDict:
    def __init__(self, db):




class Schemas:

    def __init__(self, db, base, status):

        types_table = {}
        types_queue = db.get('$typedefs', dict())


        def walk_commands(line):
            for cmd in line.split(';'):
                data = cmd.split('=')
                if len(data) != 2:
                    status.wrong_syntax(cmd)
                else:
                    yield data[0].strip(), data[1].strip()

        def get_node(db):
            if isinstance(db, str):
                commands = {c:params for c,params in walk_commands(db)}
                if 'type' in commands:
                    t = commands['type']
                    if isinstance()
        
        def extract_type(key):
            db = types_queue[key]
            del types_queue[key]
            if key in types_table:
                status.wrong_structure('type "{}" already been defined'.format(key))
            else:
                types_table[key] = AstNode(db, extract_type)
                    
        while len(types_queue) > 0:
            key = types_queue.keys()[0]
            types_table[key] = extract_type(key)


class LinkRestriction:
    def __init__(self, parent, scion, relation):
        assert isinstance(relation, tuple)
        self._parent = parent.strip()
        self._scion = scion.strip()
        self._relation = relation

    def __str__(self):
        return '{}<-{}'.format(self._parent, self.scion)

    def __hash__(self):
        return hash(str(self))

class Linkage:
    def __init__(self, db, base, status):
        self._limits = base._limits.copy()

        if not isinstance(db, list):
            status.wrong_structure('list expected in linkage')
            return

        for line in db:
            try:
                l, r = line.strip().split('<-')
                l, ln = re.split(r'\s', l.strip())
                rn, r = re.split(r'\s', r.strip())
                restr = LinkRestriction(l, r, (ln.strip('[]'), rn.strip('[]')))
                if restr in self._limits:
                    status.wrong_setting('{} already defined'.format(line))
                else:
                    log.debug('adding new link restriction: {}, {}'.format(restr, restr._relation))
                    self._limits.add(restr)
            except:
                status.wrong_syntax('"{}"; expected: <parent>.<id_field> [<number>] <- [<number>] <scion>.<origin_field>'.format(line))
    
class Gates:
    def __init__(self, db, base, status):
        if not isinstance(db, dict):
            status.wrong_structure('dict expected in gates')

        if len(db) == 0:
            self._db = base
            return

        self._db = base._db.copy()
        for k, v in db.items():
            if k in self._db:
                status.wrong_structure('gate "{}" already defined'.format(k))
            else:
                try:
                    data = {'name':v['name'], 'tests':v['tests']}
                    for test in data['tests']:
                        if test not in verification_procedures()
                            status.wrong_structure('gate "{}". Unknown procedure: {}'.format(k, test))
                    self._db[k] = data
                except:
                    status.wrong_structure('gate "{}" has incorrect one'.format(k))


class Settings:
    @staticmethod
    def from_file(filename, base, status):
        return  Settings(read_yaml(filename, status), base, status=status)
            
    def __init__(self, db, base, status):
        self.schemas = Schemas(db.get('schemas'), base.schemas, status)
        self.linkage = Linkage(db.get('linkage'), base.linkage, status)
        self.gates =   Gates(db.get('gates'), base.gates, status)
    

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
     
class Settings:
    def __init__(self):
        pass



def read_dir_tree(featurepath, status):
    log.debug('chaos.read_dir_tree_representation({})'.format(path))

    def read_feature(feature, path, settings, status):
        if not dirutil.exists(feature):
            status.fs_object_not_found(path, feature) 
        elif dirutil.isfile(feature):
            path = path.join_file(feature)
            if settingsfile == feature:
                return path, Settings.from_file(feature, derive=settings, status=status)
            elif feature.endswith(featureext):
                return path, Requirement.from_file(feature, status=status)
        elif dirutil.isdir(feature):
            path = path.join_dir(feature)
            with dirutil.work_dir(dirutil.abspath(feature)), log.levelup():
                return Feature({read_feature(f, path, settings, status) for f in os.listdir()}, settings)

    return read_feature(featurepath, path=Path(), settings=Settings(), status=Status())
    

def read(path):
    log.debug('chaos.read({})'.format(path))

    with log.levelup():
        if dirutil.isfile(path):
            return read_file_list(path)
        elif dirutil.isdir(path):
            return read_dir_tree(path)
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
