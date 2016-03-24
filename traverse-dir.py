#!/usr/bin/python

# jude.quintana@gmail.com
#
# works with both python 2.7.11 and python 3.5.1
#
# $Id: takehome-exam.ph,v 1.3 2016/02/25 07:27:25 jquintana Exp jquintana $
# $Header: /Users/judequintana/SecureSet/systems/scripts/takehome-exam.py 1.3 jquintana Exp jquintana $

import os
import stat
import argparse
from datetime import datetime
from pwd import getpwuid


def cli_parse():
    parser = argparse.ArgumentParser(description='Lists out filename properties, use flags to filter')
    parser.add_argument('path', help='Input path or filename')
    parser.add_argument('-s', '--setuid', help='List all files with setuid bit set', action='store_true')
    parser.add_argument('-g', '--setgid', help='List all files with setgid bit set', action='store_true')
    parser.add_argument('-w', '--world_writable', help='List all files that are world writable', action='store_true')
    parser.add_argument('-l', '--last_modified', help='List all files modified in the last 24 hours',
                        action='store_true')

    args = parser.parse_args()

    return vars(args)


def deep_list_dir(args):
    messages = get_messages_for_file(args)
    print_messages(messages, args)

    if os.path.isdir(args['path']):
        list_ = os.listdir(args['path'])
    else:
        return

    current_path = args['path']

    for fn in list_:
        next_path = os.path.join(args['path'], fn)
        args['path'] = next_path

        deep_list_dir(args)
        args['path'] = current_path


def check_file_exists(path):
    if not os.path.isfile(path) and not os.path.isdir(path):
        print("File not found")
        exit(0)


def get_messages_for_file(args):
    messages = []

    if args.get('setuid'):
        messages.extend(check_file(args['path'], 'setuid'))
    if args.get('setgid'):
        messages.extend(check_file(args['path'], 'setgid'))
    if args.get('world_writable'):
        messages.extend(check_file(args['path'], 'world_writable'))
    if args.get('last_modified'):
        messages.extend(last_24_hrs(args['path']))

    return messages


def print_messages(messages, args):
    if len(messages) > 0:
        print_astericks()
        print_file_props(args['path'])

        for msg in messages:
            print(msg)

        print_astericks()

    elif no_flags_set(args):
        print_astericks()
        print_file_props(args['path'])
        print_astericks()


def check_file(path, mode):
    file_modes = {
        'setuid': stat.S_ISUID,
        'setgid': stat.S_ISGID,
        'world_writable': stat.S_IWOTH,
    }

    mode_set = os.stat(path).st_mode & file_modes[mode]

    if bool(mode_set):
        return ["Has %s set!" % mode]
    else:
        return []


def last_24_hrs(path):
    epoch = os.path.getmtime(path)
    last_modified = datetime.fromtimestamp(epoch)

    days_since_last_modified = (datetime.now() - last_modified).days

    if days_since_last_modified >= 1:
        return ["Has been %s day(s) since last modified" % str(days_since_last_modified)]
    else:
        return []


def print_file_props(path):
    file_stats = os.stat(path)
    stats = {'file_created': file_stats.st_ctime, 'file_modified': file_stats.st_mtime,
             'file_last_accessed': file_stats.st_atime, 'file_owner': file_stats.st_uid}

    print("File: %s" % path)
    print("file_owner: %s" % find_owner(stats['file_owner']))

    for attr, epoch in stats.items():
        if not attr == 'file_owner':
            print("%s : %s" % (attr, datetime.fromtimestamp(epoch)))
    print


def print_astericks():
    print('*' * 50)


def no_flags_set(args):
    flags_set = [v for k, v in args.items() if not k == 'path']
    return not any(flags_set)


def find_owner(_id):
    return getpwuid(_id).pw_name


def main():
    args = cli_parse()
    check_file_exists(args['path'])
    deep_list_dir(args)


if __name__ == '__main__':
    main()
