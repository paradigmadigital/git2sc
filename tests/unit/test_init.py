import unittest
from unittest.mock import patch, PropertyMock

from git2sc import main


class TestMain(unittest.TestCase):
    def setUp(self):
        self.os_patch = patch('git2sc.os')
        self.os = self.os_patch.start()
        self.env = PropertyMock(
            return_value={
                'GIT2SC_AUTH': 'user:password',
                'GIT2SC_API_URL': 'https://confluence.sucks.com/wiki/rest/api',
            },
        )
        type(self.os).environ = self.env

        self.load_parser_patch = patch('git2sc.load_parser')
        self.load_parser = self.load_parser_patch.start()
        self.args = self.load_parser.return_value.parse_args.return_value

        self.print_patch = patch('git2sc.print')
        self.print = self.print_patch.start()

        self.git2sc_patch = patch('git2sc.Git2SC', autospect=True)
        self.git2sc = self.git2sc_patch.start()

    def tearDown(self):
        self.os_patch.stop()
        self.load_parser_patch.stop()
        self.print_patch.stop()
        self.git2sc_patch.stop()

    def test_main_loads_parser(self):
        '''Required to ensure that the main program load the parser'''

        self.load_parser.parse_args = True
        main()
        self.assertTrue(self.load_parser.called)

    def test_main_loads_gives_error_if_no_url_in_env(self):
        '''Required to ensure that the main program will fail if
        the environmental variable GIT2SC_API_URL is not set'''

        type(self.os).environ = PropertyMock(
            return_value={
                'GIT2SC_AUTH': 'user:password',
            },
        )
        main()
        self.assertEqual(
            self.print.assert_called_with(
                'GIT2SC_API_URL environmental variable not set'
            ),
            None,
        )

    def test_main_loads_gives_error_if_no_auth_in_env(self):
        '''Required to ensure that the main program will fail if
        the environmental variable GIT2SC_AUTH is not set'''

        type(self.os).environ = PropertyMock(
            return_value={
                'GIT2SC_API_URL': 'https://confluence.sucks.com/wiki/rest/api',
            },
        )
        main()
        self.assertEqual(
            self.print.assert_called_with(
                'GIT2SC_AUTH environmental variable not set'
            ),
            None,
        )

    def test_main_loads_url_and_auth_from_env(self):
        '''Required to ensure that the main program loads the GIT2SC_AUTH and
        GIT2SC_API_URL variables from the environment, I know it's not the
        perfect test but didn't manage to do any other way'''

        main()
        self.assertEqual(self.env.call_count, 2)

    def test_main_loads_git2sc_object(self):
        '''Required to ensure that the main program load the git2sc object'''

        main()
        self.assertEqual(
            self.git2sc.assert_called_with(
                'https://confluence.sucks.com/wiki/rest/api',
                'user:password',
            ),
            None,
        )
        self.assertTrue(self.git2sc.called)

    def test_article_update_subcommand_with_html(self):
        '''Required to ensure that the main program reacts as expected when
        called with the update page arguments'''

        self.args.subcommand = 'article'
        self.args.article_command = 'update'
        self.args.html = True
        self.args.article_id = '1'
        self.args.content = '<p> This is a test </p>'

        main()
        self.assertEqual(
            self.git2sc.return_value.update_page.assert_called_with(
                self.args.article_id,
                self.args.content,
            ),
            None
        )

    def test_article_create_subcommand_with_html(self):
        self.args.subcommand = 'article'
        self.args.article_command = 'create'
        self.args.title = 'new article'
        self.args.space = 'TST'
        self.args.content = '<p>New article!</p>'
        self.args.parent_id = None
        self.args.html = True

        main()
        self.assertEqual(
            self.git2sc.return_value.create_page.assert_called_with(
                self.args.space,
                self.args.title,
                self.args.content,
                self.args.parent_id,
            ),
            None
        )

    def test_article_create_children_article_with_html(self):
        self.args.subcommand = 'article'
        self.args.article_command = 'create'
        self.args.title = 'new article'
        self.args.parent_id = '1111'
        self.args.space = 'TST'
        self.args.content = '<p>New article!</p>'
        self.args.html = True

        main()
        self.assertEqual(
            self.git2sc.return_value.create_page.assert_called_with(
                self.args.space,
                self.args.title,
                self.args.content,
                self.args.parent_id,
            ),
            None
        )

    def test_article_update_subcommand_with_file(self):
        '''Required to ensure that by default the update command expects a path
        to a file containing the article'''
        self.args.subcommand = 'article'
        self.args.article_command = 'update'
        self.args.html = False
        self.args.article_id = '1'
        self.args.content = '/path/to/file'

        main()
        self.assertEqual(
            self.git2sc.return_value.import_file.assert_called_with(
                self.args.content,
            ),
            None
        )
        self.assertEqual(
            self.git2sc.return_value.update_page.assert_called_with(
                self.args.article_id,
                self.git2sc.return_value.import_file.return_value,
            ),
            None
        )

    def test_article_create_subcommand_with_file(self):
        '''Required to ensure that by default the create command expects a path
        to a file containing the article'''
        self.args.subcommand = 'article'
        self.args.article_command = 'create'
        self.args.title = 'new article'
        self.args.space = 'TST'
        self.args.content = '/path/to/file'
        self.args.parent_id = None
        self.args.html = False

        main()
        self.assertEqual(
            self.git2sc.return_value.import_file.assert_called_with(
                self.args.content,
            ),
            None
        )
        self.assertEqual(
            self.git2sc.return_value.create_page.assert_called_with(
                self.args.space,
                self.args.title,
                self.git2sc.return_value.import_file.return_value,
                self.args.parent_id,
            ),
            None
        )
