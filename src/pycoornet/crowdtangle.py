import logging
import numpy as np
import pandas as pd
from pathlib import Path
import PyCrowdTangle as pct
import time
from tqdm import tqdm
from .utils import Utils

logger = logging.getLogger(__name__)


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

    def get_shares(self, urls, url_column='url', date_column='date', platforms=('facebook', 'instagram'), nmax=500, sleep_time=20, clean_urls=False, save_ctapi_output=False):
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
            save_ctapi_output (bool, optional): saves the original CT API output in rawdata/ folder. Defaults to False.

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



            logger.info("########## PyCoornet ##########")
            logger.info(f"get_shares script execute \n\n")


            # remove duplicated rows
            urls = urls.drop_duplicates(subset=url_column, keep=False)
            # set column names
            urls = urls.rename(columns={url_column: 'url', date_column: 'date'})

            #convert the type of date column to datetime
            urls['date'] = pd.to_datetime(urls['date'])
            # clean the URLs
            if clean_urls:
                urls = Utils.clean_urls(urls, 'url')
                logger.info("Original URLs have been cleaned")

            # create empty dataframe
            ct_shares_df = pd.DataFrame()

            # Progress bar tqdm
            for i in tqdm(range(len(urls))):
                # set date limits, endDate: one week after date_published
                startDate = urls.iloc[i, :].loc['date']
                #startDate = startDate.replace(microsecond=0)
                endDate = startDate + pd.Timedelta('7 day')
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
                        logger.exception(f"Unexpected http response code on url {url}")
                        print(f"Unexpected http response code on url {url}")
                        #next iteration
                        continue

                    #if data response is empty
                    if not data['result']['posts']:
                        print(f"Empty response on url: {url}")
                        logger.debug(f"Empty response on url: {url}")
                        time.sleep(30)
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
                    account = df['account'].apply(pd.Series)

                    df.drop(['account'], axis=1, inplace = True)

                    # Expand statistics column
                    statistics = df['statistics'].apply(pd.Series)
                    actual = statistics['actual'].apply(lambda x: {f'statistics_actual_{k}': v for k, v in x.items()})
                    actual = actual.apply(pd.Series)
                    expected = statistics['expected'].apply(lambda x: {f'statistics_expected_{k}': v for k, v in x.items()})
                    expected = expected.apply(pd.Series)

                    #remove column
                    df.drop(['statistics'], axis=1, inplace = True)

                    #concat expanded account and statistics columns
                    df_full = pd.concat([df, account, actual, expected], axis=1)
                    df_full['date'] = pd.to_datetime(df_full['date'])
                    df_full = df_full.set_index('date', drop=False)

                    # remove shares performed more than one week from first share
                    df_full = df_full.loc[(df_full.index <= df_full.index.min()+ pd.Timedelta('7 day'))]

                    # concat data results in dataframe
                    ct_shares_df = ct_shares_df.append(df_full, ignore_index=True)

                    #clean variables
                    del df
                    del df_full

                except:
                    logger.exception(f"error on {url}")
                    print(f"error on {url}")
                # wait time
                time.sleep(sleep_time)
        except Exception as e:
            logger.exception(f"Exception {e.__class__} occurred.")
            raise e

        if ct_shares_df.empty:
            logger.error("No ct_shares were found!")
            raise SystemExit("\n No ct_shares were found!")

        #if save_ctapi_output is true
        if save_ctapi_output:
            #create dir to save raw data
            Path("rawdata").mkdir(parents=True, exist_ok=True)
            # save raw dataframe
            ct_shares_df.to_csv('rawdata/ct_shares_df.csv', index=False)

        # remove possible inconsistent rows with entity URL equal "https://facebook.com/null"
        ct_shares_df = ct_shares_df[ct_shares_df['account_url'] != "https://facebook.com/null"]

        # get rid of duplicates
        ct_shares_df.drop_duplicates(subset= ["id", "platformId", "postUrl", "expanded"],
                                    inplace=True, ignore_index = True)

        # clean the expanded URLs
        if clean_urls:
                ct_shares_df = Utils.clean_urls(ct_shares_df, "expanded")
                logger.info("expanded URLs have been cleaned")

        logger.info(f"Calculating is_orig field")
        ct_shares_df['is_orig'] = ct_shares_df["expanded"].apply(lambda x: bool(urls['url'].str.contains(x, case=False, regex=False).sum()))

        # write log
        logger.info(f"Original URLs: {len(urls)}")
        logger.info(f"Crowdtangle shares: {len(ct_shares_df)}")
        uni = len(ct_shares_df["expanded"].unique())
        logger.info(f"Unique URL in Crowdtangle shares: {uni}")
        sum_accu = sum(ct_shares_df["account_verified"])
        logger.info(f"Links in CT shares matching original URLs: {sum_accu}")

        return ct_shares_df
