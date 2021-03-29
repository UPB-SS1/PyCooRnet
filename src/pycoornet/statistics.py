import networkx as nx
import numpy as np
import pandas as pd
import tldextract
from urllib.parse import urlparse


class Statistics:
    @staticmethod
    def __gini(arr, eps=1e-8):

        # All values are treated equally, arrays must be 1d and > 0:
        arr = np.abs(arr).flatten() + eps

        # Values must be sorted:
        arr = np.sort(arr)

        # Index per array element:
        index = np.arange(1, arr.shape[0]+1)

        # Number of array elements:
        N = arr.shape[0]

        # Gini coefficient:
        return(np.sum((2*index - N - 1)*arr))/(N*np.sum(arr))

    @staticmethod
    def component_summary(crowtangle_shares_df, shares_graph):
        ct_shares_marked_df = crowtangle_shares_df[crowtangle_shares_df['is_coordinated']].copy()
        highly_connected_coordinated_entities_df = pd.DataFrame.from_dict(dict(shares_graph.nodes(data=True)), orient='index').reset_index().rename({'index':'name'}, axis = 'columns')

        ct_shares_marked_df['full_domain'] = ct_shares_marked_df['expanded'].apply(lambda x: urlparse(x).netloc)
        ct_shares_marked_df['parent_domain'] = ct_shares_marked_df['expanded'].apply(lambda x: f"{tldextract.extract(x).domain}.{tldextract.extract(x).suffix}")
        ct_shares_marked_df = pd.merge(ct_shares_marked_df, highly_connected_coordinated_entities_df[['name','component']], left_on='account_url', right_on='name')

        highly_connected_coordinated_entities_gb = highly_connected_coordinated_entities_df.groupby('component')

        summary_entities_df = highly_connected_coordinated_entities_gb.size().to_frame('entities').sort_index()
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_gb['avg_account_subscriber_count'].mean().to_frame('avg_subscriber_count'), left_index=True, right_index=True)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_gb.apply(lambda x: (x['coord_shares']/(x['shares']+x['coord_shares'])).mean()).to_frame('coor_share_ratio_avg'), left_index=True, right_index=True)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_gb.apply(lambda x: (x['strength']/x['degree']).mean()).to_frame('coor_score_avg'), left_index=True, right_index=True)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_gb['account_page_admin_top_country'].agg(pd.Series.mode).to_frame('page_admin_top_country'), left_index=True, right_index=True)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_df[highly_connected_coordinated_entities_df['account_account_type']=='facebook_page'].groupby('component').size().to_frame('facebook_page'), left_index=True, right_index=True, how='left').fillna(0)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_df[highly_connected_coordinated_entities_df['account_account_type']=='facebook_group'].groupby('component').size().to_frame('facebook_group'), left_index=True, right_index=True, how='left').fillna(0)
        summary_entities_df = pd.merge(summary_entities_df, highly_connected_coordinated_entities_df[highly_connected_coordinated_entities_df['account_account_type']=='facebook_profile'].groupby('component').size().to_frame('facebook_profile'), left_index=True, right_index=True, how='left').fillna(0)

        ct_shares_marked_gb = ct_shares_marked_df.groupby('component')

        summary_domains_df = ct_shares_marked_gb['full_domain'].nunique().to_frame('unique_full_domain')
        summary_domains_df = pd.merge(summary_domains_df, ct_shares_marked_gb['parent_domain'].nunique().to_frame('unique_parent_domain'), left_index=True, right_index=True)

        summary_df = pd.merge(summary_entities_df, summary_domains_df, left_index=True, right_index=True)
        summary_df = pd.merge(summary_df, ct_shares_marked_gb['full_domain'].apply(lambda x: Statistics.__gini(x.value_counts().to_list())).to_frame('gini_full_domain'), left_index=True, right_index=True)
        summary_df = pd.merge(summary_df, ct_shares_marked_gb['parent_domain'].apply(lambda x: Statistics.__gini(x.value_counts().to_list())).to_frame('gini_parent_domain'), left_index=True, right_index=True)
        summary_df = pd.merge(summary_df, ct_shares_marked_gb['full_domain'].apply(lambda x: x.value_counts().nlargest().index.to_list()).to_frame('top_full_domain'), left_index=True, right_index=True)
        summary_df = pd.merge(summary_df, ct_shares_marked_gb['parent_domain'].apply(lambda x: x.value_counts().nlargest().index.to_list()).to_frame('top_parent_domain'), left_index=True, right_index=True)

        return summary_df.reset_index()

    @staticmethod
    def get_top_coord_urls(crowtangle_shares_df, shares_graph):
        highly_connected_coordinated_entities_df = pd.DataFrame.from_dict(dict(shares_graph.nodes(data=True)), orient='index').reset_index().rename({'index':'name'}, axis = 'columns')

        crowtangle_shares_gb = crowtangle_shares_df.groupby('expanded')

        urls_df = crowtangle_shares_gb[['statistics_actual_likeCount','statistics_actual_shareCount','statistics_actual_commentCount','statistics_actual_loveCount','statistics_actual_wowCount','statistics_actual_hahaCount','statistics_actual_sadCount','statistics_actual_angryCount']].apply(lambda x: x.sum())
        urls_df = pd.merge(urls_df, urls_df.sum(axis=1).to_frame('engagement'), left_index=True, right_index=True)

        crowtangle_shares_filtered_df = crowtangle_shares_df[crowtangle_shares_df['is_coordinated'] & crowtangle_shares_df.set_index('account_url').index.isin(highly_connected_coordinated_entities_df.set_index('name').index)]

        urls_df = urls_df[urls_df.index.isin(crowtangle_shares_filtered_df.set_index('expanded').index)]

        count_df = crowtangle_shares_df.groupby('expanded')['expanded'].count().to_frame('count')

        urls_df = pd.merge(urls_df, count_df, left_index=True, right_index=True)
        urls_df = urls_df.where(urls_df['count']>0)
        urls_df = pd.merge(urls_df, crowtangle_shares_df.groupby('expanded')['account_url'].apply(lambda x: np.unique(list(x))).to_frame('account_url'), left_index=True, right_index=True)
        urls_df = pd.merge(urls_df, crowtangle_shares_filtered_df.groupby('expanded')['account_url'].apply(lambda x: np.unique(list(x))).to_frame('coor_account_url'), left_index=True, right_index=True)
        urls_df = pd.merge(urls_df, crowtangle_shares_df.groupby('expanded')['account_name'].apply(lambda x: np.unique(list(x))).to_frame('account_name'), left_index=True, right_index=True)
        urls_df = pd.merge(urls_df, crowtangle_shares_filtered_df.groupby('expanded')['account_name'].apply(lambda x: np.unique(list(x))).to_frame('coor_account_name'), left_index=True, right_index=True)

        highly_connected_filtered_df = highly_connected_coordinated_entities_df[highly_connected_coordinated_entities_df['name'].isin(urls_df['coor_account_url'].explode('coor_account_url'))]

        merge_df = pd.merge(urls_df[['coor_account_url']].explode('coor_account_url').reset_index(), highly_connected_filtered_df.groupby('name')['component'].apply(lambda x: np.unique(list(x))).to_frame('component').reset_index(), left_on='coor_account_url', right_on='name').drop(columns=['name','coor_account_url'])
        merge_df = merge_df.groupby('expanded').agg(list)
        merge_df['component'] = merge_df['component'].apply(lambda x: np.unique(x))
        merge_df.rename(columns={'component':'components'}, inplace=True)

        urls_df = pd.merge(urls_df, merge_df, left_index=True, right_index=True)

        return urls_df.reset_index()


