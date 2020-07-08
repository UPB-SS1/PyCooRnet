import logging
import numpy as np
import pandas as pd
import PyCrowdTangle as pct
from tqdm import tqdm
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class CrowdTangle:
    """Descripción de la clase.

        :param api_key: CrowdTangle API key.
        :type api_key: string
     """

    def __init__(self, api_key):
        """Constructor method
        """
        self.api_key = api_key


    def get_shares(self, urls, url_column='url', date_column='date', platforms=('facebook','instagram'), nmax=500, sleep_time=20, clean_urls=False, save_ctapi_output=False):
        """Get the URLs shares from CrowdTangle.

        :param urls: A pandas dataframe with at least a column "url" containing the URLs, and a column "date" with their published date.
        :type urls: pandas.DataFrame
        :param url_column: Name of the column (placed inside quote marks) where the URLs are stored, defaults to 'url'
        :type url_column: str, optional
        :param date_column: name of the column (placed inside quote marks) where the date of the URLs are stored, defaults to 'date'
        :type date_column: str, optional
        :param platforms: a tuple of platforms to search. You can specify only facebook to search on Facebook, or only instagram to search on Instagram, defaults to ('facebook','instagram')
        :type platforms: tuple, optional
        :param nmax: max number of results for query, defaults to 500
        :type nmax: int, optional
        :param sleep_time: pause between queries to respect API rate limits. Default to 20 secs, it can be lowered or increased depending on the assigned API rate limit, defaults to 20
        :type sleep_time: int, optional
        :param clean_urls: clean the URLs from tracking parameters, defaults to False
        :type clean_urls: bool, optional
        :param save_ctapi_output: saves the original CT API output in ./rawdata/ct_shares.df.0.rds, defaults to False
        :type save_ctapi_output: bool, optional
        :return: A pandas dataframe of posts that shared the URLs and a number of variables returned by the https://github.com/CrowdTangle/API/wiki/Links CrowdTangle API links endpoint and the original data set of news.
        :rtype: pandas.DataFrame
        """

        try:
            if url_column not in urls.columns:
                message = f"Can't find {url_column} in urls dataframe"
                raise Exception(message)

            if date_column not in urls.columns:
                message = f"Can't find {date_column} in urls dataframe"
                raise Exception(message)

            # remove duplicated rows
            urls = urls.drop_duplicates(subset = url_column, keep = False)

            # set column names
            urls = urls.rename(columns={url_column: 'url', date_column: 'date'})
            print(urls.columns)

            # clean the URLs
            if clean_urls :
                # TO DO : Limpieza de urls por medio de regex
                pass

            cf_shares_df = None

            # Progress bar tqdm

            for i in tqdm(range(len(urls))):
                # set date limits, endDate: one week after date_published
                StartDate = urls.iloc[i,:].loc[date_column]
                endDate = str(parse(StartDate) + relativedelta(weeks=+1))

                ur = urls.iloc[i,:].loc[url_column]

                data = pct.ct_get_links(link = ur, platforms = platforms,
                                        start_date= startDate,
                                        end_date= endDate,
                                        api_token = token
                                        )






        except Exception as e:
            raise e
