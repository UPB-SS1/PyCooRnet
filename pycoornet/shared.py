import logging
import networkx as nx
import pandas as pd


class Shared:
    """Shared class docsgring
    """

    def __init__(self):
        pass

    def __estimate_coord_interval(self, crowtangle_shares, q=0.1, p=0.5, clean_urls=False, keep_ourl_only=False):
        """Estimates a threshold in seconds that defines a coordinated link share. While it is common that multiple
        (pages/groups/account) entities share the same link, some tend to perform these actions in an unusually short period of time.
        Unusual is thus defined here as a function of the median co-share time difference. More specifically, the function ranks all
        co-shares by time-difference from first share and focuses on the behaviour of the quickest second share performing q\% (default 0.5) URLs.
        The value returned is the median time in seconds spent by these URLs to cumulate the p\% (default 0.1) of their total shares.

        Args:
            crowtangle_shares (pandas.Dataframe): the dataframe of link posts

            q (float, optional): controls the quantile of quickest URLs to be filtered. Defaults to 0.1.

            p (float, optional): controls the percentage of total shares to be reached. Defaults to 0.5.

            clean_urls (bool, optional): clean up unnecessary url paramters and malformed urls, and keep just the URLs included in the original
                data set. Defaults to False.

            keep_ourl_only (bool, optional): restrict the analysis to CrownTangle shares links matching the original URLs. Defaults to False.

        Returns:
            [list]: [description]
        """
        coord_interval = []
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

        return None
