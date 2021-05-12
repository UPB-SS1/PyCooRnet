import logging
import numpy as np
import pandas as pd
from pathlib import Path
import PyCrowdTangle as pct
import time
import glob
import os
from tqdm import tqdm
from ratelimiter import RateLimiter
from .utils import Utils

logger = logging.getLogger(__name__)


class CrowdTangle:
    """Descripción de la clase.

        api_key (str): CrowdTangle API key.
     """

    def __init__(self, api_key):
        """Constructor method
        """
        if not api_key:
            raise Exception('Crowdtangle Api Token is missing')
        self.api_key = api_key

    def get_shares(self, urls, url_column='url', date_column='date', platforms=('facebook', 'instagram'),
                   nmax=1000, max_calls = 2, clean_urls=False, save_ctapi_output=False,
                   temp_saves = False, temp_number = 1000,
                   id_column=None, remove_days=None):
        """ Get the URLs shares from CrowdTangle from a list of URLs with publish datetime

        Args:
            urls (pandas.DataFrame): a dataframe with at least a column "url" containing the URLs, and a column "date" with their published date
            url_column (str, optional): name of the column (placed inside quote marks) where the URLs are stored. Defaults to 'url'.
            date_column (str, optional): name of the column (placed inside quote marks) where the date of the URLs are stored. Defaults to 'date'.
            platforms (tuple, optional): a tuple of platforms to search. You can specify only facebook to search on Facebook, or only instagram to
                                         search on Instagram. Defaults to ('facebook', 'instagram').
            nmax (int, optional): max number of results for query. Defaults to 100.
            max_calls (int, optional): Max number of Api call per minute. It can be lowered or increased
                                        depending on the assigned API rate limit. Defaults to 2.
            clean_urls (bool, optional): clean the URLs from tracking parameters. Defaults to False.
            save_ctapi_output (bool, optional): saves the original CT API output in rawdata/ folder. Defaults to False.
            temp_saves (bool, optional): saves the partial concatenated dataframe to create a final dataframe at the end
            temp_number (int, optional): number of downloaded urls to be saves as temporal, temp_saves has to be set to 'True'
            id_column(str,optional): name of the column wherre the id of each URL is stored.
            remove_days(int,optional): remove shares performed more than X days from first share
        Raises:
            Exception: [description]
            Exception: [description]
            e: [description]
            SystemExit: [description]

        Returns:
            pandas.DataFrame: A pandas dataframe of posts that shared the URLs and a number of variables returned by the https://github.com/CrowdTangle/API/wiki/Links CrowdTangle API links endpoint and the original data set of news.
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

            if temp_saves:
                #create dir to save temporal data
                Path("rawdata").mkdir(parents=True, exist_ok=True)
                # for temporal file numbering
                num =1
                # if temp number is bigger than the number of urls
                if temp_number > len(urls):
                    temp_number = len(urls)//2

            #number of maximum calls to crowdtangle per minute
            rate_limiter = RateLimiter(max_calls=max_calls, period=60)

            # Progress bar tqdm
            for i in tqdm(range(len(urls))):
                # set date limits, endDate: one week after date_published
                startDate = urls.iloc[i, :].loc['date']
                #startDate = startDate.replace(microsecond=0)
                if remove_days:
                    days = f"{remove_days} day"
                    endDate = startDate + pd.Timedelta(days)
                else:
                    endDate = None

                url = urls.iloc[i, :].loc['url']

                #add ratelimit restriction
                with rate_limiter:

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

                        # if id column is specified
                        if id_column:
                            df_full["id_column"] = urls.iloc[i, :].loc[id_column]

                        # remove shares performed more than x days from first share
                        if remove_days:
                            # ex: '7 day'
                            days = f"{remove_days} day"
                            df_full = df_full.loc[(df_full.index <= df_full.index.min()+ pd.Timedelta(days))]

                        # concat data results in dataframe
                        ct_shares_df = ct_shares_df.append(df_full, ignore_index=True)

                        if temp_saves and (i+1) % temp_number == 0:
                            num_str = (str(num)).zfill(4)
                            ct_shares_df.to_feather(os.path.join("rawdata",f"temp_{num_str}.feather"))
                            num+=1
                            ct_shares_df = pd.DataFrame()
                        #clean variables
                        del df
                        del df_full

                    except Exception as e:
                        logger.exception(f"error on {url}")
                        print(f"error on {url}")



        except Exception as e:
            logger.exception(f"Exception {e.__class__} occurred.")
            raise e

        #concatenate files if temp_saves == True
        if temp_saves and num > 1:
            if len(ct_shares_df) > 0:
                num_str = (str(num)).zfill(4)
                ct_shares_df.to_feather(os.path.join("rawdata",f"temp_{num_str}.feather"))
                del ct_shares_df
            try:
                logger.info("starting concatenation of all temp files")
                ct_shares_df = pd.concat(map(pd.read_feather, sorted(glob.glob(os.path.join('rawdata', "*.feather")))))
            except:
                raise SystemExit("\n temporal ct_shares concat failed")

            print("Remember to delete the temporary files in /rawdata")

        if ct_shares_df.empty:
            logger.error("No ct_shares were found!")
            raise SystemExit("\n No ct_shares were found!")

        #if save_ctapi_output is true
        if save_ctapi_output:
            #create dir to save raw data
            Path("rawdata").mkdir(parents=True, exist_ok=True)
            # save raw dataframe
            ct_shares_df.to_csv(os.path.join("rawdata",'ct_shares_df.csv', index=False))

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
        ct_shares_df.reset_index()
        return ct_shares_df
