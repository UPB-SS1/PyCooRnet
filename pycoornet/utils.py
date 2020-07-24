import re
import numpy as np
from urllib.parse import urljoin, urlparse

class Utils:
    @staticmethod
    def clean_urls(dataframe, url_column):
        """Clean the URLs

        Args:
            dataframe ([pandas.DataFrame]): the pandas dataframe of link posts
            url_column (string): the name of the dataframe column with the urls

        Returns:
            [pandas.DataFrame]: the dateframe with the cleaned urls
        """
        #Remove the URL query parameters and set NaN to protocols that aren't http or https
        dataframe[url_column] = dataframe[url_column].apply(lambda x: urljoin(x, urlparse(x).path) if (urlparse(x).scheme == 'http' or urlparse(x).scheme == 'https') and urlparse(x).netloc != '127.0.0.1' and urlparse(x).netloc != 'localhost' else np.NaN)
        #Drop NaN values
        dataframe=dataframe.dropna()
        dataframe=dataframe.reset_index(drop=True)
        return dataframe









