import os
import sys
import uuid 
import jinja2
import yaml
import dirutil
from cast import log

specext = '.yml'
keywords = set(['feature', 'fid', 'force', 'requirement', 'origin', 'acceptance', 'rid'])
keyfiles = {word+specext for word in keywords}


def load_db(filepath, filename):
    src = os.path.join(filepath, filename)
    log.verbose('loading spec module: ' + src)
    
    class specLoader(yaml.Loader): pass

    def importer(loader, node):
        what = loader.construct_scalar(node)
        return load_db(filepath, what)

    specLoader.add_constructor('!include', importer)
    with open(src) as f:
        return yaml.load(f, Loader=specLoader)

def load_prs(filepath, filename):
    db = load_db(filepath, filename)
    prs = Subsection(['prs'], 'Project Requirement Specification', db)
    return prs

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
            if isinstance(name, int):
                name = str(name)
            assert isinstance(name, str)
            if '.' in name:
                sid, title = name.split('.')
                self.subsections.append(Subsection(path+[sid], title, sub_db))
            else:
                self.requirements.append(Requirement(path+[name], sub_db))

def fix_list(db, name):
    obj = db.get(name, [])
    obj = [obj] if isinstance(obj, str) else obj
    if obj is None:
        obj = []
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
