import logging
import networkx as nx
import pandas as pd
from .utils import Utils


class Shared:
    """Shared class docsgring
    """

    def __init__(self):
        pass

    def __estimate_coord_interval(self, crowtangle_shares_df, q=0.1, p=0.5, clean_urls=False, keep_ourl_only=False):
        """Estimates a threshold in seconds that defines a coordinated link share. While it is common that multiple
        (pages/groups/account) entities share the same link, some tend to perform these actions in an unusually short period of time.
        Unusual is thus defined here as a function of the median co-share time difference. More specifically, the function ranks all
        co-shares by time-difference from first share and focuses on the behaviour of the quickest second share performing q\% (default 0.5) URLs.
        The value returned is the median time in seconds spent by these URLs to cumulate the p\% (default 0.1) of their total shares.

        Args:
            crowtangle_shares_df (pandas.Dataframe): the dataframe of link posts

            q (float, optional): controls the quantile of quickest URLs to be filtered. Defaults to 0.1.

            p (float, optional): controls the percentage of total shares to be reached. Defaults to 0.5.

            clean_urls (bool, optional): clean up unnecessary url paramters and malformed urls, and keep just the URLs included in the original
                data set. Defaults to False.

            keep_ourl_only (bool, optional): restrict the analysis to CrownTangle shares links matching the original URLs. Defaults to False.

        Returns:
            2-element tuple containing

            - **summary** (pandas.DataFrame): summary statistics of q\% quickest second share performing URLs.
            - **time** (integer): time in seconds corresponding to the median time spent by these URLs to cumulate the % of their total shares.
        """
        if 0<p<1 == False:
            logging.error('The p value must be between 0 and 1')
            raise Exception('The p value must be between 0 and 1')

        if 0<q<1 == False:
            logging.error('The q value must be between 0 and 1')
            raise Exception('The q value must be between 0 and 1')


        # keep original URLs only?
        if keep_ourl_only:
            crowtangle_shares_df = crowtangle_shares_df[crowtangle_shares_df['is_orig'] == True]
            if crowtangle_shares_df.shape[0] < 2:
                logging.error("Can't execute with keep_ourl_only=True. Not enough posts matching original URLs")
                raise Exception("Can't execute with keep_ourl_only=TRUE. Not enough posts matching original URLs")
            else:
                logging.info("Coordination interval estimated on shares matching original URLs")

        # clean urls?
        if clean_urls:
            crowtangle_shares_df = Utils.clean_urls(crowtangle_shares_df, 'expanded')
            logging.info('Coordination interval estimated on cleaned URLs')


        crowtangle_shares_df = crowtangle_shares_df[['id', 'date', 'expanded']]

        # count the number of diferent URLs
        urls_df = pd.DataFrame(crowtangle_shares_df['expanded'].value_counts())
        urls_df.reset_index(level=0, inplace=True)
        urls_df.columns = ['URL', 'ct_shares']
        # filter the URLS where the count is > 1
        urls_df = urls_df[urls_df['ct_shares'] >1]

        # filter the crowtangle_shares_df that join with urls_df
        crowtangle_shares_df = crowtangle_shares_df[crowtangle_shares_df.set_index('expanded').index.isin(urls_df.set_index('URL').index)]

        #metrics creation
        crowtangle_shares_df['date'] = crowtangle_shares_df['date'].astype('datetime64[ns]')
        ranked_shares_df = crowtangle_shares_df[['expanded', 'date']]
        shares_gb = crowtangle_shares_df.groupby('expanded')
        ranked_shares_df['ct_shares_count']=shares_gb['id'].transform('nunique')
        ranked_shares_df['first_share_date'] = shares_gb['date'].transform('min')
        ranked_shares_df['rank'] = shares_gb['date'].rank(ascending=True, method='first')
        ranked_shares_df['sec_from_first_share'] = (ranked_shares_df['date'] - ranked_shares_df['first_share_date']).dt.seconds
        ranked_shares_df['perc_of_shares'] = ranked_shares_df['rank']/ranked_shares_df['ct_shares_count']

        filtered_ranked_df = ranked_shares_df[ranked_shares_df['rank']==2].copy(deep=True)
        filtered_ranked_df['sec_from_first_share'] = filtered_ranked_df.groupby('expanded')['sec_from_first_share'].transform('min')
        filtered_ranked_df = filtered_ranked_df[['expanded', 'sec_from_first_share']]
        filtered_ranked_df = filtered_ranked_df.drop_duplicates()

        filtered_ranked_df = filtered_ranked_df[filtered_ranked_df['sec_from_first_share']<=filtered_ranked_df['sec_from_first_share'].quantile(q)]


        # filter the ranked_shares_df that join with filtered_ranked_df
        ranked_shares_df = ranked_shares_df[ranked_shares_df.set_index('expanded').index.isin(filtered_ranked_df.set_index('expanded').index)]

        #filter the results by p value
        ranked_shares_sub_df = ranked_shares_df[ranked_shares_df['perc_of_shares']>p].copy(deep=True)
        ranked_shares_sub_df['sec_from_first_share'] = ranked_shares_sub_df.groupby('sec_from_first_share')['sec_from_first_share'].transform('min')
        ranked_shares_sub_df = ranked_shares_sub_df[['expanded', 'sec_from_first_share']]
        ranked_shares_sub_df = ranked_shares_sub_df.drop_duplicates()

        summary_secs = ranked_shares_sub_df['sec_from_first_share'].describe()
        coordination_interval= ranked_shares_sub_df['sec_from_first_share'].quantile(p)

        coord_interval = (None, None)

        if coordination_interval == 0:
            coordination_interval = 1
            coord_interval = (summary_secs, coordination_interval)
            logging.warning(f'q (quantile of quickest URLs to be filtered): {q}')
            logging.warning(f'p (percentage of total shares to be reached): {p}')
            logging.warning(f'coordination interval from estimate_coord_interval: {coordination_interval}')
            logging.warning('Warning: with the specified parameters p and q the median was 0 secs. The coordination interval has been automatically set to 1 secs')
        else:
            coord_interval = (summary_secs, coordination_interval)
            logging.info(f'q (quantile of quickest URLs to be filtered): {q}')
            logging.info(f'p (percentage of total shares to be reached): {p}')
            logging.info(f'coordination interval from estimate_coord_interval: {coordination_interval}')

        return coord_interval

    def coord_shares(self, dataframe, coordination_interval=None, parallel=False, percentile_edge_weight=0.90, clean_urls=False, keep_ourl_only=False, gtimestamps=False):
        """Given a dataframe of CrowdTangle shares and a time threshold, this function detects networks of entities (pages, accounts and groups)
        that performed coordinated link sharing behavior.

        Args:
            dataframe (pandas.DataFrame): the pandas dataframe of link posts resulting from the function
                CrowdTangle shares

            coordination_interval (int, optional): a threshold in seconds that defines a coordinated share.
                Given a dataset of CrowdTangle shares, this threshold is automatically estimated. Alternatively
                it can be manually passed to the function in seconds. Defaults to None.

            parallel (bool, optional): enables parallel processing to speed up the process taking advantage
                of multiple cores. The number of cores is automatically set to all the available cores minus one.
                Defaults to False.

            percentile_edge_weight (float, optional): defines the percentile of the edge distribution to keep in order
                to identify a network of coordinated entities. In other terms, this value determines the minimum number
                of times that two entities had to coordinate in order to be considered part of a network. Defaults to 0.90.

            clean_urls (bool, optional): clean the URLs from the tracking parameters. Defaults to False.

            keep_ourl_only (bool, optional): restrict the analysis to ct shares links matching the original URLs.
                Defaults to False.

            gtimestamps (bool, optional): add timestamps of the fist and last coordinated shares on each node.
                Slow on large networks. Defaults to False.

        Returns:
            3-element tuple containing

            - **coordinated_df** (pandas.DataFrame): The input dataframe of shares with an additional boolean variable (coordinated) that identifies coordinated shares.
            - **graph** (networkx.Graph): An graph (highly_connected_g) with networks of coordinated entities whose edges also contains a t_coord_share attribute (vector) reporting the timestamps of every time the edge was detected as coordinated sharing.
            - **conected_coordinated_df** (pandas.DataFrame): A dataframe with a list of coordinated entities (highly_connected_coordinated_entities) with respective name (the account url), number of shares performed, average subscriber count, platform, account name, if the account name changed, if the account is verified, account handle, degree and component number
        """
        # estimate the coordination interval if not specified by the users
        if coordination_interval == None:
            coordination_interval = self.__estimate_coord_interval(dataframe, clean_urls=clean_urls, keep_ourl_only=keep_ourl_only)
            coordination_interval = coordination_interval[1]

        if coordination_interval == 0:
            raise Exception("The coordination_interval value can't be 0. Please choose a value greater than zero or use coordination_interval=None to automatically calculate the interval")

        if keep_ourl_only == True:
            dataframe = dataframe[dataframe['is_orig'] == True]
            if dataframe < 2:
                raise Exception ("Can't execute with keep_ourl_only=TRUE. Not enough posts matching original URLs")

        if clean_urls:
            dataframe =  Utils.clean_urls(dataframe, 'expanded')

        urls_df = pd.DataFrame(dataframe['expanded'].value_counts())
        urls_df.reset_index(level=0, inplace=True)
        urls_df.columns = ['URL', 'ct_shares']
        urls_df = urls_df[urls_df['ct_shares'] >1]

        crowtangle_shares_df = dataframe[dataframe.set_index('expanded').index.isin(urls_df.set_index('URL').index)]

        if parallel:
            pass
        else:
            data_list = []
            for index, row in urls_df.iterrows():
                summary_df = crowtangle_shares_df[crowtangle_shares_df['expanded'] == row['URL']].copy(deep=True)
                len = summary_df.groupby('account.url')['account.url'].nunique()
                if summary_df.groupby('account.url')['account.url'].nunique().shape[0]>1:
                    summary_df['date'] = summary_df['date'].astype('datetime64[ns]')
                    #summary_df['cut'] = pd.cut(summary_df['date'], int(coordination_interval))
                    date_serie = summary_df['date'].astype('int64') // 10 ** 9
                    max = date_serie.max()
                    min = date_serie.min()
                    div = (max-min)/coordination_interval + 1
                    summary_df['cut']  = pd.cut(summary_df['date'].astype('int64') // 10 ** 9, int(div))
                    summary_gb = summary_df.groupby('cut')
                    summary_df['count'] = summary_gb['cut'].transform('nunique')
                    #Revisar si los otros pasos del mutate son necesarios, ya que no lo veo asi
                    #mutate(count = n(), account.url = list(account.url), share_date = list(date), url = url)
                    summary_df = summary_df[['cut', 'count', 'account.url', 'date']]
                    summary_df.rename(columns = {'date': 'share_date'}, inplace = True)
                    summary_df = summary_df[summary_df['count']>1]
                    summary_df = summary_df.drop_duplicates()
                    data_list.append(summary_df)

            data_df = pd.concat(data_list)
            if data_df.shape[0] == 0:
                logging.info('there are not enough shares!')
                return None

        return None
