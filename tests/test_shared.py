import pandas as pd
from pycoornet.shared import Shared

def test_shared():
        df_ct = pd.read_json('/Users/camilo/coornet/ct_shares_full.json')
        print(df_ct.count())
        shared = Shared()
        shares_graph, q = shared.coord_shares(df_ct, clean_urls=True)
        #nx.write_gexf(shares_graph, "../build/shares.gexf")
