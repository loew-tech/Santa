import os
import time
from functools import wraps
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable, List, Tuple

from bs4 import BeautifulSoup
import requests

ADVENT_URI = 'https://adventofcode.com/'
INPUTS_PATH = Path('inputs/')
TESTS_PATH = Path('tests/')


def read_input(
        year: int | str,
        day: int | str,
        session_id: str,
        inputs_path: Path | None = None,
        tests_path: Path | None = None,
        delim: str | None = '\n',
        parse: Callable[[List[str] | str], Any] | None = None,
        testing: bool = False
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

    :return: A list of parsed items or the raw input string.
    """
    inputs_path = inputs_path or INPUTS_PATH
    tests_path = tests_path or TESTS_PATH

    target_dir = tests_path if testing else inputs_path
    target_file = target_dir / f'{day}.txt'

    if target_file.exists():
        return _process_input(target_file.read_text(), delim, parse)

    target_file.parent.mkdir(parents=True, exist_ok=True)
    if testing:
        text = _fetch_test_input(year, day)
        print(f'⚠️ Scraped test input for Day {day}. Verify it in {target_file}')
    else:
        text = _fetch_official_input(year, day, session_id)

    target_file.write_text(text)
    return _process_input(text, delim, parse)

def _fetch_official_input(year: int | str, day: int | str, session_id: str) -> str:
    """
    Fetches the official puzzle input from the Advent of Code website.

    :param day: The puzzle day.
    :param year: The puzzle year.
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

    return response.text.strip()

def _fetch_test_input(year: int | str, day: int | str) -> str:
    """
    Scrapes the example input from the puzzle page <pre> blocks.

    :param day: The puzzle day.
    :param year: The puzzle year.
    :raises Exception: If the page fetch fails or no <pre> block is found.

    :return: The extracted text content from the first code block.
    """
    response = requests.get(f'{ADVENT_URI}{year}/day/{day}')
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Failed to fetch puzzle page for scraping.')

    soup = BeautifulSoup(response.content, 'html.parser')
    code_block = soup.find('pre')
    if not code_block:
        raise Exception(f'Could not automatically find a test case (<pre> block) on Day {day} page.')

    return code_block.get_text()


def _process_input(text: str, delim: str | None,
                   parse: Callable[[List[str] | str], Any] | None) -> Any:
    """
    Processes the raw input text based on the provided delimiter and parser.

    :param text: The raw input string.
    :param delim: The delimiter to split the text, or None for raw processing.
    :param parse: An optional transformation function applied to data.

    :return: A list of processed data, or a single parsed value if delim is None.
    """
    if delim == '\n':
        raw_data = text.splitlines()
    elif delim:
        raw_data = text.split(delim)
    else:
        return parse(text) if parse else text

    return [parse(item) for item in raw_data] if parse else raw_data


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
