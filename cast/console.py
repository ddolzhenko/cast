# @author   d.dolzhenko@gmail.com

import os, sys, traceback, argparse, dirutil
from cast import log 


def main():
    try:
        # create parsers tree
        parser = argparse.ArgumentParser(prog='cast', description='Order in Chaos')
        parser.add_argument('--verbose', '-v', action='count')
        subparsers = parser.add_subparsers()
        parser_judge    = subparsers.add_parser('judge',    help='evaluates project')
        parser_cutify   = subparsers.add_parser('cutify',   help='cutifies project')
        parser_query    = subparsers.add_parser('query',    help='similar to xpath queries')
        parser_update   = subparsers.add_parser('update',   help='update chaos database')
        parser_entropy  = subparsers.add_parser('entropy',  help='estimate entropy')
        parser_import   = subparsers.add_parser('import',   help='import various formats')
        parser_generate = subparsers.add_parser('alpha-generate',  help='generate document by template')

        # judge    
        parser_judge.add_argument('project', type=str, help='project path')
        parser_judge.add_argument('--gate', type=int, default="100", help='maximum quality gate')
        parser_judge.set_defaults(func=judge_handler)

        # cutify
        parser_cutify.add_argument('project', type=str, help='input project to cutify')
        parser_cutify.set_defaults(func=cutify_handler)

        # query
        parser_query.add_argument('project', type=str, help='input project')
        parser_query.add_argument('query', type=str, help='query string')
        parser_query.add_argument('--output', type=str, help='output path')
        parser_query.set_defaults(func=query_handler)

        # update
        parser_update.add_argument('project', type=str, help='project to update')
        parser_update.add_argument('patch', type=str, help='patch to aaply')
        parser_update.add_argument('--preview', action='store_true', help='only preview impact')
        parser_update.set_defaults(func=update_handler)

        # entropy
        parser_entropy.add_argument('project', type=str, help='project')
        parser_entropy.set_defaults(func=entropy_handler)

        # import
        parser_import.add_argument('project', type=str, help='project')
        parser_import.add_argument('input', type=str, help='input file')
        parser_import.add_argument('delta', type=str, help='path to delta file')
        parser_import.set_defaults(func=import_handler)

        # generate
        parser_generate.add_argument('project', type=str, help='project')
        parser_generate.add_argument('template', type=str, help='template')
        parser_generate.set_defaults(func=generate_handler)

        # parse some argument lists
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)

    except Exception as e:
        log.error('<{}>: {}'.format(sys.exc_info()[0], e))
        log.debug(traceback.format_exc())
        print('\nProcess interrupted. Please see "detailed.log" file for details\n')


def judge_handler(args):
    from cast import chaos
    from cast import judge

    with log.levelup():
        db = chaos.read(args.project)
        judge.main(db, args.gate)


def cutify_handler(args):
    from cast import chaos, serialize
    with log.levelup():
        db = chaos.read(args.project)
        work_dir = args.project+'/..'
        # work_dir = 'trial-project.tests'
        serialize.as_dir_tree(db, work_dir)
        

def query_handler(args):
    from cast import chaos, serialize
    with log.levelup():
        db = chaos.read(args.project)
        db = chaos.query(db, args.query)
        serialize.as_file_list_tree(db, args.output)


def update_handler(args):
    from cast import chaos, serialize
    
    with log.levelup():
        db = chaos.read(args.project)
        patch = chaos.read(args.patch)
        new_db = chaos.update(db, pacth)
        if not args.preview:
            work_dir = args.project+'/..'
            serialize.as_dir_tree(db, args.work_dir)


def entropy_handler(args):
    pass


def import_handler(args):
    from cast import chaos, serialize, importer
    with log.levelup():
        db = chaos.read(args.project)
        if args.input.endswith('.csv'):
            patch = importer.csv(db, args.input)

        with open(args.delta, 'w') as f:
            serialize.as_file_list(patch, f)

def split_path(path):
    src = os.path.abspath(path)
    return os.path.split(src)


def generate_handler(args):
    log.debug('loading project: {}'.format(args.project))
    log.debug('loading template: {}'.format(args.template))

    from cast import chaos

    filepath, filename = split_path(args.project)
    templatepath, templatefile = split_path(args.template)
    template = os.path.join(templatepath, templatefile)


    prs = chaos.load_prs(filepath, filename)
    with dirutil.work_safe_mkdir(filepath + '-products'):
        outfile = os.path.splitext(filename)[0] + '.' + os.path.splitext(templatefile)[0]
        chaos.render_prs(prs, template, outfile)

