import os, sys
import yaml, dirutil
from cast import log
from cast import chaos

tab = '  '
is_str = lambda x: isinstance(x, str)
is_oneline_str = lambda x: is_str(x) and ('\n' not in x)
is_multiline_str = lambda x: is_str(x) and ('\n' in x)
is_leaf = lambda x: x is None or (type(x) in {int}) or is_oneline_str(x)

def cute_str(text, level=0):
    prefix = tab*level
    yield '|'
    for line in text.split('\n'):
        yield prefix + line
    yield ''
    
def cute_dict(db, level=0):
    prefix = tab*level
    for k, req in db.items():
        if is_leaf(req):
            yield '{}{}: {}'.format(prefix, k, str(req))
        elif is_multiline_str(req):
            yield '{}{}: |'.format(prefix, k)
            yield from cute_str(req, level+1)
        else:
            yield '{}{}:'.format(prefix, k)
            yield from cute(req, level+1)

def cute_list(db, level=0):
    prefix = tab*level
    for x in db:
        if is_leaf(x):
            yield '{}- {}'.format(prefix, x)
        elif is_multiline_str(req):
            yield '{}- |'.format(prefix)
            yield from cute_str(x, level+1)
        else:
            yield '{}-'.format(prefix)
            yield from cute(x, level+1)

def cute(db, level=0):
    if isinstance(db, list):
        yield from cute_list(db, level)
    elif isinstance(db, dict):
        yield from cute_dict(db, level)
    elif isinstance(db, chaos.Requirement):
        yield from cute_dict(db._db, level)
    else:
        log.critical_error('unknown type in db: ' + str(type(db)) +str(db))


def as_file_list(db, out=sys.stdout):
    out.write('\n'.join(cute(db)))

def as_dir_tree(db, work_dir):
    structure = {}
    def update(structure, path, data):
        assert len(path) > 0

        if len(path) == 1:
            assert path[0] not in structure
            structure[path[0]] = data
            return 

        if path[0] not in structure:
            structure[path[0]] = {}

        update(structure[path[0]], path[1:], data)

    for path, req in db.items():
        update(structure, path.as_fs_path(), '\n'.join(cute_dict(req.as_dict())))
    
    with dirutil.work_dir(work_dir):
        for k in structure.keys():
            dirutil.safe_remove(k)
        dirutil.create_structure(structure)


def perform(db, work_dir, output, forced=False, representation='file-list'):
    log.debug('chaos.serialize({})'.format(output))

    if output is None:
        return as_file_list(db, sys.stdout)
    
    if not forced and dirutil.exists(output):
        log.critical_error('path already exists: {}'.format(path))
    
    output = dirutil.abspath(output)
    dirutil.safe_remove(output)
    if representation=='file-list':
        with open(output, 'w') as out:
            return as_file_list(db, out)
    elif representation=='dir-tree':
        return as_dir_tree(db, output)
    
    log.critical_error('unknown represention: ' + representation)

