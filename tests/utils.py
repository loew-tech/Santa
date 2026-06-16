import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from santas_bag.utils import *


class TestUtils(unittest.TestCase):

    @patch('santas_bag.utils._fetch_official_input')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_read_input_cached(self, mock_read, mock_exists, mock_fetch):
        """Verify that if the file exists, it returns cached data without fetching."""
        mock_exists.return_value = True
        mock_read.return_value = "line1\nline2"

        result = read_input(2026, 1, "test_session", delim='\n')

        self.assertEqual(result, ["line1", "line2"])
        mock_fetch.assert_not_called()

    @patch('requests.get')
    def test_fetch_official_input_success(self, mock_get):
        """Verify official input fetching handles successful responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "data"
        mock_get.return_value = mock_response

        # We mock the .env file check to avoid actual FS interaction
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='session=secret')):
                from santas_bag.utils import _fetch_official_input
                result = _fetch_official_input(1, 2026, "123")
                self.assertEqual(result, "data")

    @patch('requests.get')
    def test_fetch_test_input_parsing(self, mock_get):
        """Verify scraper correctly extracts data from <pre> blocks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><pre>test_data</pre></body></html>"
        mock_get.return_value = mock_response

        from santas_bag.utils  import _fetch_test_input
        result = _fetch_test_input(1, 2026)
        self.assertEqual(result, "test_data")

    def test_process_input_parsing(self):
        """Verify the parser callback is applied correctly."""
        from santas_bag.utils  import _process_input
        text = "1\n2\n3"
        result = _process_input(text, '\n', int)
        self.assertEqual(result, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()