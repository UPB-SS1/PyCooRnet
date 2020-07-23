import logging
import numpy as np
import pandas as pd
import PyCrowdTangle as pct
from tqdm import tqdm
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import time
from pathlib import Path

def get_shares(urls, url_column='url', date_column='date', platforms=('facebook', 'instagram'), nmax=500, token='', sleep_time=30, clean_urls=False, save_ctapi_output=False):

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
        :param token: Crowdtangle API token
        :type token: str,
        :param sleep_time: pause between queries to respect API rate limits. Default to 30 secs, it can be lowered or increased depending on the assigned API rate limit, defaults to 30
        :type sleep_time: int, optional
        :param clean_urls: clean the URLs from tracking parameters, defaults to False
        :type clean_urls: bool, optional
        :param save_ctapi_output: saves the original CT API output in ./rawdata/ct_shares.df.0.rds, defaults to False
        :type save_ctapi_output: bool, optional
        :return: A pandas dataframe of posts that shared the URLs and a number of variables returned by the https://github.com/CrowdTangle/API/wiki/Links CrowdTangle API links endpoint and the original data set of news.
        :rtype: pandas.DataFrame

        Example: salida = get_shares(data_in, url_column='url', date_column='publish_date',
                          platforms='facebook', token='ajhdfjadklfjhakldjfhklasdkflja',
                          sleep_time = 1, nmax = 100)
    """
    #check if api token is present
    if not token:
        message = "Crowdtangle Api Token is missing"
        raise Exception(message)


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
                                        api_token=token
                                        )
                #convert json response to dataframe
                df = pd.DataFrame(data['result']['posts'])
                # Extract account info from column and convert to columns

                # add prefix name to each key of the dictionary per row in 'account' column
                df['account'] = df['account'].apply(lambda x: {f'account_{k}': v for k, v in x.items()})
                # convert dictionary info in each row to columns
                partes = df['account'].apply(pd.Series)

                df_full = pd.concat([df, partes], axis = 1).drop(['account'], axis = 1)
                # concat data results in dataframe
                ct_shares_df = ct_shares_df.append(df_full, ignore_index = True)
            except:
                print(f"Unexpected http response code on url {url}")
            # wait time
            time.sleep(sleep_time)
    except Exception as e:
        raise e
    if ct_shares_df.dropna().empty:
        raise SystemExit("\n No ct_shares were found!")
    if save_ctapi_output:
        Path("./rawdata").mkdir(parents=True, exist_ok=True)
        ct_shares_df.to_csv('./rawdata/ct_shares_df', index=False)
    # remove possible inconsistent rows with entity URL equal "https://facebook.com/null"
    #ct_shares_df = ct_shares_df[ct_shares_df['url'] != "https://facebook.com/null"]
    # get rid of duplicates
    #ct_shares_df.drop_duplicates(inplace=True)
    # remove shares performed more than one week from first share
    # clean the expanded URLs
    # write log
    return ct_shares_df
