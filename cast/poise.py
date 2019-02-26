import os
import sys
import uuid 
import jinja2
import yaml
import dirutil
from cast import log

ext = '.yml'

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
    default = t.get('default', '')
    head = t.get('head', [])
    lines = t.get('lines', [])

    not_list = lambda x: not isinstance(x, list)
    stop_if(not_list(head), Load_error, 'table.head must be a list')
    stop_if(not_list(lines), Load_error, 'table.lines must be a list of dicts')
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
    brief = str(db.get('brief', ''))
    flow = db.get('flow', dict())
    flow = dict is flow is None else flow
    flow = list(map(parse_sequence_message, flow))
    return Lazy_sequence(brief=brief, flow=flow)
     

def load_swarc(filepath, filename):
    src = os.path.join(filepath, filename)
    log.verbose('loading spec module: ' + src)
    
    class Loader(yaml.Loader): pass
    Loader.add_constructor('!include/swarc',
        lambda loader, x: load_swarc(filepath, loader.construct_scalar(x)))
    Loader.add_constructor('!include/puml',
        lambda loader, x: load_puml(filepath, loader.construct_scalar(x)))
    Loader.add_constructor('!table', 
        lambda loader, x: load_table(loader.construct_mapping(x)))
    Loader.add_constructor('!trace', 
        lambda loader, x: load_trace(loader.construct_sequence(x)))
    Loader.add_constructor('!sequence', 
        lambda loader, x: load_sequence(loader.construct_mapping(x)))
    with open(src) as f:
        return yaml.load(f, Loader=Loader)

def load_swarc(filepath, filename):
    db = load_db(filepath, filename)
    
    prj = Project()
    load_project(filepath, filename, prj)


class Subsection:
    def __init__(self, path, title, db):
        text = ''
        if isinstance(db, str):
            text = db
            db = dict()
        elif db is None:
            db = dict()
        elif isinstance(db, dict):
            pass
        else:
            log.error('dict expected in {}'.format('/'.join(path)))
            return

        assert isinstance(db, dict)
        assert isinstance(path, list)

        self.path = path
        self.title = title
        self.text = text
        self.requirements = []
        self.subsections = []

        for name, sub_db in db.items():
            assert isinstance(name, str)
            if '.' in name:
                sid, title = name.split('.')
                self.subsections.append(Subsection(path+[sid], title, sub_db))
            else:
                self.requirements.append(Requirement(path+[name], sub_db))

def fix_list(db, name):
    obj = db.get(name, [])
    obj = [obj] if isinstance(obj, str) else obj
    assert isinstance(obj, list)
    return obj

class Requirement:
    def __init__(self, path, db):
        if isinstance(db ,str):
            db = {'description': db}

        self.rid         = '.'.join(path)
        self.guid        = db.get('guid', uuid.uuid4())
        self.description = db.get('description', '')
        self.verification_criteria = db.get('verification-criteria', '')
        self.origin         = fix_list(db, 'origin')
        self.dependencies   = fix_list(db, 'dependencies')
        self.links          = fix_list(db, 'links')

def render_prs(prs, templatefile, outfile):
    with open(templatefile) as f:
        template = jinja2.Template(f.read())
    with open(outfile, 'w') as f:
        f.write(template.render(prs=prs))

