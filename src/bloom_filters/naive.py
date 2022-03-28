import argparse
import string
import numpy as np
import pandas as pd
import serialize

# Hashing function
from random import randint
from sklearn.utils import murmurhash3_32

# Argparse Definitions
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', action='store', dest="data_path", type=str, required=True, help="path of the dataset")
parser.add_argument('--size_of_BF', action='store', dest="hash_len", type=int, required=True, help="size of the bloom filter")

# Hash function generator
def hashfunc(m: int):
  ss = randint(1, 99999999)
  # Hash function, generates value fitting into one of m buckets
  def hash_m(x):
    return murmurhash3_32(x, seed=ss)%m
  return hash_m

# Normal Bloom Filter Implementation
class BloomFilter():
  # Create Bloom Filter
  def __init__(self, n: int, hash_len: int):
    # Error handling
    if (hash_len == 0):
      raise SyntaxError('The hash table cannot be empty')

    # Initialize inputs
    self.n, self.hash_len = n, hash_len

    # Set number of hash functions
    if (self.n > 0) and (self.hash_len > 0):
      self.k = max(1, int(self.hash_len/n*0.6931472))
    elif (self.n == 0):
      self.k = 1

    # Create k hash functions
    self.h = []
    for _ in range(self.k):
      self.h.append(hashfunc(self.hash_len))
    
    # Create table to store data
    self.table = np.zeros(self.hash_len, dtype=int)
  
  # Insert data into bloom filter
  def insert(self, key: string):
    for i in key:
      for j in range(self.k):
        t = self.h[j](i)
        self.table[t] = 1
  
  # Check if key(s) exist
  def test(self, keys):
    # Create results list, counter
    results, i = np.zeros(len(keys)), 0

    # Iterate through all keys
    for key in keys:
      num_matches = 0
      # Iterate thru hash func's, determine number of matches per key
      for j in range(self.k):
        t = self.h[j](key)
        num_matches += ((self.table[t] == 1) * 1)
      # If more matches than threshold, then in dataset
      if num_matches == self.k:
        results[i] = 1
      i += 1
    return results

if __name__ == '__main__':
  results = parser.parse_args()
  DATA_PATH, hash_len = results.data_path, results.hash_len

  data = pd.read_csv(DATA_PATH)

  # Grab negative, positive samples from dataset
  negative_samples = data.loc[(data['label'] == -1)]
  positive_samples = data.loc[(data['label'] == 1)]

  # Get the urls, number of the positive samples
  query = positive_samples['url']
  n = len(query)

  # Insert positive URLs into the bloom filter
  bloom_filter = BloomFilter(n, hash_len)
  bloom_filter.insert(query)

  # Get urls of negative samples, test Bloom filter for existence
  query_negative = negative_samples['url']
  fp_test = bloom_filter.test(query_negative)
  print('Total false positive items:', sum(fp_test))
  print('False positive rate:', (sum(fp_test)*100./len(fp_test)))