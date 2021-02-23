import pytest

def pytest_addoption(parser):
    parser.addoption('--crowdtoken', action='store')

@pytest.fixture(scope='session')
def crowd_token(request):
    crowd_token_value = request.config.option.crowdtoken
    if crowd_token_value is None:
        pytest.skip()
    return crowd_token_value
