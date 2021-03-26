import networkx as nx
import pandas as pd
from urllib.parse import urlparse
import tldextract
import numpy as np

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

        return summary_df

    @staticmethod
    def get_top_coord_urls(crowtangle_shares_df, shares_graph, order_by = "engagement", component=True, top=10):
        highly_connected_coordinated_entities_df = pd.DataFrame.from_dict(dict(shares_graph.nodes(data=True)), orient='index').reset_index().rename({'index':'name'}, axis = 'columns')
    pass


