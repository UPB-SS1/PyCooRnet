import community as community_louvain
import logging
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import pandas as pd
from tqdm import tqdm
from .utils import Utils

logger = logging.getLogger(__name__)



class Shared:

    """Coordinated Link Sharing Behavor (CLSB) detector.

    Args:
        crowdtangle_shares_df (pandas.DataFrame): the pandas dataframe of link posts resulting from the function
                CrowdTangle shares
    """
    def __init__(self, crowdtangle_shares_df):
        self.__crowdtangle_shares_df = crowdtangle_shares_df

    def estimate_coord_interval(self, q=0.1, p=0.5, clean_urls=False, keep_ourl_only=False):
        """
        Estimates a threshold in seconds that defines a coordinated link share. While it is common that multiple
        (pages/groups/account) entities share the same link, some tend to perform these actions in an unusually short period of time.
        Unusual is thus defined here as a function of the median co-share time difference. More specifically, the function ranks all
        co-shares by time-difference from first share and focuses on the behaviour of the quickest second share performing q% (default 0.5) URLs.
        The value returned is the median time in seconds spent by these URLs to cumulate the p% (default 0.1) of their total shares.

        Args:

            q (float, optional): controls the quantile of quickest URLs to be filtered. Defaults to 0.1.

            p (float, optional): controls the percentage of total shares to be reached. Defaults to 0.5.

            clean_urls (bool, optional): clean up unnecessary url paramters and malformed urls, and keep just the URLs included in the original
                data set. Defaults to False.

            keep_ourl_only (bool, optional): restrict the analysis to CrownTangle shares links matching the original URLs. Defaults to False.

        Returns:
            (tuple): 2-element tuple containing

                - **summary** (pandas.DataFrame): summary statistics of q% quickest second share performing URLs.
                - **coordination interval** (integer): time in seconds corresponding to the median time spent by these URLs to cumulate the % of their total shares.
        """
        if 0<p<1 == False:
            logger.error('The p value must be between 0 and 1')
            raise Exception('The p value must be between 0 and 1')

        if 0<q<1 == False:
            logger.error('The q value must be between 0 and 1')
            raise Exception('The q value must be between 0 and 1')

        crowdtangle_shares_df = self.__crowdtangle_shares_df.copy(deep=True)

        # keep original URLs only?
        if keep_ourl_only:
            crowdtangle_shares_df = crowdtangle_shares_df[crowdtangle_shares_df['is_orig'] == True]
            if crowdtangle_shares_df.shape[0] < 2:
                logger.error("Can't execute with keep_ourl_only=True. Not enough posts matching original URLs")
                raise Exception("Can't execute with keep_ourl_only=TRUE. Not enough posts matching original URLs")
            else:
                logger.info("Coordination interval estimated on shares matching original URLs")

        # clean urls?
        if clean_urls:
            crowdtangle_shares_df = Utils.clean_urls(crowdtangle_shares_df, 'expanded')
            logger.info('Coordination interval estimated on cleaned URLs')


        crowdtangle_shares_df = crowdtangle_shares_df[['id', 'date', 'expanded']]

        # count the number of diferent URLs
        urls_df = pd.DataFrame(crowdtangle_shares_df['expanded'].value_counts())
        urls_df.reset_index(level=0, inplace=True)
        urls_df.columns = ['URL', 'ct_shares']
        # filter the URLS where the count is > 1
        urls_df = urls_df[urls_df['ct_shares'] >1]

        # filter the crowdtangle_shares_df that join with urls_df
        crowdtangle_shares_df = crowdtangle_shares_df[crowdtangle_shares_df.set_index('expanded').index.isin(urls_df.set_index('URL').index)]

        #metrics creation
        crowdtangle_shares_df['date'] = crowdtangle_shares_df['date'].astype('datetime64[ns]')
        ranked_shares_df = crowdtangle_shares_df[['expanded', 'date']]
        shares_gb = crowdtangle_shares_df.groupby('expanded')
        ranked_shares_df['ct_shares_count']=shares_gb['id'].transform('nunique')
        ranked_shares_df['first_share_date'] = shares_gb['date'].transform('min')
        ranked_shares_df['rank'] = shares_gb['date'].rank(ascending=True, method='first')
        ranked_shares_df['perc_of_shares'] = ranked_shares_df['rank']/ranked_shares_df['ct_shares_count']
        ranked_shares_df['sec_from_first_share'] = (ranked_shares_df['date'] - ranked_shares_df['first_share_date']).dt.total_seconds()
        ranked_shares_df = ranked_shares_df.sort_values(by = 'expanded')

        #find URLs with an unusual fast second share and keep the quickest
        filtered_ranked_df = ranked_shares_df[ranked_shares_df['rank']==2].copy(deep=True)
        filtered_ranked_df['sec_from_first_share'] = filtered_ranked_df.groupby('expanded')['sec_from_first_share'].transform('min')
        filtered_ranked_df = filtered_ranked_df[['expanded', 'sec_from_first_share']]
        filtered_ranked_df = filtered_ranked_df.drop_duplicates()

        filtered_ranked_df = filtered_ranked_df[filtered_ranked_df['sec_from_first_share']<=filtered_ranked_df['sec_from_first_share'].quantile(q)]


        # filter the ranked_shares_df that join with filtered_ranked_df
        ranked_shares_df = ranked_shares_df[ranked_shares_df.set_index('expanded').index.isin(filtered_ranked_df.set_index('expanded').index)]
        #filter the results by p value
        ranked_shares_sub_df = ranked_shares_df[ranked_shares_df['perc_of_shares']>p].copy(deep=True)
        ranked_shares_sub_df['sec_from_first_share'] = ranked_shares_sub_df.groupby('expanded')['sec_from_first_share'].transform('min')
        ranked_shares_sub_df = ranked_shares_sub_df[['expanded', 'sec_from_first_share']]
        ranked_shares_sub_df = ranked_shares_sub_df.drop_duplicates()

        summary_secs = ranked_shares_sub_df['sec_from_first_share'].describe()
        coordination_interval= ranked_shares_sub_df['sec_from_first_share'].quantile(p)

        coord_interval = (None, None)

        if coordination_interval == 0:
            coordination_interval = 1
            coord_interval = (summary_secs, coordination_interval)
            logger.warning(f'q (quantile of quickest URLs to be filtered): {q}')
            logger.warning(f'p (percentage of total shares to be reached): {p}')
            logger.warning(f'coordination interval from estimate_coord_interval: {coordination_interval}')
            logger.warning('Warning: with the specified parameters p and q the median was 0 secs. The coordination interval has been automatically set to 1 secs')
        else:
            coord_interval = (summary_secs, coordination_interval)
            logger.info(f'q (quantile of quickest URLs to be filtered): {q}')
            logger.info(f'p (percentage of total shares to be reached): {p}')
            logger.info(f'coordination interval from estimate_coord_interval: {coordination_interval}')

        return coord_interval

    def __buid_graph(self, crowdtangle_shares_df, coordinated_shares_df, percentile_edge_weight = 90, timestamps = False):
        logger.info("Bulding graph")
        coord_df = coordinated_shares_df[['account_url', 'url', 'share_date']].reset_index(drop=True)
        coord_graph = nx.from_pandas_edgelist(coord_df, 'account_url', 'url', create_using=nx.DiGraph())

        # Remove self loop node edges
        coord_graph.remove_edges_from(nx.selfloop_edges(coord_graph))

        #Bipartite graph creation
        account_urls = list(coordinated_shares_df['account_url'].unique())
        urls = list(coordinated_shares_df['url'].unique())

        bipartite_graph = nx.Graph()
        logger.debug('adding nodes')
        bipartite_graph.add_nodes_from(urls, bipartite=0)
        bipartite_graph.add_nodes_from(account_urls, bipartite=1)
        logger.debug('Adding edges')
        for index, row in coord_df.iterrows():
            bipartite_graph.add_edge(row['account_url'], row['url'], share_date=row['share_date'])

        #Graph projection with account nodes
        logger.debug('Projecting graph')
        full_graph = bipartite.weighted_projected_graph(bipartite_graph, account_urls)

        #pandas helper dataframe to calcule graph node attribues
        crowdtangle_shares_df['account_name'] = crowdtangle_shares_df['account_name'].astype(str)
        crowdtangle_shares_df['account_handle'] = crowdtangle_shares_df['account_handle'].astype(str)
        crowdtangle_shares_df['account_pageAdminTopCountry'] = crowdtangle_shares_df['account_pageAdminTopCountry'].astype(str)
        crowtangle_shares_gb = crowdtangle_shares_df.groupby('account_url')
        crowdtangle_shares_df['name_changed']=(crowtangle_shares_gb['account_name'].transform("nunique"))>1
        crowdtangle_shares_df['handle_changed']=(crowtangle_shares_gb['account_handle'].transform("nunique"))>1
        crowdtangle_shares_df['page_admin_top_country_changed']=(crowtangle_shares_gb['account_pageAdminTopCountry'].transform("nunique"))>1
        crowdtangle_shares_df['account_name'] = crowtangle_shares_gb['account_name'].transform(lambda col: '|'.join(col.unique()))
        crowdtangle_shares_df['account_handle'] = crowtangle_shares_gb['account_handle'].transform(lambda col: '|'.join(col.unique()))
        crowdtangle_shares_df['account_pageAdminTopCountry'] = crowtangle_shares_gb['account_pageAdminTopCountry'].transform(lambda col: '|'.join(col.unique()))
        crowdtangle_shares_df[['account_name','account_handle','account_pageAdminTopCountry','name_changed','handle_changed','page_admin_top_country_changed']]

        crowtangle_shares_gb = crowdtangle_shares_df.reset_index().groupby(['account_url'])

        account_info_df = crowtangle_shares_gb['index'].agg([('shares','count')])
        account_info_df = account_info_df.merge(pd.DataFrame(crowtangle_shares_gb['is_coordinated'].apply(lambda x: (x==True).sum())).rename(columns={'is_coordinated':'coord_shares'}), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_subscriberCount'].agg([('avg_account_subscriber_count','mean')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_name'].agg([('account_name','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['name_changed'].agg('first'), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['handle_changed'].agg('first'), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['page_admin_top_country_changed'].agg('first'), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_pageAdminTopCountry'].agg([('account_page_admin_top_country','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_handle'].agg([('account_handle','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_platform'].agg([('account_platform','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_platformId'].agg([('account_platformId','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_verified'].agg([('account_verified','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.merge(crowtangle_shares_gb['account_accountType'].agg([('account_account_type','first')]), left_index=True, right_index=True)
        account_info_df = account_info_df.reset_index().rename(columns={'account_url':'account_url'})

        #filter the dataframe with the graph nodes
        node_info_df = account_info_df[account_info_df['account_url'].isin(list(full_graph.nodes))]

        attributes= []
        for node in full_graph.nodes():
            records = node_info_df[node_info_df['account_url']==node]
            attributes.append(node)
            attributes.append({
                    'shares': records['shares'].values[0],
                    'coord_shares': records['coord_shares'].values[0],
                    'avg_account_subscriber_count': records['avg_account_subscriber_count'].values[0],
                    'account_platform': records['account_platform'].values[0],
                    'account_name': records['account_name'].values[0],
                    'account_verified': 1 if records['account_verified'].values[0] else 0,
                    'account_handle': records['account_handle'].values[0],
                    'name_changed': 1 if records['name_changed'].values[0] else 0,
                    'handle_changed': 1 if records['handle_changed'].values[0] else 0,
                    'page_admin_top_country_changed': 1 if records['page_admin_top_country_changed'].values[0] else 0,
                    'account_page_admin_top_country': records['account_page_admin_top_country'].values[0],
                    'account_account_type': records['account_account_type'].values[0]

            })
        #update graph attributes
        it = iter(attributes)
        nx.set_node_attributes(full_graph, dict(zip(it, it)))

        #set the percentile_edge_weight number of repetedly coordinated link sharing to keep
        q = np.percentile([d['weight'] for (u,v,d) in full_graph.edges(data=True)], percentile_edge_weight)

        #create a new graph where node degree > 0
        highly_connected_graph = full_graph.subgraph([key for (key,value) in full_graph.degree if value>0]).copy()

        #remove where the edge weitght is less than the given percentile value
        edges_to_remove = [(u,v) for (u,v,d) in highly_connected_graph.edges(data=True) if d['weight']<q]
        highly_connected_graph.remove_edges_from(edges_to_remove)
        highly_connected_graph.remove_nodes_from(list(nx.isolates(highly_connected_graph)))

        if timestamps:
            logger.info("Calculating nodes timestamps")
            vec_func = np.vectorize(lambda u,v: bipartite_graph.get_edge_data(u,v)['share_date'])
            attributes = []
            for (u,v) in highly_connected_graph.edges():
                attributes.append((u,v))
                attributes.append({"timestamp_coord_share":vec_func(np.intersect1d(list(list(bipartite_graph.neighbors(u))),list(list(bipartite_graph.neighbors(v)))),u)})

            it = iter(attributes)
            nx.set_edge_attributes(highly_connected_graph, dict(zip(it, it)))
            logger.info("timestamps calculated")

        #find and annotate nodes-components
        connected_components=list(nx.connected_components(highly_connected_graph))
        components_df = pd.DataFrame({"node": connected_components, "component": [*range(1,len(connected_components)+1)]})
        components_df['node'] = components_df['node'].apply(lambda x: list(x))
        components_df = components_df.explode('node')

        #add cluster to simplyfy the analysis of large components
        cluster_df = pd.DataFrame(community_louvain.best_partition(highly_connected_graph).items(), columns=['node', 'cluster'])

         #re-calculate the degree on the graph
        degree_df = pd.DataFrame(list(highly_connected_graph.degree()), columns=['node', 'degree'])
        #sum up the edge weights of the adjacent edges for each node
        strength_df = pd.DataFrame(list(highly_connected_graph.degree(weight='weight')), columns=['node', 'strength'])

        attributes_df = components_df.merge(cluster_df, on='node').merge(degree_df, on='node').merge(strength_df, on='node')

        #update graph attribues
        nx.set_node_attributes(highly_connected_graph, attributes_df.set_index('node').to_dict('index'))
        logger.info("graph builded")

        return highly_connected_graph, q


    def coord_shares(self, coordination_interval=None, percentile_edge_weight=90, clean_urls=False, keep_ourl_only=False, gtimestamps=False):
        """Given a dataframe of CrowdTangle shares and a time threshold, this function detects networks of entities (pages, accounts and groups)
        that performed coordinated link sharing behavior.

        Args:
            coordination_interval (int, optional): a threshold in seconds that defines a coordinated share.
                Given a dataset of CrowdTangle shares, this threshold is automatically estimated. Alternatively
                it can be manually passed to the function in seconds. Defaults to None.

            percentile_edge_weight (float, optional): defines the percentile of the edge distribution to keep in order
                to identify a network of coordinated entities. In other terms, this value determines the minimum number
                of times that two entities had to coordinate in order to be considered part of a network. Defaults to 0.90.

            clean_urls (bool, optional): clean the URLs from the tracking parameters. Defaults to False.

            keep_ourl_only (bool, optional): restrict the analysis to ct shares links matching the original URLs.
                Defaults to False.

            gtimestamps (bool, optional): add timestamps of the fist and last coordinated shares on each node.
                Slow on large networks. Defaults to False.

        Returns:
            (tuple): 3-element tuple containing

                - **coordinated_df** (pandas.DataFrame): The input dataframe of shares with an additional boolean variable (coordinated) that identifies coordinated shares.
                - **graph** (networkx.Graph): An graph (highly_connected_g) with networks of coordinated entities whose edges also contains a t_coord_share attribute (vector) reporting the timestamps of every time the edge was detected as coordinated sharing.
                - **q** (networkx.Graph): Percentile edge weight number of leeped repetedly coordinated link sharing.
                - **coordination_interval** (int): coordination time in seconds
        """
        # estimate the coordination interval if not specified by the users
        dataframe = self.__crowdtangle_shares_df.copy(deep=True)
        if coordination_interval == None:
            coordination_interval = self.estimate_coord_interval(clean_urls=clean_urls, keep_ourl_only=keep_ourl_only)
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
        urls_df = urls_df.sort_values('URL')

        crowdtangle_shares_df = dataframe[dataframe.set_index('expanded').index.isin(urls_df.set_index('URL').index)]

        data_list = []
        urls_count = urls_df.shape[0]
        i=0

        with tqdm(total=urls_df.shape[0]) as pbar:
            for index, row in urls_df.iterrows():
                pbar.update(1)
                i=i+1
                logger.debug(f"processing {i} of {urls_count}, url={row['URL']}")
                summary_df = crowdtangle_shares_df[crowdtangle_shares_df['expanded'] == row['URL']].copy(deep=True)
                if summary_df.groupby('account_url')['account_url'].nunique().shape[0]>1:
                    summary_df['date'] = summary_df['date'].astype('datetime64[ns]')
                    date_serie = summary_df['date'].astype('int64') // 10 ** 9
                    max = date_serie.max()
                    min = date_serie.min()
                    div = (max-min)/coordination_interval + 1
                    logger.debug(f"cutting row['URL'] in {div} parts")
                    summary_df["cut"] = pd.cut(summary_df['date'],int(div)).apply(lambda x: x.left).astype('datetime64[ns]')
                    cut_gb = summary_df.groupby('cut')
                    summary_df.loc[:,'count'] = cut_gb['cut'].transform('count')
                    summary_df.loc[:,'url'] = row['URL']
                    summary_df.loc[:,'account_url'] = cut_gb['account_url'].transform(lambda x: [x.tolist()]*len(x))
                    summary_df.loc[:,'share_date'] = cut_gb['date'].transform(lambda x: [x.tolist()]*len(x))
                    summary_df = summary_df[['cut', 'count', 'account_url','share_date', 'url']]
                    summary_df = summary_df[summary_df['count']>1]
                    if summary_df.shape[0]>1:
                        summary_df = summary_df.loc[summary_df.astype(str).drop_duplicates().index]
                        data_list.append(summary_df)

        data_df = pd.concat(data_list)
        if data_df.shape[0] == 0:
            logger.info('there are not enough shares!')
            return None

        coordinated_shares_df = data_df.reset_index(drop=True).apply(pd.Series.explode).reset_index(drop=True)

        crowdtangle_shares_df = crowdtangle_shares_df.reset_index(drop=True)
        crowdtangle_shares_df.loc[:,'coord_expanded']=crowdtangle_shares_df['expanded'].isin(coordinated_shares_df['url'])
        crowdtangle_shares_df.loc[:,'coord_date']=crowdtangle_shares_df['date'].astype('datetime64[ns]').isin(coordinated_shares_df['share_date'])
        crowdtangle_shares_df.loc[:,'coord_account_url']=crowdtangle_shares_df['account_url'].isin(coordinated_shares_df['account_url'])

        crowdtangle_shares_df.loc[:,'is_coordinated'] = crowdtangle_shares_df.apply(lambda x : True if (x['coord_expanded'] and x['coord_date'] and x['coord_account_url']) else False, axis=1)
        crowdtangle_shares_df.drop(['coord_expanded','coord_date', 'coord_account_url'], inplace = True, axis=1)

        highly_connected_graph, q =  self.__buid_graph(crowdtangle_shares_df, coordinated_shares_df, percentile_edge_weight=percentile_edge_weight, timestamps=gtimestamps)

        return crowdtangle_shares_df, highly_connected_graph, q

    def coord_shares_differential(self, coordination_interval=None, percentile_edge_weight=90, clean_urls=False, keep_ourl_only=False, gtimestamps=False):
        dataframe = self.__crowdtangle_shares_df.copy(deep=True)
        if coordination_interval == None:
            coordination_interval = self.estimate_coord_interval(clean_urls=clean_urls, keep_ourl_only=keep_ourl_only)
            coordination_interval = coordination_interval[1]

        if coordination_interval == 0:
            raise Exception("The coordination_interval value can't be 0. Please choose a value greater than zero or use coordination_interval=None to automatically calculate the interval")

        if keep_ourl_only == True:
            dataframe = dataframe[dataframe['is_orig'] == True]
            if dataframe < 2:
                raise Exception ("Can't execute with keep_ourl_only=TRUE. Not enough posts matching original URLs")

        if clean_urls:
            logger.debug("cleaning urls")
            dataframe =  Utils.clean_urls(dataframe, 'expanded')

        dataframe = dataframe.sort_values(['expanded', 'date'])
        counts_serie = dataframe['expanded'].value_counts()

        logger.debug('selecting urls with more than 1 share')
        urls_serie = counts_serie.where(lambda x : x>1).dropna().index.to_list()
        filtered_df =dataframe.query("expanded in @urls_serie").copy()
        logger.debug("features")
        del urls_serie
        filtered_df.loc[:,'diff']=filtered_df.groupby('expanded')['date'].diff().dt.total_seconds().fillna(0)
        filtered_df.loc[:,'valid_delta'] = filtered_df['diff']<= coordination_interval
        filtered_df.loc[:,'valid_before'] = filtered_df.groupby('expanded')['valid_delta'].shift(-1)

        logger.debug('selecting valid shares')
        coord_df = filtered_df.copy(deep=True)
        coord_df = coord_df.query('valid_delta | valid_before==True')

        logger.debug('deleting first shares that not are coordinated')

        # Delete the first share of every group if this is not coordinated
        delete_df = coord_df.reset_index().groupby('expanded').first().query("valid_before == False")
        coord_df = coord_df.drop(delete_df['index'])

        coord_gb=coord_df.reset_index().groupby('expanded')

        logger.debug('creating vectorized columns')
        data_df = pd.DataFrame({'count':coord_gb['expanded'].count(), 'date':coord_gb['date'].apply(lambda x: x.tolist()), 'account_url': coord_gb['account_url'].apply(lambda x: x.tolist())})

        if data_df.shape[0] == 0:
            logger.info('there are not enough shares!')
            return None

        logger.debug('exploding')
        coordinated_shares_df = data_df.reset_index().apply(pd.Series.explode)
        logger.debug('joining data')
        analyzed_df = filtered_df.set_index(['expanded','date', 'account_url']).join(coordinated_shares_df.drop_duplicates().set_index(['expanded','date', 'account_url'])).reset_index()
        logger.debug('calculating coordinates')
        analyzed_df.loc[:, 'is_coordinated'] = analyzed_df['count'].notna()
        analyzed_df.drop(['count', 'diff', 'valid_delta', 'valid_before'], inplace = True, axis=1)

        logger.debug('bulding graph')
        highly_connected_graph, q =  self.__buid_graph(analyzed_df, coordinated_shares_df.rename(columns = {'expanded':'url', 'date':'share_date'}), percentile_edge_weight=percentile_edge_weight, timestamps=gtimestamps)


        return analyzed_df, highly_connected_graph, q

