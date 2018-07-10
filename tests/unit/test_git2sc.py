import json
import unittest
from unittest.mock import patch, Mock
from git2sc.git2sc import Git2SC


class TestGit2SC(unittest.TestCase):

    def setUp(self):
        self.api_url = 'https://confluence.sucks.com/wiki/rest/api'
        self.auth_string = 'user:password'
        self.auth = tuple(self.auth_string.split(':'))
        self.g = Git2SC(self.api_url, self.auth_string)

        self.requests_patch = patch('git2sc.git2sc.requests')
        self.requests = self.requests_patch.start()

        self.print_patch = patch('git2sc.git2sc.print')
        self.print = self.print_patch.start()

    def tearDown(self):
        self.requests.stop()
        self.print.stop()

    def test_has_auth_set(self):
        self.assertEqual(self.g.auth, self.auth)

    def test_has_empty_pages_by_default(self):
        self.assertEqual(self.g.pages, {})

    def test_has_confluence_url_set(self):
        self.assertEqual(self.g.api_url, self.api_url)

    def test_can_get_page_info(self):
        page_id = '372274410'
        result = self.g.get_page_info(page_id)
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
        self.assertTrue(self.requests.get.return_value.raise_for_status.called)
        self.assertEqual(result, self.requests.get.return_value.json())

    def test_can_get_space_homepage(self):
        space_id = 'TST'
        self.requests.get.return_value.json.return_value = {
            '_expandable': {'homepage': '/rest/api/content/372334010'},
        }
        result = self.g.get_space_homepage(space_id)
        self.assertEqual(
            self.requests.get.assert_called_with(
                '{}/space/{}'.format(
                    self.api_url,
                    space_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(self.requests.get.return_value.raise_for_status.called)
        self.assertEqual(result, '372334010')

    def test_can_get_space_articles(self):
        space_id = 'TST'
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
        self.g.get_space_articles(space_id)
        self.assertEqual(
            self.requests.get.assert_called_with(
                '{}/content/?spaceKey={}?expand='
                'ancestors,body.storage,version'.format(
                    self.api_url,
                    space_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(self.requests.get.return_value.raise_for_status.called)
        self.assertEqual(self.g.pages, desired_pages)

    def test_can_update_articles(self):
        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.g.pages = {}
        self.g.pages[page_id] = {
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
        self.g.update_page(page_id, html)

        data_json = json.dumps({
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
        })

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
        self.assertTrue(self.requests.put.return_value.raise_for_status.called)

    @patch('git2sc.git2sc.json')
    @patch('git2sc.git2sc.Git2SC.get_page_info')
    def test_can_update_articles_not_in_pages(self, getPageInfoMock, jsonMock):
        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.g.pages = {}
        self.g.update_page(page_id, html)
        self.assertEqual(getPageInfoMock.assert_called_with(page_id), None)

    def test_can_update_articles_with_title(self):
        page_id = '372274410'
        html = '<p> This is a test </p>'
        self.g.pages = {}
        self.g.pages[page_id] = {
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
        self.g.update_page(page_id, html, 'new title')
        self.assertEqual(self.g.pages[page_id]['title'], 'new title')

    def test_can_create_articles_as_parent(self):
        html = '<p> This is a new page </p>'
        self.g.create_page('TST', 'new title', html)

        data_json = json.dumps({
            'type': 'page',
            'title': 'new title',
            'space': {'key': 'TST'},
            'body': {
                'storage': {
                    'value': html,
                    'representation': 'storage'
                },
            },
        })

        self.assertEqual(
            self.requests.post.assert_called_with(
                '{}/content'.format(self.api_url),
                data=data_json,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
            ),
            None,
        )
        self.assertTrue(self.requests.post.return_value.raise_for_status.called)

    def test_can_create_articles_as_a_child(self):
        html = '<p> This is a new page </p>'
        parent_id = '372274410'
        self.g.create_page('TST', 'new title', html, parent_id)

        data_json = json.dumps({
            'type': 'page',
            'title': 'new title',
            'space': {'key': 'TST'},

            'ancestors': [{'id': parent_id}],
            'body': {
                'storage': {
                    'value': html,
                    'representation': 'storage'
                },
            },
        })

        self.assertEqual(
            self.requests.post.assert_called_with(
                '{}/content'.format(self.api_url),
                data=data_json,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
            ),
            None,
        )
        self.assertTrue(self.requests.post.return_value.raise_for_status.called)

    def test_request_error_display_message_if_rc_not_200(self):
        requests_object = Mock()
        requests_object.text = json.dumps({
            'statusCode': 400,
            'message': 'Error message',
        })
        self.g._requests_error(requests_object)
        self.assertEqual(
            self.print.assert_called_with(
                'Error 400: Error message'
            ),
            None,
        )

    def test_request_error_do_nothing_if_rc_is_200(self):
        requests_object = Mock()
        requests_object.text = json.dumps({
            'statusCode': 200,
            'message': 'Error message',
        })
        self.g._requests_error(requests_object)
        self.assertFalse(self.print.called)
