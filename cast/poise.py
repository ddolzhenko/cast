import os
import sys
import uuid 
import jinja2
import yaml
import dirutil
from cast import log

ext = '.yml'

# helpers
def get_not_none(db, key, expected_type):
    x = db.get(key)
    x = expected_type() if x is None else x
    return expected_type(x)

get_str     = lambda db, key: get_not_none(db, key, str)
get_list    = lambda db, key: get_not_none(db, key, list)
get_dict    = lambda db, key: get_not_none(db, key, dict)

not_list    = lambda x: not isinstance(x, list)
not_dict    = lambda x: not isinstance(x, dict)

# -----------------------------------------------------------------

class PoiseError(Exception):
    def __init__(self, mark, message):
        self.message = message
        self.mark = mark

    def __str__(self):
        err = '{}:{}:{}: error: {}'.format(
            str(self.mark.name), 
            self.mark.line, 
            self.mark.column, 
            str(self.message))
        return err

class ShortCirquit(Exception):
    def __init__(self, msg):
        self.msg = msg

def stop_if(cond, msg):
    if cond:
        raise ShortCirquit(msg)


class Lazy_swarc:
    def __init__(self, db):
        self.db = db

class Lazy_prs:
    def __init__(self, db):
        self.db = db

class Lazy_table:
    def __init__(self, head, lines, default):
        self.head = head
        self.lines = lines
        self.default = default

class Lazy_trace:
    def __init__(self, ids):
        self.ids = ids

class Lazy_sequence:
    def __init__(self, brief, flow):
        self.brief = brief
        self.flow = flow
        self.puml = None

class Lazy_entity:
    def __init__(self, typename, brief, description, details, interfaces):
        self.typename=typename
        self.brief=brief
        self.description=description
        self.details=details
        self.interfaces=interfaces

class Lazy_relation:
    def __init__(self, x, y, typename):
        self.x = x
        self.y = y
        self.typename = typename

class Lazy_message:
    @staticmethod
    def valid_types():
        return { 
            '->', 'right',
            '-->', 'right-dotted',
            '<-', 'left',
            '<--', 'left-dotted',
            }

    def __init__(self, x, y, typeid, text):
        self.x, self.y = x, y
        self.typeid = typeid



def load_table(t):
    default = get_str(t, 'default')
    head    = get_list(t, 'head')
    lines   = get_list(t, 'lines')
    for line in lines:
        stop_if(not_dict(line), 'table.lines must be a list of dicts: {}'.format(t))
    return Lazy_table(head, lines, default)

def load_trace(t):
    return Lazy_trace([str(x) for x in t])

def parse_relation(relation):
    pass
    # <|-- extension
    # *-- composition
    # o-- aggregation
    # .. realization
    # -- association
    # -- dirrection

def parse_sequence_message(msg):
    stop_if(len(msg.items()) != 1, 'only one message per line allowed')
    rel, text = list(msg.items())[0]
    for r in Lazy_message.valid_types().keys():
        res = rel.split(r)
        if len(r) == 2:
            return Lazy_message(x=res[0].strip(), y=res[1].strip(), typeid=r, text=text)
    stop_if(True, 'sequence.message is strange')

def load_puml(pumlfile, path):
    res = Lazy_sequence(brief='', flow=[])
    res.pumlfile = os.path.join(path, pumlfile)
    return res

def load_sequence(db):
    # TODO
    return Lazy_sequence(brief='', flow=[])
    brief = get_str(db, 'brief')
    flow = list(map(parse_sequence_message, get_list(db, 'flow')))
    return Lazy_sequence(brief=brief, flow=flow)

def load_entity(entity, typename):
    entity = dict() if entity is None else entity
    brief       = get_str(entity, 'brief')
    desc        = get_str(entity, 'description')
    details     = get_dict(entity, 'details')
    interfaces  = get_dict(entity, 'interfaces')
    return Lazy_entity( typename=typename, 
                        brief=brief, 
                        description=desc, 
                        details=details, 
                        interfaces=interfaces)

def load_entities(entity, typename):
    return Lazy_swarc({name: load_entity(value, typename) for name, value in entity.items()})

def loader_bind(expected_type, loader_handler, *params):
    def wrapper(loader, node):
        mark = node.end_mark
        if expected_type == dict:
            db = loader.construct_mapping(node)
        elif expected_type == list:
            db = loader.construct_sequence(node)
        else:
            db = loader.construct_scalar(node)
        db = expected_type() if db is None else expected_type(db)
        try:
            # print('calling: ', loader_handler.__name__)
            # print('db: ', db)
            # print('params: ', params)
            result = loader_handler(db, *params)
            result.mark = mark
        except ShortCirquit as e:
            raise PoiseError(mark, e.msg)
        except Exception as e:
            # raise e
            raise e if isinstance(e, PoiseError) else PoiseError(mark, str(e))
        return result
    return wrapper

def fix_path(filename, filepath):
    src = os.path.join(filepath, filename)
    src = os.path.abspath(src)
    filepath, filename = os.path.split(src)
    return filename, filepath
    

def load_swarc(filename, filepath):
    filename, filepath = fix_path(filename, filepath)
    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include/swarc',    loader_bind(str,  load_swarc, filepath))
    Loader.add_constructor('!include/puml',     loader_bind(str,  load_puml, filepath))
    Loader.add_constructor('!nodes',            loader_bind(dict, load_entities, 'node'))
    Loader.add_constructor('!units',            loader_bind(dict, load_entities, 'unit'))
    Loader.add_constructor('!components',       loader_bind(dict, load_entities, 'component'))
    Loader.add_constructor('!domains',          loader_bind(dict, load_entities, 'domain'))
    Loader.add_constructor('!sequence',         loader_bind(dict, load_sequence))
    Loader.add_constructor('!table',            loader_bind(dict, load_table))
    Loader.add_constructor('!trace',            loader_bind(list, load_trace))
    try:
        with open(os.path.join(filepath, filename)) as f:
            return Lazy_swarc(yaml.load(f, Loader=Loader))
    except FileNotFoundError as e:
        raise ShortCirquit(str(e))


def load_prs(filepath, filename):
    filename, filepath = fix_path(filename, filepath)
    raise Exception('TODO')
    
def load(filename, filepath):
    filename, filepath = fix_path(filename, filepath)
    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include/swarc',    loader_bind(str, load_swarc, filepath))
    Loader.add_constructor('!include/prs',      loader_bind(str, load_prs, filepath))
    Loader.add_constructor('!include',          loader_bind(str, load, filepath))
    try:
        with open(os.path.join(filepath, filename)) as f:
            return yaml.load(f, Loader=Loader)
    except yaml.scanner.ScannerError as e:
        raise PoiseError(e.problem_mark, e.problem)
    
        
# ----------------------------------------------------------------------

# dict like 
class Mapping(dict):
    def __init__(self, db):
        assert isinstance(db, dict)
        self.__dict__.__init__(db)
    def __getitem__(self, key):
        return self.__dict__[key]
    def __len__(self):
        return len(self.__dict__)
    def __contains__(self, item):
        return item in self.__dict__
    def __iter__(self):
        return iter(self.__dict__)
    def keys(self):
        return self.__dict__.keys()
    def values(self):
        return self.__dict__.values()
    def items(self):
        return self.__dict__.items()
    def __str__(self):
        return str(self.__dict__)
    
class DataTable:
    def __init__(self, data=dict()):
        assert isinstance(data, dict)
        self.data = data
        self.maps = {'name', Mapping(self.data)}

    def __setitem__(self, key, item):
        self.data[key] = item
    def __getitem__(self, key):
        return self.data[key]
    def __len__(self):
        return len(self.data)

    def items(self):
        return self.maps['name']

    def map_by(attribute_name):
        if attribute_name not in self.maps:
            db = {}
            for v in self.data.values():
                if attribute_name in v:
                    db[attribute_name].append(v)
                else:
                    db[attribute_name] = [v]
            self.maps[attribute_name] = db
        return maps[attribute_name]


class Objects:
    def __init__(self):
        self.db = {}

    def get_table(name):
        if name not in self.db:
            self.db[name] = DataTable()
        return self.db[name]

    def define(self, class_name, name, obj):
        tbl = self.get_table(class_name)
        tbl[name] = obj
        return obj

class Entity:

    def __init__(self):
        self.type_name
        self.name
        self.brief
        self.description

        # self.parents    {who, what kind}
        # self.children   {who, }

        # self.interfaces {}

        # self.dependencies_on_me {who, how}
        # self.dependencies_me_on {who, how}


class Relation:
    def __init__(self, data):
        ...
        
        self.x
        self.y
        self.relation_type
        self.relation_dirrection
    
    


def compile(data):

    obj = Objects()

    def parse(parent, node_name, node):
        if node is None:
            return
        if isinstance(node, dict):
            for name, subnode in node.items():
                parse(name, subnode)
            return
        if isinstance(node, list):
            for i, subnode in enumerate(node):
                parse(i, subnode)
            return
        if isinstance(node, Lazy_swarc):
            return parse(node_name, node.db)
        if isinstance(node, Lazy_prs):
            return parse(node_name, node.db)
        if isinstance(node, Lazy_table):
            return
        if isinstance(node, Lazy_trace):
            return
        if isinstance(node, Lazy_sequence):

            return
        if isinstance(node, Lazy_entity):
            obj.define('entities', node_name, Entity(node))
            return parse(node_name, node.details)
        if isinstance(node, Lazy_relation):
            obj.define('relations', node_name, Relation(node))
            return
        if isinstance(node, Lazy_message):
            obj.define('relations', node_name, Relation(node))
            return 


    root = obj.define('root', 'root', 'root')
    parse(root, data)
    return obj

# ------------------------------------------------------------------------
#  linker

def link(obj):
    # add link information to each object
    entities  = obj.get_table('entities').map_by('name')
    relations = obj.get_table('relations').map_by('name')

    for name, r in relations.values():
        pass        



def render(lib, templatefile, outfile):
    for target in lib.targets():
        with open(target.templatefile) as f:
            template = jinja2.Template(f.read())
        with open(target.outfile, 'w') as f:
            f.write(template.render(entity=target.entity))

# @monadic
def do_all(filepath, filename):
    data = load(filename, filepath)
    obj = compile(data)
    lib = link(obj)
    return render(lib)


