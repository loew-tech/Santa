import os
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable, List

from bs4 import BeautifulSoup
import requests

ADVENT_URI = 'https://adventofcode.com/'
# @TODO: have these be overridable from config
ENV_PATH = '.env'
INPUTS_PATH = Path('inputs/')
TESTS_PATH = Path('tests/')


def read_input(
        day: int | str,
        # @TODO: set this default better; datetime.now.year or read from config.
        year: int | str,
        delim: str | None = '\n',
        parse: Callable[[List[str] | str], Any] | None = None,
        testing: bool = False
) -> List[Any] | str:
    target_dir = TESTS_PATH if testing else INPUTS_PATH
    target_file = target_dir / f'{day}.txt'

    if target_file.exists():
        return _process_input(target_file.read_text(), delim, parse)

    target_file.parent.mkdir(parents=True, exist_ok=True)
    if testing:
        text = _fetch_test_input(day, year)
        print(f'⚠️ Scraped test input for Day {day}. Verify it in {target_file}')
    else:
        text = _fetch_official_input(day, year)

    target_file.write_text(text)
    return _process_input(text, delim, parse)

def _fetch_official_input(day: int | str, year: int | str) -> str:
    # @TODO: look into better way of doing this
    session_id = None
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if line.startswith('session='):
                    session_id = line.strip().split('=', 1)[1]
                    break

    if not session_id:
        raise ValueError("Could not find 'session=' variable in your .env file.")

    response = requests.get(
        f'{ADVENT_URI}{year}/day/{day}/input',
        cookies={'session': session_id},
        headers={'User-Agent': 'github.com/loew-tech/santas_bag by loew.technology@gmail.com'}
    )

    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Failed to acquire input from {ADVENT_URI} (Status: {response.status_code})')

    return response.text

def _fetch_test_input(day: int | str, year: int | str) -> str:
    response = requests.get(f'{ADVENT_URI}{year}/day/{day}')
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Failed to fetch puzzle page for scraping.')

    soup = BeautifulSoup(response.content, 'html.parser')
    code_block = soup.find('pre')
    if not code_block:
        raise Exception(f'Could not automatically find a test case (<pre> block) on Day {day} page.')

    return code_block.get_text()


def _process_input(text: str, delim: str | None, parse: Callable[[List[str] | str], Any] | None) -> Any:
    if delim == '\n':
        raw_data = text.splitlines()
    elif delim:
        raw_data = text.split(delim)
    else:
        return parse(text) if parse else text

    return [parse(item) for item in raw_data] if parse else raw_data
