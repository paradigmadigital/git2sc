#!/usr/bin/python
# git2sc: program to sync a git documentation repository to Confluence.
#
# Copyright (C) 2018 jamatute <jamatute@paradigmadigital.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
from git2sc.git2sc import Git2SC
from git2sc.cli import load_parser


def main():
    parser = load_parser()
    args = parser.parse_args()
    try:
        api_url = os.environ['GIT2SC_API_URL']
    except KeyError:
        print('GIT2SC_API_URL environmental variable not set')
        return

    try:
        auth = os.environ['GIT2SC_AUTH']
    except KeyError:
        print('GIT2SC_AUTH environmental variable not set')
        return

    g = Git2SC(api_url, auth, args.space)

    if args.subcommand == 'article':
        if args.article_command == 'delete':
            g.delete_page(args.article_id)
        else:
            if args.html:
                html = args.content
            else:
                html = g.import_file(args.content)
            if args.article_command == 'update':
                g.update_page(args.article_id, html)
            elif args.article_command == 'create':
                g.create_page(args.title, html, args.parent_id)

    elif args.subcommand == 'upload':
        g.directory_full_upload(args.path, args.exclude)


if __name__ == "__main__":
    main()
