import pytest
from utils import getScore


def test_getScore():
    score = getScore('廖妤宸')
    assert score == '85'


if __name__ == '__main__':
    pytest.main(["test_all.py"])
