# Milestone Report
John Yang, 3/30/2022, [Link](https://github.com/john-b-yang/cos513) to project repository

### 1 Project Pivot

Upon writing my abstract, I took the following two weeks to study and write out different RL algorithms. I found that given the compute resources I had at this time (i.e. personal laptop, limited GPU runtime on Google Colab, Princeton compute resources which are usually heavily utilized), training policies on games with even just a small set of controls took a while to converge (both because of sub-optimal implementations and limited compute). In addition, writing the game gym environment to train an RL agent from scratch took quite some time. As a result, I decided that within the allocated amount of time, I would likely not be able to complete my original project.

### 2 Project Idea

*The Case for Learned Index Structures* paper by Tim Kraska and his team at Google Brain puts forth an idea regarding the potential for "learned index structures". The authors initially observe that traditional data structures tend to be designed upon heuristics that optimize for more common "best case" patterns when it comes to data access and manipulation. The paper's forefront suggestion is to use models that can learn a dataset's underlying distribution and use such a signal to effectively predict positions or existence of instances in the dataset. In other words, indexes are essentially models, and using learned indices founded upon powerful machine learning models could potentially yield large gains in performance and accuracy. The paper puts this approach into action for three different domains - key-value mapping in sorted array (B+ Trees), key-value mapping in unsorted array (Hashmap), and key existence (Bloom Filter).

This paper has been a book opener, kicking off a domain of research that is reinventing indexing problems at different scales with a variety of probabilistic ML models. This direction is an area that I have wanted to explore for some time. Therefore, for my new project, I have chosen to implement the chain of research that has been improving the accuracy and efficiency of Bloom Filters, a data structure that determines whether or not a key exists. To this end, I've curated several papers and since then, I have successfully implemented three of the five bloom filter variations described throughout these papers. Chronologically, the papers I've read and used as the reference for my code are as follows:
* The Case for Learned Index Structures by Kraska | [link](https://arxiv.org/abs/1712.01208)
* Adaptive Learned Bloom Filter (Ada-BF) by Dai | [link](https://openreview.net/pdf?id=rJlNKCNtPB)
* A Model for Learned Bloom Filters, and Optimizing by Sandwiching by Mitzenmacher | [link](https://arxiv.org/abs/1901.00902)

In no particular order, the models described in the papers, which I plan to implement and benchmark for this project, are naive bloom filter, learned bloom filter, adaptive bloom filter, disjoint adaptive bloom filter, and sandwiched learned bloom filter.

The outcome of this project is to demonstrate how the learned design choices for these bloom filters both reduce the amount of memory used while boosting the test accuracy on the task of determining data existence. Ultimately, I'd like the report to be a benchmark study comparing the impact of different parameters (i.e. size, # of hashing functions) on the false positive rate of each bloom filter.

### 3 Current Progress

As of the submission of this proposal, I have completed the implementations for the naive bloom filter, learned bloom filter, and adaptive bloom filter. In this section, I will first briefly discuss each of the bloom filters I've implemented so far. Then, I'll present an overview of how I've organized the codebase to store the implementations and data. Finally, I will include a table and chart demonstrating the results of some preliminary evaluations on each model.

#### 3.1 Complete BF Implementations

In this section, I briefly describe each bloom filter and leave some details about the implementation process. Every bloom filter has two arguments, `--size_of_BF` for the size of the bloom filter and `--data_path` which takes in the file path to the dataset for evaluating the bloom filter.

**Naive Bloom Filter**

The naive bloom filter implementation is necessary to establish a benchmark for quantifying the relative memory and accuracy performance of the learned models. Bloom filters are a probabilistic data structure for determining existence within a set. To *add* an element, the element is fed through a set of `k` hash functions, which maps the data to a set of indices within an `m`-length array. The array is initially set to zeros; upon each insert, each position the hash function maps to is changed to 1. To *query* an element, the input is run through the hash functions again; if any of the indices correspond to a 0, the element definitively does not exist in the set. If all are 1, either the element is in the set, or it is a false positive. The `naive.py` code strictly abides by this logic.

**Learned Bloom Filter**

The learned bloom filter introduces a binary classifier that attempts to determine existence based on the URL's position with respect to the data distribution that is being stored. If the LBF's confidence in its prediction is above a certain threshold, the result is used. Otherwise, the LBF falls back on a vanilla bloom filter. The implementation determines an appropriate threshold and ingests data that falls under the target threshold with an instance of the `naive.py` bloom filter class.

**Adaptive Bloom Filter**

This implementation builds upon the work of learned bloom filters. With the LBF, we split the approach to determining existing into two groups - one that is determined via classifier and another that is determined via `k` hash functions. With adaptive bloom filters, instead of just 2 groups, we split the data into `n` number of groups, where
* The number of keys in each group is the same (determined by `c` ratio)
* The thresholds bounding each group is adjusted so that the `c` ratio is upheld.
* The number of hash functions used to determine existence for the members of each group is determined during training

The purpose of segmenting the dataset into more than one group is to introduce greater granularity and flexibility when it comes to mimicking the distribution of the dataset. This approach takes longer to train, but yields drastic improvements over the original learned bloom filter approach. In the implementation, a nested search across the number of groups `n` and the ratio of keys in each group `c` is performed, with the threshold and corresponding bloom filter's number of hash functions determined in the process.

#### 3.2 Codebase Overview

The code for this project, under the `src` directory, contains two folders. The `bloom_filter` folder contains the implementations for each of the learned bloom filters, where each file contains a self-contained implementation (i.e. `adaptive`, `learned`, `naive`). The `data` folder contains a single dataset, which is the `URL_data.csv` dataset, which is used for evaluation. This dataset has three columns: `URL`, `label`, and `score`. The `URL` column is the raw URL string, while the `label` of `1` or `-1` indicates whether or not that URL should be inserted into the bloom filter. Finally, the `score` column corresponds to the confidence generated by a classifier when determining existence. The values in the `score` column are not numbers I've generated; these numbers came with the original dataset. As a result, in my current implementation, I have not implemented the binary classifier for determining existence. Instead, for the portions of the training implementation that require the scores, I use the associated `score` column value for now.

#### 3.3 Preliminary Evaluation

In my preliminary evaluations, I have been able to successfully generate and compare the false positive rate for the three bloom filters across different sizes, using the `URL` dataset as the benchmark for evaluation. The github repository for my project contains extra details on the commands I used to run each filter.

||100K|150K|200K|250K|300K|350K|400K|450K|
|-|-|-|-|-|-|-|-|-|
|Naive|0.4868|0.3573|0.2353|0.1696|0.1147|0.0821|0.0558|0.0399|0.0274|
|Learned|0.1195|0.0539|0.0332|0.0224|0.0157|0.0114|0.0083|0.0058|0.0045|
|Adapative|0.0712|0.0316|0.0176|0.0106|0.0069|0.0044|0.0030|0.0020|0.0014|

Generally, as one can see, as the size of the bloom filter increases, the FPR drops; the learned indices perform much better than the naive filter.

### 4 Next Steps

For the remainder of the semester, I have three sets of tasks I hope to complete in time for the final project report.

First, I would like to complete the implementations for the disjoint adaptive bloom filter and the sandwiched learned bloom filter. I believe this will take me about two weeks. The prior experience with implementing the other three filters will hopefully allow me to execute this step without too much trouble.

Second, I would like to run a more thorough set of evaluation tests to draw conclusions regarding how the parameters for each of the different bloom filters affect the false positive rate performance, and how each bloom filter might be better for different kinds of workloads. Beyond a description of what I did, I believe the findings here will constitute large portions of my final report.

Finally, if time allows, I would like to implement more learned structures for the purpose of indexing and existence beyond the scope of bloom filters. I think it'd be interesting to see the signals given by a dataset (i.e. its distribution, nature of the values) that different models pick up on and learn. This would ideally result in work similar to the [Benchmarking Learned Indices](https://vldb.org/pvldb/vol14/p1-marcus.pdf) paper that compares three different learned index structures with a variety of different analysis techniques (i.e. Pareto analysis, Exploratory analysis).