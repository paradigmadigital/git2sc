import argparse
import argcomplete


def load_parser():
    ''' Configure environment '''

    # Argparse
    parser = argparse.ArgumentParser(
        description="Synchronize a Confluence space with a "
        "git documentation repository"
    )

    subparser = parser.add_subparsers(dest='subcommand', help='subcommands')
    subparser.required = True

    article_parser = subparser.add_parser('article')
    article_parser.add_argument(
        "article_id",
        type=str,
        help='Confluence article id',
    )
    article_parser.add_argument(
        "content",
        help="HTML content for the page",
    )
    # article_parser.add_argument(
    #     "content_path",
    #     help="Path to the file with the content to upload",
    # )

    argcomplete.autocomplete(parser)
    return parser
