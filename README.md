# PyCooRnet
Using Python Given a set of URLs, this packages detects coordinated link sharing behavior on social media and outputs the network of entities that performed such behaviour.

pip: [https://pypi.org/project/pycoornet/](https://pypi.org/project/pycoornet/)

Project: https://upb-ss1.github.io/

based on https://github.com/fabiogiglietto/CooRnet

## Overview
Given a set of URLs, this package detects coordinated link sharing behavior (CLSB) and outputs the network of entities that performed such behavior.

### What do we mean by coordinated link sharing behavior?
CLSB refers to a specific coordinated activity performed by a network of Facebook pages, groups and verified public profiles (Facebook public entities) that repeatedly shared the same news articles in a very short time from each other.

To identify such networks, we designed, implemented and tested an algorithm that detects sets of Facebook public entities which performed CLSB by (1) estimating a time threshold that identifies URLs shares performed by multiple distinguished entities within an unusually short period of time (as compared to the entire dataset), and (2) grouping the entities that repeatedly shared the same news story within this coordination interval. The rationale is that, while it may be common that several entities share the same URLs, it is unlikely, unless a consistent coordination exists, that this occurs within the time threshold and repeatedly.

## Installation

[https://pypi.org/project/pycoornet/](https://pypi.org/project/pycoornet/)

```sh
pip install pycoornet
```
## Jupyter Notebook Example

[pycoonet_example.ipynb](samples/pycoornet_example.ipynb)

## Usage example
```python
from pycoornet.crowdtangle import CrowdTangle
from pycoornet.shared import Shared
from pycoornet.statistics import Statistics
import networkx as nx
import numpy as np
import pandas as pd
import logging


def main():
    links_df = pd.read_csv('samples/sample_source_links.csv')
    # Init CrowdTangle with api key
    crowd_tangle = CrowdTangle("abc123def345")
    ct_df = crowd_tangle.get_shares(urls=links_df, url_column='clean_url',
                                    date_column='date',clean_urls=True,
                                    platforms='facebook', max_calls = 2)

    shared = Shared(ct_df)
    crowtangle_shares_df, shares_graph, q, coordination_interval = shared.coord_shares(clean_urls=True)

    print(f"Coordination Time = {coordination_interval}")

    #Build Gephi File
    for node in shares_graph.nodes(data=True):
        node[1]['label']=node[1]['account_name']
    nx.write_gexf(shares_graph, "samples/out/shares.gexf")

    componet_summary_df = Statistics.component_summary(crowtangle_shares_df, shares_graph)
    top_urls_df = Statistics.get_top_coord_urls(crowtangle_shares_df, shares_graph)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="pycoornet.log")
    main()
```


## running tests
```sh
py.test --crowdtoken=<your crowdtangle api token>
```
For Example
```sh
py.test --crowdtoken=akZbRIg2DNKhFogkN6rFurv
```

## Acknowledgements
CooRnet has been developed as part of the project [Social Media Behaviour](https://upb-ss1.github.io/) research project activities.

The project is supported by a the Social Media and Democracy Research Grants from Social Science Research Council (SSRC). Data and tools provided by Facebook.
