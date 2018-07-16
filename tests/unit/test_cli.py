import unittest
from git2sc.cli import load_parser


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_has_subcommand_article_update(self):
        '''Required to ensure that the parser is correctly configured to
        update an article as expected'''
        parsed = self.parser.parse_args(
            ['article', 'update', '1', 'index.html']
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'update')
        self.assertEqual(parsed.article_id, '1')
        self.assertEqual(parsed.content, 'index.html')

    def test_has_subcommand_article_create(self):
        '''Required to ensure that the parser is correctly configured to
        create an article as expected'''

        parsed = self.parser.parse_args(
            ['article', 'create', 'TST', 'new article', '<p>New article!</p>']
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'create')
        self.assertEqual(parsed.title, 'new article')
        self.assertEqual(parsed.space, 'TST')
        self.assertEqual(parsed.content, '<p>New article!</p>')
        self.assertEqual(parsed.parent_id, None)

    def test_has_subcommand_article_create_optional_parent_id(self):
        '''Required to ensure that the parser is correctly configured to
        create an article as a child of another article'''

        parsed = self.parser.parse_args(
            [
                'article',
                'create',
                '-p',
                '1111',
                'TST',
                'new article',
                '<p>New article!</p>',
            ]
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'create')
        self.assertEqual(parsed.title, 'new article')
        self.assertEqual(parsed.parent_id, '1111')
        self.assertEqual(parsed.space, 'TST')
        self.assertEqual(parsed.content, '<p>New article!</p>')
