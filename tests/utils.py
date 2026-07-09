import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import time

from santas_bag.utils import *
from santas_bag.utils import _fetch_expected


class TestUtils(unittest.TestCase):

    @patch('santas_bag.utils.read_input')
    def test_get_read_input_factory(self, mock_read_input):
        """Verify get_read_input returns a function that calls read_input with captured defaults."""
        # 1. Setup the factory
        read_func = get_read_input(year=2026, session_id='my_session')

        # 2. Mock a return value for the inner read_input call
        mock_read_input.return_value = ["mocked_data"]

        # 3. Call the returned function
        result = read_func(day=1, testing=True)

        # 4. Assert that read_input was called with the combined arguments
        # (factory args + function call args)
        mock_read_input.assert_called_once_with(
            2026, 1, 'my_session', None, None, '\n', None, True, 1
        )
        self.assertEqual(result, ["mocked_data"])

    @patch('santas_bag.utils.read_input')
    def test_get_read_input_overrides(self, mock_read_input):
        """Verify that individual calls to the returned function can pass custom parsers."""
        read_func = get_read_input(2026, 'session_123')

        my_parser = lambda x: [int(i) for i in x]

        # Call the function
        read_func(day=5, parse=my_parser)

        # Access call_args
        args, kwargs = mock_read_input.call_args

        # Based on your signature:
        # read_input(year, day, session_id, inputs_path, tests_path, delim, parse, testing)
        # Arguments are:
        # [0]=2026, [1]=5, [2]='session_123', [3]=None, [4]=None, [5]='\n', [6]=my_parser, [7]=False

        self.assertEqual(args[6], my_parser)

    @patch('santas_bag.utils._fetch_official_input')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_read_input_cached(self, mock_read, mock_exists, mock_fetch):
        """Verify that if the file exists, it returns cached data without fetching."""
        mock_exists.return_value = True
        mock_read.return_value = "line1\nline2"

        result = read_input(2026, 1, "test_session", delim='\n')

        self.assertEqual(["line1", "line2"], result)
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
                self.assertEqual("data", result)

    @patch('requests.get')
    def test_fetch_test_input_parsing(self, mock_get):
        """Verify scraper correctly extracts data from <pre> blocks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><pre>test_data</pre></body></html>"
        mock_get.return_value = mock_response

        from santas_bag.utils  import _fetch_test_input
        result = _fetch_test_input(1, 2026)
        self.assertEqual("test_data", result)

    def test_process_input_parsing(self):
        """Verify the parser callback is applied correctly."""
        from santas_bag.utils  import _process_input
        text = "1\n2\n3"
        result = _process_input(text, '\n', int)
        self.assertEqual([1, 2, 3], result)

    @patch('requests.get')
    def test_fetch_test_input_http_error(self, mock_get):
        """Verify _fetch_test_input raises Exception on non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        from santas_bag.utils import _fetch_test_input
        with self.assertRaisesRegex(Exception, 'Failed to fetch puzzle page'):
            _fetch_test_input(2026, 1)

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('santas_bag.utils._fetch_test_input', return_value="mock_test_content")
    @patch('santas_bag.utils._fetch_expected')
    @patch('builtins.print')
    @patch('pathlib.Path.exists', return_value=False)
    def test_read_input_testing_mode_triggers_scraping(
            self, mock_exists, mock_print, mock_expected, mock_fetch_input, mock_write, mock_mkdir
    ):
        """Verify that testing=True triggers fetching and directory creation safely in-memory."""
        read_input(2026, 1, 'session', part=1, testing=True)

        mock_mkdir.assert_called_once()
        mock_fetch_input.assert_called_once()
        mock_expected.assert_called_once()
        mock_print.assert_called()

    @patch('pathlib.Path.read_text', return_value="dummy_data")
    @patch('pathlib.Path.exists', return_value=True)
    @patch('santas_bag.utils._fetch_expected')
    def test_read_input_skips_fetch_if_exists(self, mock_fetch, mock_exists, mock_read):
        """Verify _fetch_expected is NOT called when the file already exists."""
        read_input(2026, 1, 'session', testing=True, part=1)
        mock_fetch.assert_not_called()

    @patch('requests.get')
    def test_fetch_test_input_no_pre_block(self, mock_get):
        """Verify _fetch_test_input raises Exception when <pre> is missing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Valid HTML but no <pre> tag
        mock_response.content = b"<html><body><p>No code here</p></body></html>"
        mock_get.return_value = mock_response

        from santas_bag.utils import _fetch_test_input
        with self.assertRaisesRegex(Exception, 'Could not automatically find a test case'):
            _fetch_test_input(2026, 1)

    def test_process_input_custom_delimiter(self):
        """Verify processing with a custom delimiter (e.g., comma-separated)."""
        from santas_bag.utils import _process_input

        # Test with custom delimiter and no parser
        text = "1,2,3"
        result = _process_input(text, delim=',', parse=None)
        self.assertEqual(result, ["1", "2", "3"])

        # Test with custom delimiter and a parser
        result = _process_input(text, delim=',', parse=int)
        self.assertEqual(result, [1, 2, 3])

    def test_process_input_no_delimiter(self):
        """Verify processing when delim is None (raw processing)."""
        from santas_bag.utils import _process_input

        # Test with no delimiter and no parser (returns raw text)
        text = "some raw text"
        result = _process_input(text, delim=None, parse=None)
        self.assertEqual(result, "some raw text")

        # Test with no delimiter but with a parser
        # Example: parsing a raw string into a list of characters
        result = _process_input("abc", delim=None, parse=list)
        self.assertEqual(result, ['a', 'b', 'c'])

    def test_process_input_trailing_newline_stripping(self):
        """Verify that the function correctly strips the trailing newline."""
        from santas_bag.utils import _process_input

        # '1,2,3\n' should become ['1', '2', '3']
        result = _process_input("1,2,3\n", delim=',', parse=None)
        self.assertEqual(result, ["1", "2", "3"])

    @patch('time.perf_counter')
    def test_time_execution(self, mock_perf):
        """Verify the decorator calls the function and logs the correct duration."""
        # 1. Setup mock time: return 1.0 on first call, 2.5 on second call
        mock_perf.side_effect = [1.0, 2.5]

        # 2. Define a test function to be decorated
        @time_execution
        def sample_func(x, y=0):
            return x + y

        # 3. Call the decorated function
        with patch('builtins.print') as mock_print:
            result = sample_func(10, y=5)

            # Verify result is passed through correctly
            self.assertEqual(15, result)

            # Verify the print statement happened (the time calculation)
            # Duration should be 2.5 - 1.0 = 1.5
            mock_print.assert_called_with("⏱️ Execution time for sample_func: 1.5000 seconds")

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.read_text', return_value="dummy_data")
    @patch('pathlib.Path.exists', return_value=False)
    @patch('santas_bag.utils._fetch_expected')
    def test_read_input_fetches_expected_if_missing(
            self, mock_fetch, mock_exists, mock_read, mock_write
    ):
        """Verify _fetch_expected IS called when the file is missing."""
        # We also mock _fetch_test_input to prevent network calls
        with patch('santas_bag.utils._fetch_test_input', return_value="data"):
            read_input(2026, 1, 'session', testing=True, part=1)
            mock_fetch.assert_called_once()
            mock_write.assert_called_once()

    from unittest.mock import patch, mock_open, MagicMock

    # ... inside your TestUtils class ...

    @patch('builtins.open', new_callable=mock_open)  # Intercepts the open() call
    @patch('pathlib.Path.exists', return_value=False)
    @patch('requests.get')
    def test_fetch_expected_nested_em_code(self, mock_get, mock_exists, mock_file_open):
        """Verify <em><code>answer</code></em> and ensure no disk artifact is created."""
        mock_response = MagicMock()
        mock_response.content = b"<html><p><em><code>999</code></em></p></html>"
        mock_get.return_value = mock_response

        with patch('pathlib.Path.mkdir'):
            result = _fetch_expected(2026, 1, "session", 1)

            self.assertEqual("999", result)

            # Assert that the file was opened for writing
            mock_file_open.assert_called_once()

            # Optionally, assert that the correct data was written
            # .return_value is the handle; .write is the method called on that handle
            mock_file_open().write.assert_called_once_with("999")

    @patch('pathlib.Path.exists', return_value=False)
    @patch('requests.get')
    def test_fetch_expected_not_found(self, mock_get, mock_exists):
        """Verify the 'Could not find any test cases' fallback logic."""
        mock_response = MagicMock()
        # HTML with no <code> or <em> tags at all
        mock_response.content = b"<html><body><p>No answers here</p></body></html>"
        mock_get.return_value = mock_response

        with patch('pathlib.Path.mkdir'):
            result = _fetch_expected(2026, 1, "session", 1)
            self.assertIn("Could not find any test cases", result)

    @patch('requests.get')
    def test_fetch_expected_part2_locked(self, mock_get):
        """Verify Part 2 locked logic without disk interaction."""
        mock_response = MagicMock()
        mock_response.content = b"<html><body>Part One only</body></html>"
        mock_response.prettify.return_value = "<html><body>Part One only</body></html>"
        mock_get.return_value = mock_response

        # Mock Path to return False for exists()
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.mkdir'):
                result = _fetch_expected(2026, 1, "session", 2)
                self.assertEqual("UNLOCK PART 2 TO TEST", result)

    def test_time_execution_args_forwarding(self):
        """Verify that args and kwargs are passed transparently."""

        @time_execution
        def check_args(*args, **kwargs):
            return args, kwargs

        args, kwargs = check_args(1, 2, key='value')
        self.assertEqual((1, 2), args)
        self.assertEqual({'key': 'value'}, kwargs)


if __name__ == '__main__':
    unittest.main()
