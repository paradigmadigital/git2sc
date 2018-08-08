import os
import json
import pytest
import unittest
from unittest.mock import patch, Mock, call
from git2sc.git2sc import Git2SC, UnknownExtension


class TestGit2SC(unittest.TestCase):
    '''Test class for the Git2SC class'''

    def setUp(self):
        self.api_url = 'https://confluence.sucks.com/wiki/rest/api'
        self.auth_string = 'user:password'
        self.auth = tuple(self.auth_string.split(':'))
        self.space = 'TST'
        self.git2sc = Git2SC(self.api_url, self.auth_string, self.space)

        self.requests_patch = patch('git2sc.git2sc.requests', autospect=True)
        self.requests = self.requests_patch.start()
        self.requests_error_patch = patch(
            'git2sc.git2sc.Git2SC._requests_error',
            autospect=True
        )
        self.requests_error = self.requests_error_patch.start()

        self.json_patch = patch('git2sc.git2sc.json', autospect=True)
        self.json = self.json_patch.start()

        self.os_patch = patch('git2sc.git2sc.os', autospect=True)
        self.os = self.os_patch.start()

    def tearDown(self):
        self.requests_patch.stop()
        self.requests_error_patch.stop()
        self.json_patch.stop()
        self.os_patch.stop()

    def test_has_auth_set(self):
        'Required attribute for some methods'

        self.assertEqual(self.git2sc.auth, self.auth)

    def test_has_space_set(self):
        'Required attribute for some methods'

        self.assertEqual(self.git2sc.space, self.space)

    def test_has_empty_pages_by_default(self):
        'Required to initialize the dictionary'

        self.assertEqual(self.git2sc.pages, {})

    def test_has_confluence_url_set(self):
        'Required attribute for some methods'

        self.assertEqual(self.git2sc.api_url, self.api_url)

    def test_can_get_page_info(self):
        '''Required to ensure that the get_page_info method calls the correct
        api endpoint and returns a json object'''

        page_id = '372274410'
        result = self.git2sc.get_page_info(page_id)
        self.assertEqual(
            self.requests.get.assert_called_with(
                '{}/content/{}?expand=ancestors,body.storage,version'.format(
                    self.api_url,
                    page_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)
        self.assertEqual(result, self.requests.get.return_value.json())

    def test_can_get_space_homepage(self):
        '''Required to ensure that the get_space_homepage method calls the
        correct api endpoint and returns the article id'''

        self.requests.get.return_value.json.return_value = {
            '_expandable': {'homepage': '/rest/api/content/372334010'},
        }
        result = self.git2sc.get_space_homepage()
        self.assertEqual(
            self.requests.get.assert_called_with(
                '{}/space/{}'.format(
                    self.api_url,
                    self.space,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)
        self.assertEqual(result, '372334010')

    def test_can_get_space_articles(self):
        '''Required to ensure that the get_space_articles method calls the
        correct api endpoint and returns a dictionary with the desired
        pages as a dictionary of dictionaries'''

        self.requests.get.return_value.json.return_value = {
            "results": [
                {
                    "id": "371111110",
                    "type": "page",
                    "status": "current",
                },
                {
                    "id": "372222220",
                    "type": "page",
                    "status": "current",
                },
            ]
        }
        desired_pages = {
            '371111110': {
                "id": "371111110",
                "type": "page",
                "status": "current",
            },
            '372222220': {
                "id": "372222220",
                "type": "page",
                "status": "current",
            },
        }
        self.git2sc.get_space_articles()
        self.assertEqual(
            self.requests.get.assert_called_with(
                '{}/content/?spaceKey={}?expand='
                'ancestors,body.storage,version'.format(
                    self.api_url,
                    self.space,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)
        self.assertEqual(self.git2sc.pages, desired_pages)

    def test_can_update_articles(self):
        '''Required to ensure that the update_page method posts to the
        correct api endpoint with the correct data structure '''

        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.git2sc.pages = {}
        self.git2sc.pages[page_id] = {
            'version': {
                'number': 1
            },
            'title': 'Test page title',
            'ancestors': [
                {
                    'ancestor': 'ancestor name',
                    '_links': 'link',
                    '_expandable': 'expandable',
                    'extensions': 'extensions',
                }
            ]
        }

        data = {
            'id': page_id,
            'type': 'page',
            'title': 'Test page title',
            'version': {'number': 2},
            'ancestors': [{'ancestor': 'ancestor name'}],
            'body': {
                'storage':
                {
                    'representation': 'storage',
                    'value': html,
                }
            }
        }
        data_json = json.dumps(data)
        self.json.dumps.return_value = data_json

        self.git2sc.update_page(page_id, html)

        self.assertEqual(
            self.requests.put.assert_called_with(
                '{}/content/{}'.format(
                    self.api_url,
                    page_id,
                ),
                data=data_json,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)

    @patch('git2sc.git2sc.Git2SC.get_page_info', autospect=True)
    def test_can_update_articles_not_in_pages(self, getPageInfoMock):
        '''Required to ensure that the update_page method can update a page
        even though the pages attribute is empty'''

        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.git2sc.pages = {}
        self.git2sc.update_page(page_id, html)
        self.assertEqual(getPageInfoMock.assert_called_with(page_id), None)

    def test_can_update_articles_with_title(self):
        '''Required to ensure that the update_page method can update a page
        specifying the title'''

        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.git2sc.pages = {}
        self.git2sc.pages[page_id] = {
            'version': {
                'number': 1
            },
            'title': 'Test page title',
            'ancestors': [
                {
                    'ancestor': 'ancestor name',
                    '_links': 'link',
                    '_expandable': 'expandable',
                    'extensions': 'extensions',
                }
            ]
        }
        self.git2sc.update_page(page_id, html, 'new title')
        self.assertEqual(self.git2sc.pages[page_id]['title'], 'new title')

    def test_can_create_articles_as_parent(self):
        '''Required to ensure that the create_page method posts to the
        correct api endpoint with the correct data structure if no
        inheritance is set'''

        html = '<p> This is a new page </p>'

        requests_data = {
            'type': 'page',
            'title': 'new title',
            'space': {'key': self.space},
            'body': {
                'storage': {
                    'value': html,
                    'representation': 'storage'
                },
            },
        }
        requests_data_json = json.dumps(requests_data)
        self.json.dumps.return_value = requests_data_json

        response_data = {'id': '412254212', 'type': 'page'}
        response_data_json = json.dumps(response_data)
        self.requests.post.return_value.text = response_data_json
        self.json.loads.return_value = response_data

        page_id = self.git2sc.create_page('new title', html)

        self.assertEqual(
            self.json.dumps.assert_called_with(requests_data),
            None,
        )
        self.assertEqual(
            self.requests.post.assert_called_with(
                '{}/content'.format(self.api_url),
                data=requests_data_json,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)
        self.assertEqual(
            self.json.loads.assert_called_with(response_data_json),
            None,
        )
        self.assertEqual(page_id, '412254212')

    def test_can_create_articles_as_a_child(self):
        '''Required to ensure that the create_page method posts to the
        correct api endpoint with the correct data structure if inheritance
        is set'''

        html = '<p> This is a new page </p>'
        parent_id = '372274410'

        requests_data = {
            'type': 'page',
            'ancestors': [{'id': parent_id}],
            'title': 'new title',
            'space': {'key': self.space},
            'body': {
                'storage': {
                    'value': html,
                    'representation': 'storage'
                },
            },
        }
        requests_data_json = json.dumps(requests_data)
        self.json.dumps.return_value = requests_data_json

        response_data = {'id': '412254212', 'type': 'page'}
        response_data_json = json.dumps(response_data)
        self.requests.post.return_value.text = response_data_json
        self.json.loads.return_value = response_data

        page_id = self.git2sc.create_page('new title', html, parent_id)

        self.assertEqual(
            self.json.dumps.assert_called_with(requests_data),
            None,
        )
        self.assertEqual(
            self.requests.post.assert_called_with(
                '{}/content'.format(self.api_url),
                data=requests_data_json,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
            ),
            None,
        )
        self.assertTrue(self.requests_error.called)
        self.assertEqual(
            self.json.loads.assert_called_with(response_data_json),
            None,
        )
        self.assertEqual(page_id, '412254212')

    @patch('git2sc.git2sc.shlex', autospect=True)
    def test_can_load_files_safely(self, shlexMock):
        '''Required to ensure that we can load files in a safe way'''
        path_to_file = '/path/to/file'

        self.git2sc._safe_load_file(path_to_file)

        self.assertEqual(
            shlexMock.quote.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            self.os.path.expanduser.assert_called_with(
                shlexMock.quote.return_value,
            ),
            None,
        )

    @patch('git2sc.git2sc.Git2SC._safe_load_file', autospect=True)
    @patch('git2sc.git2sc.subprocess', autospect=True)
    def test_can_process_adoc(self, subprocessMock, loadfileMock):
        '''Required to ensure that we can transform adoc files to html'''
        path_to_file = '/path/to/file.adoc'
        result = self.git2sc._process_adoc(path_to_file)

        self.assertEqual(
            loadfileMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            subprocessMock.check_output.assert_called_with(
                [
                    'asciidoctor',
                    '-b',
                    'xhtml',
                    loadfileMock.return_value,
                    '-o',
                    '-',
                ],
                shell=False,
            ),
            None,
        )
        self.assertEqual(
            result,
            subprocessMock.check_output.return_value.decode.
            return_value.replace('<!DOCTYPE html>\n', '')
        )

    @patch('git2sc.git2sc.Git2SC._safe_load_file', autospect=True)
    @patch('git2sc.git2sc.open', autospect=True)
    def test_can_process_html(self, openMock, loadfileMock):
        '''Required to ensure that we can load html files'''
        path_to_file = '/path/to/file.html'
        result = self.git2sc._process_html(path_to_file)

        self.assertEqual(
            loadfileMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            openMock.assert_called_with(
                loadfileMock.return_value,
                'r',
            ),
            None,
        )
        self.assertEqual(
            result,
            openMock.return_value.__enter__.return_value.read.return_value
        )

    @patch('git2sc.git2sc.Git2SC._safe_load_file', autospect=True)
    @patch('git2sc.git2sc.subprocess', autospect=True)
    def test_can_process_md(self, subprocessMock, loadfileMock):
        '''Required to ensure that we can transform md files to html'''
        path_to_file = '/path/to/file.md'
        result = self.git2sc._process_md(path_to_file)

        self.assertEqual(
            loadfileMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            subprocessMock.check_output.assert_called_with(
                [
                    'pandoc',
                    loadfileMock.return_value,
                    '-t',
                    'html',
                    '-o',
                    '-',
                ],
                shell=False,
            ),
            None,
        )
        self.assertEqual(
            result,
            subprocessMock.check_output.return_value.decode.return_value
        )

    @patch('git2sc.git2sc.Git2SC._process_adoc', autospect=True)
    def test_import_file_method_supports_adoc_files(self, adocMock):
        '''Required to ensure that the import_file method as a wrapper
        of the _process_* recognizes asciidoc files'''
        path_to_file = '/path/to/file.adoc'
        self.os.path.splitext.return_value = ['/path/to/file', '.adoc']
        html = self.git2sc.import_file(path_to_file)
        self.assertEqual(
            adocMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            html,
            adocMock.return_value
        )

    @patch('git2sc.git2sc.Git2SC._process_html', autospect=True)
    def test_import_file_method_supports_html_files(self, htmlMock):
        '''Required to ensure that the import_file method as a wrapper
        of the _process_* recognizes html files'''
        path_to_file = '/path/to/file.html'
        self.os.path.splitext.return_value = ['/path/to/file', '.html']
        html = self.git2sc.import_file(path_to_file)
        self.assertEqual(
            htmlMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            html,
            htmlMock.return_value
        )

    @patch('git2sc.git2sc.Git2SC._process_md', autospect=True)
    def test_import_file_method_supports_md_files(self, mdMock):
        '''Required to ensure that the import_file method as a wrapper
        of the _process_* recognizes markdown files'''
        path_to_file = '/path/to/file.md'
        self.os.path.splitext.return_value = ['/path/to/file', '.md']
        html = self.git2sc.import_file(path_to_file)
        self.assertEqual(
            mdMock.assert_called_with(path_to_file),
            None,
        )
        self.assertEqual(
            html,
            mdMock.return_value
        )

    def test_import_file_exits_gracefully_if_extension_unknown(self):
        '''Required to ensure that the import_file method doesn't crash if
        the extension is unknown'''
        path_to_file = '/path/to/file.unknown_extension'
        with self.assertRaises(UnknownExtension):
            self.git2sc.import_file(path_to_file)

    def test_can_delete_articles(self):
        '''Required to ensure that the delete_page method posts to the
        correct api endpoint with the correct data structure'''

        page_id = '372274410'
        self.requests.delete.return_value.status_code = 204

        self.git2sc.delete_page(page_id)

        self.assertEqual(
            self.requests.delete.assert_called_with(
                '{}/content/{}'.format(self.api_url, page_id),
                auth=self.auth,
            ),
            None,
        )
        self.assertFalse(self.requests_error.called)

    def test_delete_articles_calls_requests_error_if_rc_not_204(self):
        '''If the deletion of article works it returns a 204 as stated by the
        docs, we need to make sure that requests_error gets called otherwise'''

        page_id = '372274410'
        self.requests.delete.return_value.status_code = 404

        self.git2sc.delete_page(page_id)

        self.assertTrue(self.requests_error.called)

    @patch('git2sc.git2sc.Git2SC.create_page', autospect=True)
    @patch('git2sc.git2sc.Git2SC._process_directory_readme', autospect=True)
    @patch('git2sc.git2sc.Git2SC._process_mainpage', autospect=True)
    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    def test_can_full_upload_directory(
        self,
        importfileMock,
        mainpageMock,
        readmeMock,
        createpageMock,
    ):
        '''Given a directory path test that git2sc crawls all the files and
        uploads them to confluence.

        The repository structure is under tests/data:
        └── repository_example
            ├── formation
            │   ├── ansible
            │   │   ├── molecule
            │   │   │   ├── child_child_doc.adoc
            │   │   │   └── README.md
            │   │   └── README.md
            │   ├── excluded_dir
            │   │   └── excluded_file
            │   ├── formation_guide.adoc
            │   └── README.md
            ├── .git
            │   └── git_file
            ├── parent_article.adoc
            └── README.md

        It should ignore the .git and excluded_dir directories as they are in
        the excluded list
        '''

        def create_side_effect(directory_name, parent_id=None):
            return 'id_{}'.format(os.path.basename(directory_name))

        excluded_directories = ['.git', 'excluded_dir']
        readmeMock.side_effect = create_side_effect
        self.os.walk.side_effect = os.walk
        self.os.path.basename.side_effect = os.path.basename

        self.git2sc.directory_full_upload(
            'tests/data/repository_example',
            excluded_directories,
        )

        # Assert that the directories are created
        self.assertEqual(
            readmeMock.mock_calls,
            [
                call('tests/data/repository_example/formation'),
                call('tests/data/repository_example/formation/ansible'),
                call(
                    'tests/data/repository_example/formation/ansible/molecule'
                )
            ]
        )

        # Assert that the files are created
        self.assertEqual(
            createpageMock.mock_calls,
            [
                call('parent_article', importfileMock.return_value, None),
                call(
                    'formation_guide',
                    importfileMock.return_value,
                    'id_formation'
                ),
                call(
                    'child_child_doc',
                    importfileMock.return_value,
                    'id_molecule'
                )
            ]
        )

        # Assert that the homepage is created
        self.assertEqual(mainpageMock.assert_called_with(), None)

    @patch('git2sc.git2sc.Git2SC.create_page', autospect=True)
    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    @pytest.mark.skip('Not yet implemented')
    def test_can_full_upload_directory_hanging_from_parent_article(
        self,
        importfileMock,
        createpageMock,
    ):
        pass

    @patch('git2sc.git2sc.Git2SC.update_page', autospect=True)
    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    @patch('git2sc.git2sc.Git2SC.get_space_homepage', autospect=True)
    def test_can_import_mainpage(
        self,
        gethomepageMock,
        importfileMock,
        updatepageMock,
    ):
        '''Given a root directory path test that git2sc substitutes the homepage
        of the confluence page with the README.adoc
        '''

        gethomepageMock.return_value = '372223610'
        importfileMock.return_value = '<p> This is a test </p>'

        self.git2sc._process_mainpage('README.adoc')

        self.assertEqual(
            gethomepageMock.assert_called_with(),
            None,
        )
        self.assertEqual(
            importfileMock.assert_called_with('README.adoc'),
            None,
        )
        self.assertEqual(
            updatepageMock.assert_called_with(
                gethomepageMock.return_value,
                importfileMock.return_value,
            ),
            None,
        )

    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    def test_can_discover_directory_readme_adoc(self, importfileMock):
        '''Given a directory path test that git2sc returns the html of the
        README.adoc file'''

        directory_path = '/path/to/directory'
        self.os.path.join.side_effect = os.path.join
        self.os.path.basename.side_effect = os.path.basename

        def true_if_adoc(file_path):
            extension = os.path.splitext(file_path)[-1]
            if extension == '.adoc':
                return True
            return False

        self.os.path.isfile.side_effect = true_if_adoc

        result = self.git2sc._discover_directory_readme(directory_path)

        self.assertTrue(
            call(directory_path, 'README.adoc')
            in self.os.path.join.mock_calls
        )

        self.assertEqual(
            importfileMock.assert_called_with('/path/to/directory/README.adoc'),
            None,
        )
        self.assertEqual(
            result,
            importfileMock.return_value
        )

    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    def test_can_discover_directory_readme_md(self, importfileMock):
        '''Given a directory path test that git2sc returns the html of the
        README.md file'''

        directory_path = '/path/to/directory'
        self.os.path.join.side_effect = os.path.join
        self.os.path.basename.side_effect = os.path.basename

        def true_if_md(file_path):
            extension = os.path.splitext(file_path)[-1]
            if extension == '.md':
                return True
            return False

        self.os.path.isfile.side_effect = true_if_md

        result = self.git2sc._discover_directory_readme(directory_path)

        self.assertTrue(
            call(directory_path, 'README.md')
            in self.os.path.join.mock_calls
        )

        self.assertEqual(
            importfileMock.assert_called_with('/path/to/directory/README.md'),
            None,
        )
        self.assertEqual(
            result,
            importfileMock.return_value
        )

    @patch('git2sc.git2sc.Git2SC.create_page', autospect=True)
    @patch('git2sc.git2sc.Git2SC._discover_directory_readme', autospect=True)
    def test_can_process_directory_readme(
        self,
        discoverreadmeMock,
        createpageMock,
    ):
        '''Given a directory path test that git2sc creates a page with the
        contents of README being the title the name of the directory'''

        directory_path = '/path/to/directory'
        createpageMock.return_value = '372223610'
        self.os.path.join.side_effect = os.path.join
        self.os.path.basename.side_effect = os.path.basename

        result = self.git2sc._process_directory_readme(directory_path)

        self.assertEqual(
            discoverreadmeMock.assert_called_with(
                '/path/to/directory',
            ),
            None,
        )
        self.assertEqual(
            createpageMock.assert_called_with(
                'directory',
                discoverreadmeMock.return_value,
                None,
            ),
            None
        )
        self.assertEqual(
            result,
            createpageMock.return_value,
        )

    @patch('git2sc.git2sc.Git2SC.create_page', autospect=True)
    @patch('git2sc.git2sc.Git2SC.import_file', autospect=True)
    def test_process_directory_readme_can_accept_parent_id(
        self,
        importfileMock,
        createpageMock,
    ):
        '''Given a directory path test that git2sc creates a page with the
        contents of README.md under a specified article id'''

        directory_path = '/path/to/directory'
        parent_id = '372223610'
        self.os.path.join.side_effect = os.path.join
        self.os.path.basename.side_effect = os.path.basename

        def true_if_md(file_path):
            extension = os.path.splitext(file_path)[-1]
            if extension == '.md':
                return True
            return False

        self.os.path.isfile.side_effect = true_if_md

        self.git2sc._process_directory_readme(directory_path, parent_id)

        self.assertEqual(
            createpageMock.assert_called_with(
                'directory',
                importfileMock.return_value,
                parent_id
            ),
            None
        )

class TestGit2SC_requests_error(unittest.TestCase):
    '''Test class for the Git2SC _requests_error method'''

    def setUp(self):
        self.api_url = 'https://confluence.sucks.com/wiki/rest/api'
        self.auth_string = 'user:password'
        self.auth = tuple(self.auth_string.split(':'))
        self.space = 'TST'
        self.git2sc = Git2SC(self.api_url, self.auth_string, self.space)

        self.requests_object = Mock()

        self.print_patch = patch('git2sc.git2sc.print', autospect=True)
        self.print = self.print_patch.start()

    def tearDown(self):
        self.print.stop()

    def test_request_error_display_message_if_rc_not_200(self):
        '''Required to ensure that the _requests_error method returns the
        desired structure inside the print when a requests instance has a
        return code different from 200'''

        self.requests_object.status_code = 400
        self.requests_object.text = json.dumps({
            'statusCode': 400,
            'message': 'Error message',
        })
        self.git2sc._requests_error(self.requests_object)
        self.assertEqual(
            self.print.assert_called_with(
                'Error 400: Error message'
            ),
            None,
        )

    def test_request_error_do_nothing_if_rc_is_200(self):
        '''Required to ensure that the _requests_error method does nothing
        if the return code is 200'''

        self.requests_object.status_code = 200
        self.requests_object.text = json.dumps({
            'statusCode': 200,
            'message': 'Error message',
        })
        self.git2sc._requests_error(self.requests_object)
        self.assertFalse(self.print.called)
