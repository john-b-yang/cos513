# Bloom Filter Implementations

### Overview
Bloom filters are meant to support insertion and look up of items similar to hash tables, but do so with much less space. They don't directly store the items, but instead

### Naive
> `naive.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to dataset to run bloom filter on

Implementation for original bloom filter. Generates (number of elements * storage size in number of bits) * 0.693 hash functions, which are used to set the positions within an array corresponding to the hashes to indicate existence. All full, detailed explanation is [here](https://freecontent.manning.com/all-about-bloom-filters/).

**Example Run**
```
python3 naive.py --size_of_BF 100000 --data_path ../data/URL_data.csv
```

### Learned
Proposed in *The Case for Learned Index Structures (Kraska 2018)*
> `learned.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to dataset to run bloom filter on
> * `--thres_max`: Maximum threshold for positive samples
> * `--thres_man`: Minimum threshold for negative samples

Implementation for learned bloom filter. The implementation accounts for the `score` tied to each prediction on whether the element belongs to the set. If it's greater than some confidence threshold, then we return true. Otherwise, the backup bloom filter is called upon to make the decision. The goal of this approach is that the classifier can handle a large majority of the cases, while the backup bloom filter, which scales in size, doesn't need to be as large and is only concerned with handling more difficult cases. For a dataset, the `learned.py` implementation tests thresholds between the `thres_max` and `thres_min` arguments, then returns the bloom filter with the best performing threshold (tested on sample of training data).

**Example Run**
```
python3 learned.py --size_of_BF 100000 --data_path ../data/URL_data.csv --thres_max 0.95 --thres_min 0.05
```

### Adaptive
Proposed in *Adaptive Learned Bloom Filter (Ada-BF): Efficient Utilization of the Classifier (Dai 2020)*
> `adaptive.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to data to run bloom filter on
> * `--c_min`: Minimum ratio of the keys
> * `--c_max`: Maximum ratio of the keys
> * `--group_min`: Minimum number of groups
> * `--group_min`: Maximum number of groups

Implementation for adaptive bloom filter. This implementation builds upon the work of learned bloom filters. With the LBF, we split the approach to determining existing into two groups - one that is determined via classifier and another that is determined via `K` hash functions. With adaptive bloom filters, instead of just 2 groups, we split the data into `n` number of groups, where
* The number of keys in each group is the same (determined by `c` ratio)
* The thresholds bounding each group is adjusted so that the `c` ratio is upheld.
* The number of hash functions used to determine existence for the members of each group is determined during training
The purpose of the time is to introduce greater granularity and flexibility when it comes to mimicking the distribution of the dataset. This approach takes longer to train, but yields drastic improvements over the original learned bloom filter approach.

**Example Run**
```
python3 adaptive.py --size_of_BF 100000 --data_path ../data/URL_data.csv --c_min 1.6 --c_max 2.5 --group_min 8 --group_max 12
```

### Disjoint Adaptive
Proposed in *Adaptive Learned Bloom Filter (Ada-BF): Efficient Utilization of the Classifier (Dai 2020)*
> `disjoint.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to data to run bloom filter on
> * `--c_min`: Minimum ratio of the keys
> * `--c_max`: Maximum ratio of the keys
> * `--group_min`: Minimum number of groups
> * `--group_min`: Maximum number of groups
> * `--model_path`: Path to binary classifier for determining existence

Implementation for disjoint adaptive bloom filter. The approach is very similar to the adaptive bloom filter, where we split the data distribution into `g` groups, and each group has a unique number of hash functions. However, instead of aggregating the hashing results into a single bloom filter, the disjoint implementation puts the resultss into separate, variable-sized bloom filters. This design allows for more firm decision boundaries between different groups, which leads to lower false positive rates.

**Example Run**
```
python disjoint.py --data_path ../data/URL_data.csv --size_of_BF 200000 --group_min 8 --group_max 12 --c_min 1.6 --c_max 2.5 --model_path ../models URL_Random_Forest_Model_n_10_leaf_20.pickle
```

### References
* [COS 598D Assignment 4](https://github.com/yushansu/COS598D_Assignment4)
* [Optimal num of hash functions](https://freecontent.manning.com/all-about-bloom-filters/)
* [The Case for Learned Index Structures](https://arxiv.org/abs/1712.01208)
* [Adaptive Learned Bloom Filter](https://openreview.net/pdf?id=rJlNKCNtPB)
* [Optimizing Learned Bloom Filteres by Sandwiching](https://www.arxiv-vanity.com/papers/1803.01474/)