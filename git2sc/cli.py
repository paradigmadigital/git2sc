import argparse
import argcomplete


def load_parser():
    ''' Configure environment '''

    # Argparse
    parser = argparse.ArgumentParser(
        description="Synchronize a Confluence space with a "
        "git documentation repository"
    )
    parser.add_argument(
        "space",
        type=str,
        help='Confluence space id',
    )

    subcommand_parser = parser.add_subparsers(
        dest='subcommand',
        help='Git2SC Subcommands',
    )
    subcommand_parser.required = True

    article_parser = subcommand_parser.add_parser('article')
    article_command_parser = article_parser.add_subparsers(
        dest='article_command',
        help='Article command',
        )

    article_update_parser = article_command_parser.add_parser('update')
    article_update_parser.add_argument(
        "article_id",
        type=str,
        help='Confluence article id',
    )
    article_update_parser.add_argument(
        "content",
        help="HTML content for the page",
    )
    article_update_parser.add_argument(
        "--html",
        action="store_true",
        help='Content is html and not a path',
    )

    article_create_parser = article_command_parser.add_parser('create')
    article_create_parser.add_argument(
        "title",
        type=str,
        help='Confluence article title',
    )
    article_create_parser.add_argument(
        "content",
        help="HTML content for the page",
    )
    article_create_parser.add_argument(
        "-p",
        "--parent_id",
        type=str,
        nargs='?',
        default=None,
        help="Parent id of the article to create",
    )
    article_create_parser.add_argument(
        "--html",
        action="store_true",
        help='Content is html and not a path',
    )

    article_delete_parser = article_command_parser.add_parser('delete')
    article_delete_parser.add_argument(
        "article_id",
        type=str,
        help='Confluence article id',
    )

    upload_parser = subcommand_parser.add_parser('upload')
    upload_parser.add_argument(
        "path",
        type=str,
        help='Path to directory',
    )

    upload_parser.add_argument(
        "--exclude",
        nargs='*',
        default=['.git', '.gitignore', '.gitmodules'],
        help="List of directories to exclude",
    )
    upload_parser.add_argument(
        "-p",
        "--parent_id",
        type=str,
        nargs='?',
        default=None,
        help="Parent id of the article to create",
    )
    sync_parser = subcommand_parser.add_parser('sync')
    sync_parser.add_argument(
        "path",
        type=str,
        help='Path to directory',
    )

    sync_parser.add_argument(
        "--exclude",
        nargs='*',
        default=['.git', '.gitignore', '.gitmodules'],
        help="List of directories to exclude",
    )

    argcomplete.autocomplete(parser)
    return parser
