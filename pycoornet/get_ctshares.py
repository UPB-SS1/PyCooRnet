import logging
import numpy as np
import pandas as pd
import PyCrowdTangle as pct
from tqdm import tqdm
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import time
from pathlib import Path


def get_shares(self, urls, url_column='url', date_column='date', platforms=('facebook', 'instagram'), nmax=500, sleep_time=20, clean_urls=False, save_ctapi_output=False):
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
        urls = urls.drop_duplicates(subset=url_column, keep=False)
        # set column names
        urls = urls.rename(columns={url_column: 'url', date_column: 'date'})
        print(urls.columns)
        # clean the URLs
        if clean_urls:
            # TO DO : Limpieza de urls por medio de regex
            pass
        # create empty dataframe
        cf_shares_df = pd.DataFrame()
        # Progress bar tqdm
        for i in tqdm(range(len(urls))):
            # set date limits, endDate: one week after date_published
            startDate = urls.iloc[i, :].loc['date']
            endDate = str(parse(startDate) + relativedelta(weeks=+1))
            url = urls.iloc[i, :].loc['url']
            try:
                # pycrowdtangle get links
                data = pct.ct_get_links(link=url, platforms=platforms,
                                        start_date=startDate,
                                        end_date=endDate,
                                        include_history='true',
                                        count=nmax,
                                        api_token=token
                                        )
                # concat data results in dataframe
                cf_shares_df = cf_shares_df.append(data)
            except:
                print(f"Unexpected http response code on url {url}")
            # wait time
            time.sleep(sleep_time)
    except Exception as e:
        raise e
    if cf_shares_df.dropna().empty:
        raise SystemExit("\n No ct_shares were found!")
    if save_ctapi_output:
        Path("./rawdata").mkdir(parents=True, exist_ok=True)
        cf_shares_df.to_csv('./rawdata/cf_shares_df', index=False)
    # remove possible inconsistent rows with entity URL equal "https://facebook.com/null"
    ct_shares_df = ct_shares_df[ct_shares_df['url']
                                != "https://facebook.com/null"]
    # get rid of duplicates
    ct_shares_df.drop_duplicates(inplace=True)
    # remove shares performed more than one week from first share
    # clean the expanded URLs
    # write log
    return ct_shares_df
