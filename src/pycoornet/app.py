# from .crowdtangle import CrowdTangle
# import logging
# import networkx as nx
# import pandas as pd
# from .shared import Shared


# class App:

#     @staticmethod
#     def run():
#         print("Hello World")

#     @staticmethod
#     def get_ct_shares():
#         # urls_df = pd.read_csv('samples/sample.csv')
#         # ct = CrowdTangle('hWGv30FDktGlUDKzjEV5ncoa3VMRptkfq2ChWmG7')
#         # ct.get_shares(urls_df, date_column='publish_date')
#         pass

#     @staticmethod
#     def get_shares():
#         df_ct = pd.read_json('/Users/camilo/coornet/ct_shares_full.json')
#         print(df_ct.count())
#         shared = Shared()
#         shares_graph, q = shared.coord_shares(df_ct, clean_urls=True)
#         nx.write_gexf(shares_graph, "../build/shares.gexf")



