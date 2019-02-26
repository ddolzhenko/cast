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
    x = expected_type() if key is None else key
    return expected_type(x)

get_str     = lambda db, key: get_not_none(db, x, str)
get_list    = lambda db, key: get_not_none(db, x, list)
get_dict    = lambda db, key: get_not_none(db, x, dict)

# -----------------------------------------------------------------

class Load_error(Exception): pass

def stop_if(cond, error_class, *params):
    if cond:
        raise error_class('Stop error: {}'.format(''.join(params)))

class Lazy_table:
    def __init__(self, head, lines, default):
        self.head = head
        self.lines = lines
        self.default = default

class Lazy_trace:
    def __init__(self, ids=[]):
        self.ids = ids

class Lazy_sequence:
    def __init__(self, brief='', relations=[]):
        self.brief = brief
        self.relations = realtions
        self.puml = None

class Lazy_entity:
    def __init__(self, typename, brief, description, details, interfaces)
        self.typename=typename
        self.brief=brief
        self.description=description
        self.details=details
        self.interfaces=interfaces

class Relation:
    def __init__(self, x, y, typename='association'):
        self.x = x
        self.y = y
        self.typename = typename

class Message:
    @staticmethod
    def valid_types():
        return { 
            '->', 'right',
            '-->', 'right-dotted',
            '<-', 'left',
            '<--', 'left-dotted',
            }

    def __init__(self, x, y, typeid='->', text=''):
        self.x, self.y = x, y
        self.typeid = typeid


def load_table(t):
    assert isinstance(t, dict), 
    default = get_str('default')
    head    = get_list(t, 'head')
    lines   = get_list(t, 'lines')
    for line in lines:
        stop_if(not_list(line), Load_error, 'table.lines must be a list of dicts')

    return Lazy_table(head, lines, default)

def load_trace(t):
    return Lazy_trace([str(x) for x in t])


def parse_relation(relation):
    stop_if(not isinstance(relation, dict), Load_error, 'relation must be a dict', realation)
    # <|-- extension
    # *-- composition
    # o-- aggregation
    # .. realization
    # -- association
    # -- dirrection

def parse_sequence_message(msg):
    stop_if(not isinstance(msg, dict), Load_error, 'sequence.message must be a dict: ', msg)
    stop_if(len(msg.items()) != 1, Load_error, 'only one message per line allowed: ', msg)
    rel, text = list(msg.items())[0]
    for r in Message.valid_types().keys():
        res = rel.split(r)
        if len(r) == 2:
            return Message(x=res[0].strip(), y=res[1].strip(), typeid=r, text=text)
    stop_if(True, Load_error, 'sequence.message is strange: ', msg)

def load_puml(path, pumlfile):
    res = Lazy_sequence()
    res.pumlfile = os.path.join(path, pumlfile)
    return res

def load_sequence(db):
    assert isinstance(db, dict)
    brief = get_str(db, 'brief')
    flow = list(map(parse_sequence_message, get_list(db, 'flow')))
    return Lazy_sequence(brief=brief, flow=flow)

def load_entity(entity, typename):
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
    assert isinstance(entity, dict)
    return {name: load_enity(value, typename) for name, value in entity.items()}

def load_swarc(filepath, filename):
    src = os.path.join(filepath, filename)
    log.verbose('loading swarc: ' + src)
    
    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include/swarc',
        lambda loader, x: load_swarc(filepath, loader.construct_scalar(x)))
    Loader.add_constructor('!include/puml',
        lambda loader, x: load_puml(filepath, loader.construct_scalar(x)))
    
    Loader.add_constructor('!unit',
        lambda loader, x: load_entity(loader.construct_mapping(x), 'unit'))
    Loader.add_constructor('!units',
        lambda loader, x: load_entities(loader.construct_mapping(x), 'unit'))
    Loader.add_constructor('!component',
        lambda loader, x: load_entity(loader.construct_mapping(x), 'component'))
    Loader.add_constructor('!components',
        lambda loader, x: load_entities(loader.construct_mapping(x), 'component'))
    Loader.add_constructor('!domain',
        lambda loader, x: load_entity(loader.construct_mapping(x), 'domain'))
    Loader.add_constructor('!domains',
        lambda loader, x: load_entities(loader.construct_mapping(x), 'domain'))

    Loader.add_constructor('!node',
        lambda loader, x: load_entity(loader.construct_mapping(x), 'node'))
    Loader.add_constructor('!nodes',
        lambda loader, x: load_entities(loader.construct_mapping(x), 'node'))
    
    Loader.add_constructor('!sequence', 
        lambda loader, x: load_sequence(loader.construct_mapping(x)))
    
    Loader.add_constructor('!table', 
        lambda loader, x: load_table(loader.construct_mapping(x)))
    Loader.add_constructor('!trace', 
        lambda loader, x: load_trace(loader.construct_sequence(x)))
    with open(src) as f:
        return yaml.load(f, Loader=Loader)

def load_prs(filepath, filename):
    src = os.path.join(filepath, filename)
    log.verbose('loading prs: ' + src)

    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include',
        lambda loader, x: load(filepath, loader.construct_scalar(x)))
    with open(src) as f:
        return yaml.load(f, Loader=Loader)

def load(filepath, filename):
    src = os.path.join(filepath, filename)
    log.verbose('loading: ' + src)
   
    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include/swarc',
        lambda loader, x: load_swarc(filepath, loader.construct_scalar(x)))
    Loader.add_constructor('!include/prs',
        lambda loader, x: load_prs(filepath, loader.construct_scalar(x)))
    Loader.add_constructor('!include',
        lambda loader, x: load(filepath, loader.construct_scalar(x)))
    with open(src) as f:
        return yaml.load(f, Loader=Loader)

# ----------------------------------------------------------------------
class Objects:
    def __init__(self):
        self.


def compile_objects(data):
    def parser(obj, tree):


    obj = Objects()
    parser(obj, data)
    return obj

@monadic
def do_all():
    data = load(filepath, filename)
    obj = compile_objects(data)
    lib = link(obj)
    return lib


def render_prs(prs, templatefile, outfile):
    with open(templatefile) as f:
        template = jinja2.Template(f.read())
    with open(outfile, 'w') as f:
        f.write(template.render(prs=prs))

