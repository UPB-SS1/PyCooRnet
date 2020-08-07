# crowdtangle tests
# test of get_shares function
import os
import pandas as pd


from pycoornet.crowdtangle import CrowdTangle

# linux create enviroment variable
# Example:    export CROWD_TOKEN=ASIU29834792387UYGI

# load enviroment variable
token = os.getenv('CROWD_TOKEN')

#create variable class with crowdtangle api key
get_ct_shares = CrowdTangle(token)

# load test file
test_file = pd.read_csv('samples/sample.csv')

shares = get_ct_shares.get_shares(urls = test_file, url_column='clean_url', date_column='date',
                                platforms='facebook', sleep_time=1)
print(shares)





