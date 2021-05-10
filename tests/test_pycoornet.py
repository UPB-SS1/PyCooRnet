import pandas as pd
from pycoornet.crowdtangle import CrowdTangle
from pycoornet.shared import Shared
import pytest


@pytest.fixture
def sample_ct_df():
    return pd.read_pickle('samples/ct_output.pickle')


@pytest.fixture
def sample_source_df():
    return pd.read_csv('samples/sample_source_links.csv')


def test_crowdtangle(crowd_token, sample_source_df):
    crowd_tangle = CrowdTangle(crowd_token)
    shares_df = crowd_tangle.get_shares(urls=sample_source_df, url_column='clean_url', date_column='date',
                                        clean_urls=True, platforms='facebook', sleep_time=1,
                                        id_column = 'url_rid')
    if shares_df.shape[0] > 0:

        assert True
    else:
        assert False


def test_shared(sample_ct_df):
    shared = Shared(sample_ct_df)
    crowtangle_shares_df, highly_connected_graph, q = shared.coord_shares(clean_urls=True)
    if crowtangle_shares_df.shape[0] > 0 and highly_connected_graph != None:
        assert True
    else:
        assert False

def test_estimate_coord_interval(sample_ct_df):
    shared = Shared(sample_ct_df)
    summary, coord_interval = shared.estimate_coord_interval(True)
    if coord_interval > 0:
        assert True
    else:
        assert False

