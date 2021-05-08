import re
import numpy as np
from urllib.parse import urljoin, urlparse

class Utils:
    @staticmethod
    def clean_urls(dataframe, url_column):
        """Clean the URLs

        Args:
            dataframe (pandas.DataFrame): the pandas dataframe of link posts
            url_column (str): the name of the dataframe column with the urls

        Returns:
            pandas.DataFrame: the dateframe with the cleaned urls
        """
        pattern = [
            '\\?utm_.*',
            'feed_id.*',
            '&_unique_id.*',
            '\\?#.*',
            '\\?ref.*',
            '\\?fbclid.*',
            '\\?rss.*',
            '\\?ico.*',
            '\\?recruiter.*',
            '\\?sr_share_.*',
            '\\?fb_rel.*',
            '\\?social.*',
            '\\?intcmp_.*',
            '\\?xrs.*',
            '\\?CMP.*',
            '\\?tid.*',
            '\\?ncid.*',
            '&utm_.*',
            '\\?rbs&utm_hp_ref.*',
            '/#\\..*',
            '\\?mobile.*',
            '&fbclid.*',
            '/$',
            '#.*',
            '\\?mbid.*',
            '\\?platform',
            '\\?__twitter_impression',
            '\\/amp$',
            '\\?amp$',
            '\\/amp=.*',
            '\\?verso.*',
            '\\?mc_cid.*',
            '\\?mc_eid.*',
            '\\?source=TDB.*',
            '\\?spMailingID.*',
            '\\?mcd.*',
            '\\?cd-origin=.*'
            ]

        dataframe[url_column] = dataframe[url_column].str.replace('|'.join(pattern), '', regex=True)
        dataframe[url_column] = dataframe[url_column].str.replace('|'.join(pattern), '', regex=True)
        dataframe[url_column] = dataframe[url_column].str.replace('|'.join(pattern), '', regex=True)

        dataframe[url_column] = dataframe[url_column].str.replace('.*(http)', '\\1', regex=True)
        dataframe[url_column] = dataframe[url_column].str.replace('\\/$', '', regex=True)
        dataframe[url_column] = dataframe[url_column].str.replace('\\&$'.join(pattern), '', regex=True)

         #Remove the URL query parameters and set NaN to protocols that aren't http or https
        dataframe = dataframe.loc[dataframe[url_column].str.contains('^http://127.0.0.1|^https://127.0.0.1|http://localhost|https://localhost') == False]
        dataframe = dataframe.loc[dataframe[url_column].str.contains('http://|https://')]

        dataframe=dataframe.reset_index(drop=True)
        return dataframe









