import pytest

def pytest_addoption(parser):
    parser.addoption('--crowdtoken', action='store')
    parser.addoption('--urlsfile', action='store')
    #parser.addoption('--crowdoutputfilename', action='store')
    parser.addoption('--crowdresultfile', action='store')

@pytest.fixture(scope='session')
def crowd_token(request):
    crowd_token_value = request.config.option.crowdtoken
    if crowd_token_value is None:
        pytest.skip()
    return crowd_token_value

@pytest.fixture(scope='session')
def urls_file(request):
    urls_file_value = request.config.option.urlsfile
    if urls_file_value is None:
        pytest.skip()
    return urls_file_value

# @pytest.fixture(scope='session')
# def crowd_output_file_name(request):
#     crowd_output_value = request.config.option.crowdoutputfilename
#     if crowd_output_value is None:
#         pytest.skip()
#     return crowd_output_value


@pytest.fixture(scope='session')
def crowd_result_file(request):
    crowd_result_file_value = request.config.option.crowdresultfile
    if crowd_result_file_value is None:
        pytest.skip()
    return crowd_result_file_value
