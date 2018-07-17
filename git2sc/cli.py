import argparse
import argcomplete


def load_parser():
    ''' Configure environment '''

    # Argparse
    parser = argparse.ArgumentParser(
        description="Synchronize a Confluence space with a "
        "git documentation repository"
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

    article_create_parser = article_command_parser.add_parser('create')
    article_create_parser.add_argument(
        "space",
        type=str,
        help='Confluence space id',
    )
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

    article_delete_parser = article_command_parser.add_parser('delete')
    article_delete_parser.add_argument(
        "article_id",
        type=str,
        help='Confluence article id',
    )

    argcomplete.autocomplete(parser)
    return parser
