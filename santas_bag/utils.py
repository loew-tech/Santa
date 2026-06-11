import os
from datetime import datetime
from http import HTTPStatus
from typing import Any, Callable, List

from bs4 import BeautifulSoup
import requests

ADVENT_URI = 'https://adventofcode.com/'
INPUTS_PATH = 'inputs/'
TESTS_PATH = 'tests/'


def read_input(
        day: int | str,
        year: int | str = 2025,
        delim: str | None = '\n',
        parse: Callable[[List[str] | str], Any] | None = None,
        testing: bool = False
) -> List[Any] | str:
    if testing:
        return _process_input(_get_test_input(day, year), delim, parse)

    if os.path.exists(f'{INPUTS_PATH}{day}.txt'):
        with open(f'{INPUTS_PATH}{day}.txt') as in_:
            return _process_input(in_.read(), delim, parse)

    with open('.env') as env_:
        session_id = env_.read().strip().split('\n')[0]
    response = requests.get(f'{ADVENT_URI}{year}/day/{day}/input',
                            cookies={'session': session_id})

    if not response.status_code == HTTPStatus.OK:
        raise Exception(f'Failed to acquire input from {ADVENT_URI}')
    if not os.path.exists(INPUTS_PATH):
        os.mkdir(INPUTS_PATH)
    with open(f'{INPUTS_PATH}{day}.txt', 'w') as out:
        out.write(response.text)
    return _process_input(response.text, delim, parse)


def _get_test_input(
        day: int | str,
        year: int | str = datetime.now().year,
) -> str:
    if os.path.exists(f'{TESTS_PATH}{day}.txt'):
        with open(f'{TESTS_PATH}{day}.txt') as in_:
            return in_.read()

    problem = requests.get(f'{ADVENT_URI}{year}/day/{day}')
    soup = BeautifulSoup(problem.content, 'html.parser')
    input_ = soup.find('pre').code
    txt = input_.get_text()
    if not os.path.exists(TESTS_PATH):
        os.mkdir(TESTS_PATH)
    with open(f'{TESTS_PATH}{day}.txt', 'w') as out:
        out.write(txt)
    return txt

def _process_input(
        text: str, delim: str | None,
        parse: Callable[[List[str] | str], Any] | None
) -> Any:
    data = text.strip().split(delim) if delim else text
    return data if parse is None else [
        parse(e) for e in (data if type(data) == list else [data])
    ]
