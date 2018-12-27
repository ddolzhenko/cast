# @author   d.dolzhenko@gmail.com

import sys, traceback, argparse
from cast import log 


def main():
    try:
        # create parsers tree
        parser = argparse.ArgumentParser(prog='cast', description='Order in Chaos')
        parser.add_argument('--verbose', '-v', action='count')
        subparsers = parser.add_subparsers()
        parser_judge    = subparsers.add_parser('judge',   help='evaluates project')
        parser_cutify   = subparsers.add_parser('cutify',   help='cutifies project')
        parser_query    = subparsers.add_parser('query',    help='similar to xpath queries')
        parser_update   = subparsers.add_parser('update',   help='update chaos database')
        parser_entropy  = subparsers.add_parser('entropy',  help='estimate entropy')

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

        # parse some argument lists
        args = parser.parse_args()
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
