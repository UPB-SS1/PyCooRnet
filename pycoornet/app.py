from .crowdtangle import CrowdTangle
import pandas as pd

class App:

    @staticmethod
    def run():
        print("Hello World")

    # @staticmethod
    # def get_ct_shares():
    #     urls_df = pd.read_csv('test_data.csv')
    #     ct = CrowdTangle('hWGv30FDktGlUDKzjEV5ncoa3VMRptkfq2ChWmG7')
    #     ct.get_shares(urls_df, date_column='publish_date')
