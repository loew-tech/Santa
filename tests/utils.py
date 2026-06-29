import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import time

from santas_bag.utils import *


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
            2026, 1, 'my_session', None, None, '\n', None, True
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
