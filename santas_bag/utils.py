import time
from functools import wraps
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable

from bs4 import BeautifulSoup
import requests

ADVENT_URI = 'https://adventofcode.com/'
INPUTS_PATH = Path('inputs/')
TESTS_PATH = Path('tests/')


def get_read_input(
        year: int | str,
        session_id: str,
        inputs_path: Path | None = None,
        tests_path: Path | None = None,
) -> Callable[..., Any]:
    """
    Returns a closure of read_input pre-configured with
    the year, authentication credentials, and inputs/tests paths.

    :param year: The puzzle year (e.g., 2024).
    :param session_id: The session cookie for authentication.
    :param inputs_path: Directory to store official input files. If None, defaults to ./inputs/
    :param tests_path: Directory to store test/scraped input files. If None, defaults to ./tests/

    :return: A callable that accepts day, delim, parse, and testing arguments.
    """
    def read(day: int | str,
             delim: str | None = '\n',
             parse: Callable[[Any], Any] | None = None,
             testing=False,
             part=1) -> Any:
        return read_input(year, day, session_id, inputs_path, tests_path, delim, parse, testing, part)
    return read


def read_input(
        year: int | str,
        day: int | str,
        session_id: str,
        inputs_path: Path | None = None,
        tests_path: Path | None = None,
        delim: str | None = '\n',
        parse: Callable[[Any], Any] | None = None,
        testing: bool = False,
        part = 1
) ->  Any:
    """
    Retrieves and parses Advent of Code input data.

    :param year: The puzzle year (e.g., 2024).
    :param day: The puzzle day.
    :param session_id: The session cookie for authentication.
    :param inputs_path: Directory to store official input files.
    :param tests_path: Directory to store test/scraped input files.
    :param delim: String to split input text; defaults to newline.
    :param parse: A callable to transform input lines or the entire text.
    :param testing: Whether to fetch from the test path and scrape test cases.
    :param part: The part of the problem being tested / solved.

    :return: A list of parsed items or the raw input string.
    """
    inputs_path = inputs_path or INPUTS_PATH
    tests_path = tests_path or TESTS_PATH

    target_dir = tests_path if testing else inputs_path
    target_file = target_dir / f'{day}_part_{part}.txt' if testing else target_dir / f'{day}.txt'
    if target_file.exists():
        return _process_input(target_file.read_text(), delim, parse)

    target_file.parent.mkdir(parents=True, exist_ok=True)
    if testing:
        text = _fetch_test_input(year, day, session_id, part)
        print(f'⚠️ Scraped test input for Day {day}. Verify it in {target_file}')
    else:
        text = _fetch_official_input(year, day, session_id)

    target_file.write_text(text)
    return _process_input(text, delim, parse)


def _fetch_official_input(year, day: int | str, session_id: str) -> str:
    """
    Fetches the official puzzle input from the Advent of Code website.

    :param year: The puzzle year.
    :param day: The puzzle day.
    :param session_id: your session cookie for authentication.

    :raises Exception: If the HTTP request fails.

    :return: The raw string content of the puzzle input.
    """
    response = requests.get(
        f'{ADVENT_URI}{year}/day/{day}/input',
        cookies={'session': session_id},
        headers={'User-Agent': 'github.com/loew-tech/santas_bag by loew.technology@gmail.com'}
    )

    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Failed to acquire input from {ADVENT_URI} (Status: {response.status_code})')

    return response.text


def _fetch_test_input(year,  day: int | str, session_id: str, part: int | str) -> str:
    """
    Scrapes the example input from the puzzle page <pre> blocks.

    :param day: The puzzle day.
    :param year: The puzzle year.
    :raises Exception: If the page fetch fails or no <pre> block is found.

    :return: The extracted text content from the first code block.
    """
    response = requests.get(f'{ADVENT_URI}{year}/day/{day}',
    cookies = {'session': session_id if not int(part) == 1 else ''},
    headers = {'User-Agent': 'github.com/loew-tech/santas_bag by loew.technology@gmail.com'}
    )
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Failed to fetch puzzle page for scraping.')

    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find_all('article')[int(part) - 1]
    code_block = article.find('pre')
    if not code_block and not (code_block:=soup.find('pre')):
        raise Exception(f'Could not automatically find a test case (<pre> block) on Day {day} page.')
    return code_block.get_text()


def _process_input(text, delim: str | None,
                   parse: Callable[[Any], Any] | None) -> Any:
    """
    Processes the raw input text based on the provided delimiter and parser.

    :param text: The raw input string.
    :param delim: The delimiter to split the text, or None for raw processing.
    :param parse: An optional transformation function applied to data.

    :return: A list of processed data, or a single parsed value if delim is None.
    """
    text = text[:-1] if text[-1] == '\n' else text
    if delim == '\n':
        raw_data = text.splitlines()
    elif delim:
        raw_data = text.split(delim)
    else:
        return parse(text) if parse else text

    return [parse(item) for item in raw_data] if parse else raw_data


def _fetch_expected(year, day: int | str, session_id: str, part: int | str) -> str:
    """
    Scrapes the example output from the puzzle page <code> blocks. Result is cached in TESTS_PATH (default: /test) and
    written to <day>_part_<part>_expected.txt

    :param year: The puzzle year.
    :param day: The puzzle day.
    :param session_id: your session cookie for authentication. Necessary for scraping answer for part 2.
    :param part: The part of the problem being tested / solved.

    :return: The expected answer for the puzzle's sample input
    """
    TESTS_PATH.mkdir(exist_ok=True)
    file_path = TESTS_PATH / f'{day}_part_{part}_expected.txt'

    if file_path.exists():
        return file_path.read_text().strip()

    response = requests.get(f'{ADVENT_URI}{year}/day/{day}',
    cookies = {'session': session_id if not int(part) == 1 else ''},
    headers = {'User-Agent': 'github.com/loew-tech/santas_bag by loew.technology@gmail.com'}
    )
    soup = BeautifulSoup(response.content, 'html.parser')
    if not part == 1:
        if 'Part Two' not in soup.prettify():
            return 'UNLOCK PART 2 TO TEST'

    expected = ''
    for p in soup.find_all('p'):
        for c in p.find_all('code'):
            if em := c.find('em'):
                expected = em.get_text().strip()

    if not expected:
        for p in soup.find_all('p'):
            for em in p.find_all('em'):
                if code := em.find('code'):
                    expected = code.get_text().strip()

    if expected:
        with open(file_path, 'w') as out:
            out.write(expected)
        return expected

    return f'Could not find any test cases year {year} for Day {day}. Verify by examining {ADVENT_URI}{year}/day/{day}'


def time_execution(func):
    """
    Decorator to log the execution time of a function.

    :param func: The function to be wrapped and timed.

    :return: A wrapper function that prints the execution duration.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'\t\t\ttimed_execution {args=} {kwargs=}')
        # @TODO: is this the right way to handle this?
        kws = {**kwargs}
        start = time.perf_counter()
        result = func(*args, **kws)
        end = time.perf_counter()
        print(f"⏱️ Execution time for {func.__name__}: {end - start:.4f} seconds")
        return result
    return wrapper


def get_naughty_or_nice(year: int, session_id: str):
    """
    Outer factory: Configures the decorator with persistent
    values like year and session_id.
    """

    def naughty_or_nice(day: int, part: int = 1):
        """
        Middle layer: Captures the arguments provided at the @ line
        (e.g., @decorator(day=1, part=1)).
        """

        def decorator(func):
            """
            Inner layer: Receives the function (e.g., day_1) being decorated.
            """
            timed_func = time_execution(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                print(f'\t\twrapper {args=} {kwargs=}')
                actual = timed_func(*args, **kwargs)

                # We inject the captured arguments into kwargs so the function
                # or the validation logic can use them.
                kwargs.setdefault('year', year)
                kwargs.setdefault('session_id', session_id)
                kwargs.setdefault('day', day)
                kwargs.setdefault('part', part)

                # Validation logic
                if kwargs.get("testing"):
                    # Use the values we injected above
                    y = kwargs['year']
                    d = kwargs['day']
                    p = kwargs['part']
                    s = kwargs['session_id']
                    expected = _fetch_expected(y, d, s, p)
                    if expected == str(actual):
                        print(f"{func.__name__}     NICE: {expected}.")
                    else:
                        print(f"{func.__name__}  NAUGHTY: {expected=}. {actual=}.")
                return actual

            return wrapper

        return decorator

    return naughty_or_nice


# def solve(year: str| int,
#           day: int | str,
#           session_id: str,
#           part1_func: Callable,
#           part2_func: Callable | None=None,
#           testing=False) -> Any:
#     naughty_or_nice(part1_func, year=year, day=day, session_id=session_id, part=1, testing=testing)()
#     if part2_func is not None:
#         naughty_or_nice(part2_func, year=year, day=day, session_id=session_id, part=2, testing=testing)()
