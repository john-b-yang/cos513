# Bloom Filter Implementations

### Overview
Bloom filters are meant to support insertion and look up of items similar to hash tables, but do so with much less space. They don't directly store the items, but instead

### Naive
> `naive.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to dataset to run bloom filter on.

Implementation for original bloom filter. Generates (number of elements * storage size in number of bits) * 0.693 hash functions, which are used to set the positions within an array corresponding to the hashes to indicate existence. All full, detailed explanation is [here](https://freecontent.manning.com/all-about-bloom-filters/).

**Example Run**
```
python3 naive.py --size_of_BF 100000 --data_path ../data/URL_data.csv
```

### Learned
Proposed in *The Case for Learned Index Structures (Kraska 2018)*
> `learned.py`
> * `--size_of_BF`: Size of bloom filter (number of slots)
> * `--data_path`: Relative path to dataset to run bloom filter on.
> * `--thres_max`: Maximum threshold for positive samples
> * `--thres_man`: Minimum threshold for negative samples

Implementation for learned bloom filter. The implementation accounts for the `score` tied to each prediction on whether the element belongs to the set. If it's greater than some confidence threshold, then we return true. Otherwise, the backup bloom filter is called upon to make the decision. The goal of this approach is that the classifier can handle a large majority of the cases, while the backup bloom filter, which scales in size, doesn't need to be as large and is only concerned with handling more difficult cases. For a dataset, the `learned.py` implementation tests thresholds between the `thres_max` and `thres_min` arguments, then returns the bloom filter with the best performing threshold (tested on sample of training data).

**Example Run**
```
python3 learned.py --size_of_BF 100000 --data_path ../data/URL_data.csv --thres_max 0.95 --thres_min 0.05
```

### Adaptive