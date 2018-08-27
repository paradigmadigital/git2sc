import unittest
from git2sc.cli import load_parser


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_has_subcommand_article_update(self):
        '''Required to ensure that the parser is correctly configured to
        update an article as expected'''
        parsed = self.parser.parse_args(
            [
                'TST',
                'article',
                'update',
                '--html',
                '1',
                '<p>Updated article</p>'
            ]
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'update')
        self.assertEqual(parsed.article_id, '1')
        self.assertEqual(parsed.content, '<p>Updated article</p>')
        self.assertEqual(parsed.html, True)

    def test_has_subcommand_article_create(self):
        '''Required to ensure that the parser is correctly configured to
        create an article as expected'''

        parsed = self.parser.parse_args(
            [
                'TST',
                'article',
                'create',
                '--html',
                'new article',
                '<p>New article!</p>',
            ]
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'create')
        self.assertEqual(parsed.title, 'new article')
        self.assertEqual(parsed.space, 'TST')
        self.assertEqual(parsed.content, '<p>New article!</p>')
        self.assertEqual(parsed.parent_id, None)
        self.assertEqual(parsed.html, True)

    def test_has_subcommand_article_create_optional_parent_id(self):
        '''Required to ensure that the parser is correctly configured to
        create an article as a child of another article'''

        parsed = self.parser.parse_args(
            [
                'TST',
                'article',
                'create',
                '--html',
                '-p',
                '1111',
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
        self.assertEqual(parsed.html, True)

    def test_create_has_file_flag(self):
        '''Required to ensure that the parser is correctly configured to
        create an article from a file by default'''

        parsed = self.parser.parse_args(
            [
                'TST',
                'article',
                'create',
                'new article',
                '/path/to/article',
            ]
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'create')
        self.assertEqual(parsed.title, 'new article')
        self.assertEqual(parsed.space, 'TST')
        self.assertEqual(parsed.html, False)
        self.assertEqual(parsed.content, '/path/to/article')

    def test_has_subcommand_article_delete(self):
        '''Required to ensure that the parser is correctly configured to
        update an article as expected'''

        parsed = self.parser.parse_args(
            ['TST', 'article', 'delete', '1']
        )
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_command, 'delete')
        self.assertEqual(parsed.space, 'TST')
        self.assertEqual(parsed.article_id, '1')

    def test_has_subcommand_upload_directory(self):
        '''Required to ensure that the parser is correctly configured to
        upload a directory'''
        parsed = self.parser.parse_args(
            [
                'TST',
                'upload',
                '/path/to/directory',
            ]
        )
        self.assertEqual(parsed.subcommand, 'upload')
        self.assertEqual(parsed.path, '/path/to/directory')
        self.assertEqual(parsed.exclude, ['.git', '.gitignore', '.gitmodules'])

    def test_has_subcommand_upload_directory_can_specify_excluded_dirs(self):
        '''Required to ensure that the parser is correctly configured to
        upload a directory with excluded directories'''
        parsed = self.parser.parse_args(
            [
                'TST',
                'upload',
                '/path/to/directory',
                '--exclude',
                'excluded_dir1',
                'excluded_dir2',
            ]
        )
        self.assertEqual(parsed.exclude, ['excluded_dir1', 'excluded_dir2'])

    def test_has_subcommand_upload_directory_can_specify_parent_id(self):
        '''Required to ensure that the parser is correctly configured to
        upload a directory to a parent article'''
        parsed = self.parser.parse_args(
            [
                'TST',
                'upload',
                '/path/to/directory',
                '-p',
                'parent_id',
            ]
        )
        self.assertEqual(parsed.parent_id, 'parent_id')
