from git2sc.git2sc import Git2SC
import pytest
import unittest
from unittest.mock import patch


class TestGit2SC(unittest.TestCase):

    def setUp(self):
        self.api_url = 'https://confluence.sucks.com/wiki/rest/api'
        self.auth = 'user:password'
        self.g = Git2SC(self.api_url, self.auth)

    def test_has_auth_set(self):
        self.assertEqual(self.g.auth, self.auth)

    def test_has_confluence_url_set(self):
        self.assertEqual(self.g.api_url, self.api_url)

    @patch('git2sc.git2sc.requests.get')
    def test_can_get_page_info(self, requestMock):
        page_id = '372274410'
        result = self.g.get_page_info(page_id)
        self.assertEqual(
            requestMock.assert_called_with(
                '{}/content/{}?expand=ancestors,body.storage'.format(
                    self.api_url,
                    page_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(requestMock.return_value.raise_for_status.called)
        self.assertEqual(result, requestMock.return_value.json())

    @patch('git2sc.git2sc.requests.get')
    def test_can_get_space_homepage(self, requestMock):
        space_id = 'TST'
        requestMock.return_value.json.return_value = {
            '_expandable': {'homepage': '/rest/api/content/372334010'},
        }
        result = self.g.get_space_homepage(space_id)
        self.assertEqual(
            requestMock.assert_called_with(
                '{}/space/{}'.format(
                    self.api_url,
                    space_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(requestMock.return_value.raise_for_status.called)
        self.assertEqual(result, '372334010')

    @patch('git2sc.git2sc.requests.get')
    def test_can_get_space_articles(self, requestMock):
        space_id = 'TST'
        requestMock.return_value.json.return_value = {
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
            requestMock.assert_called_with(
                '{}/content/?spaceKey={}?expand=ancestors,body.storage'.format(
                    self.api_url,
                    space_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(requestMock.return_value.raise_for_status.called)
        self.assertEqual(self.g.pages, desired_pages)

    @pytest.mark.skip()
    @patch('git2sc.git2sc.requests.get')
    def test_can_update_articles(self, requestMock):
        page_id = '372274410'
        html = '<p> This is a test </p>'
        result = self.g.update_page(page_id, html)
        self.assertEqual(
            requestMock.assert_called_with(
                '{}/content/{}'.format(
                    self.api_url,
                    page_id,
                ),
                auth=self.auth
            ),
            None,
        )
        self.assertTrue(requestMock.return_value.raise_for_status.called)
        self.assertEqual(result, requestMock.return_value.json())
