import pandas as pd
from pycoornet.crowdtangle import CrowdTangle
from pycoornet.shared import Shared

def test_crowdtangle(crowd_token, urls_file):
    crowdTangle = CrowdTangle(crowd_token)
    test_file = pd.read_csv(urls_file)
    shares_df = crowdTangle.get_shares(urls = test_file, url_column='clean_url', date_column='date',
                                    clean_urls=True, platforms='facebook', sleep_time=1)
    #shares_df.to_csv(f'output/{crowd_output_file_name}', index=False)
    assert True

def test_shared(crowd_result_file):
        df_ct = pd.read_json(crowd_result_file)
        print(df_ct.count())
        shared = Shared()
        shares_graph, q = shared.coord_shares(df_ct, clean_urls=True)
        #nx.write_gexf(shares_graph, "../build/shares.gexf")
        assert True
