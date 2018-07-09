import pytest
import unittest
from unittest.mock import MagicMock, patch, call
from git2sc.cli import load_parser


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_has_subcommand_article(self):
        parsed = self.parser.parse_args(['article', '1', 'index.html'])
        self.assertEqual(parsed.subcommand, 'article')
        self.assertEqual(parsed.article_id, '1')
        self.assertEqual(parsed.path_to_content, 'index.html')
