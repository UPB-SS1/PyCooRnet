from .pycoornet import PyCooRnet
from .app import App
import pandas as pd

if __name__ == '__main__':
    App.run()
    # pc = PyCooRnet("test")
    # datos = {
    #     'url2': ['http://test.com','http://test2.com'],
    #     'date2': [22000,25000]
    #     }

    # df = pd.DataFrame(datos)
    # pc.get_crowtangle_shares(df, url_column='url2', date_column='date2')
