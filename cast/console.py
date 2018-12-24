# @author   d.dolzhenko@gmail.com

import sys, traceback, argparse
from cast import log 


def main():
    try:
        # create parsers tree
        parser = argparse.ArgumentParser(prog='cast', description='Order in Chaos')
        parser.add_argument('--verbose', '-v', action='count')
        subparsers = parser.add_subparsers()
        parser_verify   = subparsers.add_parser('verify',   help='verifies project')
        parser_cutify   = subparsers.add_parser('cutify',   help='cutifies project')
        parser_query    = subparsers.add_parser('query',    help='similar to xpath queries')
        parser_update   = subparsers.add_parser('update',   help='update chaos database')
        parser_entropy  = subparsers.add_parser('entropy',  help='estimate entropy')

        # verify    
        parser_verify.add_argument('project', type=str, help='project path')
        parser_verify.set_defaults(func=verify)

        # cutify
        parser_cutify.add_argument('project', type=str, help='input project to cutify')
        parser_cutify.add_argument('output', type=str, help='output') # OPTIONAL, default inplace
        parser_cutify.set_defaults(func=cutify)

        # query
        parser_query.add_argument('project', type=str, help='input project')
        parser_query.add_argument('query', type=str, help='query string')
        parser_query.add_argument('output', type=str, help='output path') # OPTONAL default stdonly
        parser_query.set_defaults(func=query)

        # update
        parser_update.add_argument('patch', type=str, help='input project')
        parser_update.add_argument('project', type=str, help='query string')
        parser_update.add_argument('--preview', action='store_true', help='only preview impact')
        parser_update.set_defaults(func=update)

        # entropy
        parser_entropy.add_argument('project', type=str, help='project')
        parser_entropy.set_defaults(func=entropy)

        # import

        # parse some argument lists
        args = parser.parse_args()
        args.func(args)

    except Exception as e:
        log.error('<{}>: {}'.format(sys.exc_info()[0], e))
        log.debug(traceback.format_exc())
        print('\nProcess interrupted. Please see "detailed.log" file for details\n')


def verify(args):
    print ('verify...............')
    pass
def cutify(args):
    pass
def query(args):
    pass
def update(args):
    pass
def entropy(args):
    pass
