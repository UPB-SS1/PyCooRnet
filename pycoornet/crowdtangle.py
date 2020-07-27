from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import PyCrowdTangle as pct
import time
from tqdm import tqdm
from .utils import Utils


class CrowdTangle:
    """Descripción de la clase.

        :param api_key: CrowdTangle API key.
        :type api_key: string
     """

    def __init__(self, api_key):
        """Constructor method
        """
        if not api_key:
            raise Exception('Crowdtangle Api Token is missing')
        self.api_key = api_key

    def get_shares(self, urls, url_column='url', date_column='date', platforms=('facebook', 'instagram'), nmax=100, sleep_time=20, clean_urls=False, save_ctapi_output=False):
        """ Get the URLs shares from CrowdTangle from a list of URLs with publish datetime

        Args:
            urls (dataframe): a dataframe with at least a column "url" containing the URLs, and a column "date" with their published date
            url_column (str, optional): name of the column (placed inside quote marks) where the URLs are stored. Defaults to 'url'.
            date_column (str, optional): name of the column (placed inside quote marks) where the date of the URLs are stored. Defaults to 'date'.
            platforms (tuple, optional): a tuple of platforms to search. You can specify only facebook to search on Facebook, or only instagram to
                                         search on Instagram. Defaults to ('facebook', 'instagram').
            nmax (int, optional): max number of results for query. Defaults to 100.
            sleep_time (int, optional): pause between queries to respect API rate limits. Default to 20 secs, it can be lowered or increased
                                        depending on the assigned API rate limit. Defaults to 20.
            clean_urls (bool, optional): clean the URLs from tracking parameters. Defaults to False.
            save_ctapi_output (bool, optional): saves the original CT API output in ./rawdata/. Defaults to False.

        Raises:
            Exception: [description]
            Exception: [description]
            e: [description]
            SystemExit: [description]

        Returns:
            [pandas.Dataframe]: [A pandas dataframe of posts that shared the URLs and a number of variables returned by the https://github.com/CrowdTangle/API/wiki/Links
                    CrowdTangle API links endpoint and the original data set of news.
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
            urls = urls.rename(
                columns={url_column: 'url', date_column: 'date'})
            print(urls.columns)
            # clean the URLs
            if clean_urls:
                urls = Utils.clean_urls(urls, 'url')

            # create empty dataframe
            ct_shares_df = pd.DataFrame()

            # Progress bar tqdm
            for i in tqdm(range(len(urls))):
                # set date limits, endDate: one week after date_published
                startDate = parse(urls.iloc[i, :].loc['date'])
                startDate = startDate.replace(microsecond=0)
                endDate = str(startDate + relativedelta(weeks=+1))
                startDate = str(startDate)
                url = urls.iloc[i, :].loc['url']
                try:
                    # pycrowdtangle get links
                    data = pct.ct_get_links(link=url, platforms=platforms,
                                            start_date=startDate,
                                            end_date=endDate,
                                            include_history='true',
                                            sortBy='date',
                                            count=nmax,
                                            api_token=self.api_key
                                            )
                    # if status is an error
                    if data['status'] != 200:
                        print(f"Unexpected http response code {data['status']} on {url}")
                        #next iteration
                        continue

                    # convert json response to dataframe
                    df = pd.DataFrame(data['result']['posts'])

                    #get pagination pending

                    # Extract expanded info from column and convert to columns
                    df['expanded'] = df['expandedLinks'].map(lambda x: x[0]).apply(pd.Series)['expanded']

                    # Remove column
                    df.drop(['expandedLinks'], axis=1, inplace = True)

                    # Extract account info from column and convert to columns

                    # add prefix name to each key of the dictionary per row in 'account' column
                    df['account'] = df['account'].apply(
                        lambda x: {f'account_{k}': v for k, v in x.items()})
                    # convert dictionary info in each row to columns
                    partes = df['account'].apply(pd.Series)

                    df_full = pd.concat([df, partes], axis=1).drop(
                        ['account'], axis=1)
                    # concat data results in dataframe
                    ct_shares_df = ct_shares_df.append(df_full, ignore_index=True)
                except:
                    logging.exception(f"Unexpected http response code on url {url}")
                    print(f"Unexpected http response code on url {url}")
                # wait time
                time.sleep(sleep_time)
        except Exception as e:
            raise e
        if ct_shares_df.dropna().empty:
            logging.error("No ct_shares were found!")
            raise SystemExit("\n No ct_shares were found!")
        if save_ctapi_output:
            Path("./rawdata").mkdir(parents=True, exist_ok=True)
            ct_shares_df.to_csv('./rawdata/ct_shares_df', index=False)
        # remove possible inconsistent rows with entity URL equal "https://facebook.com/null"
        ct_shares_df = ct_shares_df[ct_shares_df['account_url'] != "https://facebook.com/null"]
        # get rid of duplicates
        ct_shares_df.drop_duplicates(inplace=True)
        # remove shares performed more than one week from first share
        # clean the expanded URLs
        # write log
        return ct_shares_df
