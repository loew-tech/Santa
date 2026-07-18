"""High-level Advent of Code helpers for reading, caching, and solving puzzle input with optional testing and expected-answer validation."""


import inspect
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
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"⏱️ Execution time for {func.__name__}: {end - start:.4f} seconds")
        return result
    return wrapper


def get_naughty_or_nice(year: str | int, session_id: str):
    """
    Outer factory: Configures the decorator with persistent
    values like year and session_id.

    :param year: The puzzle year.
    :param session_id: The session cookie for authentication.

    :return: A wrapper for ease of testing and timing
    """

    def naughty_or_nice(day: str | int, part: int = 1):
        """
        Middle layer: Captures the arguments provided at the @ line
        (e.g., @decorator(day=1, part=1)).

        :param day: The day of the problem being tested / solved.
        :param part: The part of the problem being tested / solved
        """

        def decorator(func):
            """
            Inner layer: Receives the function (e.g., day_1) being decorated.
            """
            timed_func = time_execution(func)
            @wraps(func)
            def wrapper(*args, **kwargs):
                actual = timed_func(*args, **kwargs)

                # Validation logic
                testing = kwargs.get('testing', False)
                if testing:
                    expected = _fetch_expected(year, day, session_id, part)
                    if expected == str(actual):
                        print(f"{func.__name__}     NICE: {expected}.")
                    else:
                        print(f"{func.__name__}  NAUGHTY: {expected=}. {actual=}.")
                return actual

            return wrapper

        return decorator

    return naughty_or_nice


def get_solve(year: str | int, session_id: str) -> Callable[..., Any]:
    """
    Return a function that takes day, part1_func, [optional] part2_func, and [optional] testing bool and solves/tests
    the functions

    :param year: The puzzle year.
    :param session_id: The session cookie for authentication.

    :return: Callable that allows for running solution functions
    """
    def _solve(
            day: str | int, part1_func: Callable[..., Any], part2_func: Callable[..., Any] | None = None, testing=True
               ) -> tuple[Any, Any]:
        return solve(year,
                     day,
                     session_id,
                     part1_func,
                     part2_func,
                     testing=testing)
    return _solve


def solve(year: str | int,
          day: str|int,
          session_id: str,
          part1_func: Callable[..., Any],
          part2_func: Callable[..., Any] | None = None,
          testing=False
) -> tuple[Any, Any]:
    """
    Takes part1_func and [optional] part2_func and executes them. If keyword testing=True, then tests functions.
    Returns tuple of the results of part1_func and part2_func

    :param year: The puzzle year.
    :param day: The day of the problem being tested / solved.
    :param session_id: The session cookie for authentication.
    :param part1_func: Solution function for part 1.
    :param part2_func: Solution function for part 2.
    :param testing: bool indicating if this is a test run.

    :return: Tuple (result of part1_func, result of part2_func)
    """
    naughty_or_nice = get_naughty_or_nice(year, session_id)
    part1_wrapped = naughty_or_nice(day, part=1)(part1_func)
    res1 = part1_wrapped(testing=testing) if _accepts_testing_arg(part1_wrapped) else part1_wrapped()

    res2 = None
    if part2_func is not None:
        part2_wrapped = naughty_or_nice(day, part=2)(part2_func)
        res2 = part2_wrapped(testing=testing) if _accepts_testing_arg(part2_wrapped) else part2_wrapped()
    return res1, res2


def get_read_and_solve(year: str| int,
                       session_id: str,
                       inputs_path: Path | None = None,
                       tests_path: Path | None = None,
) -> Callable[..., Any]:
    """
    Return a function that takes day, part1_func, [optional] part2_func, delimiter (defaults to '\n'), an [optional]
    parser and [optional] testing bool and solves/tests the functions

    :param year: The puzzle year.
    :param session_id: The session cookie for authentication.
    :param inputs_path: Directory to store official input files. If None, defaults to ./inputs/
    :param tests_path: Directory to store test/scraped input files. If None, defaults to ./tests/

    :return: Callable that allows for running solution functions
    """
    def _read_and_solve(
            day, part1_func, part2_func, delim='\n', parse=None, testing=False
    ) -> tuple[Any, Any]:
        return read_and_solve(year,
                              day,
                              session_id,
                              part1_func,
                              part2_func,
                              inputs_path=inputs_path,
                              tests_path=tests_path,
                              delim=delim,
                              parse=parse,
                              testing=testing)
    return _read_and_solve


def _accepts_testing_arg(func) -> bool:
    """
    Returns whether testing or kwargs is present in the function argument

    :param func: The solution function
    :return: True is function accepts testing keyword argument or kwargs
    """

    sig = inspect.signature(func)
    # Check if 'testing' is a parameter (by name or as part of **kwargs)
    return 'testing' in sig.parameters or any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )


def read_and_solve(year: str | int,
          day: str|int,
          session_id: str,
          part1_func: Callable[..., Any],
          part2_func: Callable[..., Any] | None = None,
          inputs_path: Path | None = None,
          tests_path: Path | None = None,
          delim='\n',
          parse: Callable[..., Any] | None = None,
          testing=False
) -> tuple[Any, Any]:
    """
    Takes part1_func and [optional] part2_func and executes them. If keyword testing=True, then tests functions.
    Returns tuple of the results of part1_func and part2_func

    :param year: The puzzle year.
    :param day: The day of the problem being tested / solved.
    :param session_id: The session cookie for authentication.
    :param part1_func: Solution function for part 1.
    :param part2_func: Solution function for part 2.
    :param inputs_path: Directory to store official input files. If None, defaults to ./inputs/
    :param tests_path: Directory to store test/scraped input files. If None, defaults to ./tests/
    :param delim: String to split input text; defaults to newline.
    :param parse: A callable to transform input lines or the entire text.
    :param testing: bool indicating if this is a test run.

    :return: Tuple (result of part1_func, result of part2_func)
    """
    data = read_input(year, day, session_id, inputs_path, tests_path, delim, parse, testing=testing, part=1)
    if not data:
        raise ValueError(f"Failed to load or parse input for Day {day}, Year {year}. Data is empty.")

    def part_1():
        if _accepts_testing_arg(part1_func):
            return part1_func(data)
        return part1_func(data)

    data2 = data if not testing else \
        read_input(year, day, session_id, inputs_path, tests_path, delim, parse, testing=testing, part=2)
    if not data2:
        raise ValueError(f'Failed to load or parse input for Day {day} part 2. Data is empty.')

    def part_2():
        if _accepts_testing_arg(part2_func):
            return part2_func(data)
        return part2_func(data)

    return solve(year,
                 day,
                 session_id,
                 part_1,
                 part_2 if part2_func is not None else None,
                 testing=testing)
