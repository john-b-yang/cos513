import argparse
import numpy as np
import pandas as pd
from naive import hashfunc

DEBUG = True

# Argparse Definitions
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', action='store', dest="data_path", type=str, required=True, help="path of the dataset")
parser.add_argument('--size_of_BF', action='store', dest="hash_len", type=int, required=True, help="size of the bloom filter")
parser.add_argument('--c_min', action="store", dest="c_min", type=float, required=True, help="minimum ratio of the keys")
parser.add_argument('--c_max', action="store", dest="c_max", type=float, required=True, help="maximum ratio of the keys")
parser.add_argument('--group_min', action="store", dest="group_min", type=int, required=True, help="minimum number of groups")
parser.add_argument('--group_max', action="store", dest="group_max", type=int, required=True, help="maximum number of groups")

class AdaptiveFilter():
  def __init__(self, n: int, hash_len: int, k: int):
    self.n, self.hash_len = n, hash_len
    self.h = []
    for _ in range(k):
      self.h.append(hashfunc(self.hash_len))
    self.table = np.zeros(self.hash_len, dtype=int)
  
  def insert(self, key, k):
    for i in range(int(k)):
      t = self.h[i](key)
      self.table[t] = 1
  
  def test(self, key, k):
    test_result, match = 0, 0
    for j in range(int(k)):
      t = self.h[j](key)
      match += 1*(self.table[t] == 1)
    if match == k:
      test_result = 1
    return test_result

def search_best_filter(c_min, c_max, group_min, group_max, hash_len, train_negative, positive_samples):
  k_min, c_opt = 0, 0
  FP_opt = train_negative.shape[0]

  # Iterate across number of groups (to split the dataset into, i.e. number of bloom filters)
  for k_max in range(group_min, group_max+1):
    # Iterate across the possible thresholds
    for c in np.arange(c_min, c_max+10**(-3), 0.1):
      tau = sum(c ** np.arange(0, k_max - k_min + 1, 1))

      # Create bloom filter for this bucket
      n = positive_samples.shape[0]
      bloom_filter = AdaptiveFilter(n, hash_len, k_max)
      
      # Determine thresholds based on number of groups being used
      thresholds = np.zeros(k_max - k_min + 1)
      thresholds[-1] = 1.1

      # Determine amount of training data that falls in the bucket
      num_negative = sum(train_negative['score'] <= thresholds[-1])
      num_piece = int(num_negative / tau) + 1

      # Get list of scores
      score = train_negative.loc[(train_negative['score'] <= thresholds[-1]), 'score']
      score = np.sort(score)

      # Iterate across number of groups, adjust thresholds based on proximity of scores
      for k in range(k_min, k_max):
        i = k - k_min
        score_1 = score[score < thresholds[-(i+ 1)]]
        if int(num_piece * c ** i) < len(score_1):
          thresholds[-(i+2)] = score_1[-int(num_piece * c ** i)]
      
      url, score = positive_samples['url'], positive_samples['score']

      for score_s, url_s in zip(score, url):
        ix = min(np.where(score_s < thresholds)[0])
        k = k_max - ix
        bloom_filter.insert(url_s, k)
      
      # Test the configured bloom filter
      ML_positive = train_negative.loc[(train_negative['score'] >= thresholds[-2]), 'url']
      temp = (train_negative['score'] < thresholds[-2])
      url_negative, score_negative = train_negative.loc[(temp, 'url')], train_negative.loc[(temp, 'score')]
      
      test_result = np.zeros(len(url_negative))
      ss = 0
      for score_s, url_s in zip(score_negative, url_negative):
        ix = min(np.where(score_s < thresholds)[0])
        k = k_max - ix
        test_result[ss] = bloom_filter.test(url_s, k)
        ss += 1
      
      # Calculate # of FP items, FP rate. Keep if best performing bloom filter
      FP_items = sum(test_result) + len(ML_positive)

      if FP_opt > FP_items:
        FP_opt = FP_items
        bloom_filter_opt = bloom_filter
        thresholds_opt = thresholds
        k_max_opt = k_max
        c_opt = c
  
  if DEBUG:
    print('Optimal FPs: %f, Optimal c: %f, Optimal num_group: %d' % (FP_opt, c_opt, k_max_opt))

  return bloom_filter_opt, thresholds_opt, k_max_opt

if __name__ == '__main__':
  results = parser.parse_args()
  DATA_PATH, hash_len = results.data_path, results.hash_len
  c_min, c_max, group_min, group_max = results.c_min, results.c_max, results.group_min, results.group_max

  data = pd.read_csv(DATA_PATH)

  # Grab negative, positive samples from dataset
  negative_samples = data.loc[(data['label'] == -1)]
  positive_samples = data.loc[(data['label'] == 1)]

  # Get negative training data sample to test different thresholds
  train_negative = negative_samples.sample(frac=0.3)

  # Search for optimal bloom filter
  print("Ada-BF w/ Size ", hash_len)
  bloom_filter, thresholds, k_max = search_best_filter(c_min, c_max, group_min, group_max, hash_len, train_negative, positive_samples)

  # Test Queries
  ML_positive = negative_samples.loc[(negative_samples['score'] >= thresholds[-2]), 'url']
  query_negative = negative_samples.loc[(negative_samples['score'] < thresholds[-2]), 'url']
  score_negative = negative_samples.loc[(negative_samples['score'] < thresholds[-2]), 'score']

  # Evaluate on test dataset
  test_result = np.zeros(len(query_negative))
  ss = 0

  for score_s, query_s in zip(score_negative, query_negative):
    ix = min(np.where(score_s < thresholds)[0])
    k = k_max - ix
    test_result[ss] = bloom_filter.test(query_s, k)
    ss += 1
  
  FP_items = sum(test_result) + len(ML_positive)
  FPR = FP_items * 100 / negative_samples.shape[0]

  print("False positive items: {}; FPR: {}; Size of queries: {}".format(FP_items, FPR, negative_samples.shape[0]))
  print('----------')