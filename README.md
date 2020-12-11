# PyCooRnet
Using Python Given a set of URLs, this packages detects coordinated link sharing behavior on social media and outputs the network of entities that performed such behaviour.

based on https://github.com/fabiogiglietto/CooRnet

## Overview
Given a set of URLs, this package detects coordinated link sharing behavior (CLSB) and outputs the network of entities that performed such behavior.

### What do we mean by coordinated link sharing behavior?
CLSB refers to a specific coordinated activity performed by a network of Facebook pages, groups and verified public profiles (Facebook public entities) that repeatedly shared the same news articles in a very short time from each other.

To identify such networks, we designed, implemented and tested an algorithm that detects sets of Facebook public entities which performed CLSB by (1) estimating a time threshold that identifies URLs shares performed by multiple distinguished entities within an unusually short period of time (as compared to the entire dataset), and (2) grouping the entities that repeatedly shared the same news story within this coordination interval. The rationale is that, while it may be common that several entities share the same URLs, it is unlikely, unless a consistent coordination exists, that this occurs within the time threshold and repeatedly.


## Workflow
https://www.atlassian.com/es/git/tutorials/comparing-workflows/gitflow-workflow


## CD/CI Github actions
https://github.com/features/actions

## IDE
VSCODE

## StyleGuide
http://google.github.io/styleguide/pyguide.html


## running tests
```sh
py.test --crowdtoken=<your crowdtangle api token> --urlsfilepath=<path of the urls file> --crowdresultfile=<path of the crowdtangle file>
```
For Example
```sh
py.test --crowdtoken=akZbRIg2DNKhFogkN6rFurv --urlsfile=samples/sample.csv --crowdresultfile=samples/ct_shares_full.json
