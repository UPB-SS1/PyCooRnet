from .crowdtangle import CrowdTangle
import pandas as pd
from .shared import Shared


class App:

    @staticmethod
    def get_shares():
        df = pd.read_json('samples/ct_shares_telesur.json')
        #df = pd.read_csv('samples/telesurenglish2017-1000.csv')
        shared = Shared()
        shared.coord_shares(df, clean_urls=True, )

    @staticmethod
    def run():
        #print("Hello World")
        App.get_shares()

    # @staticmethod
    # def get_ct_shares():
    #     urls_df = pd.read_csv('test_data.csv')
    #     ct = CrowdTangle('hWGv30FDktGlUDKzjEV5ncoa3VMRptkfq2ChWmG7')
    #     ct.get_shares(urls_df, date_column='publish_date')


