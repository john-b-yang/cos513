import argparse
import numpy as np
import os
import pandas as pd
from naive import BloomFilter

OPTIMAL_K_FACTOR = np.log(0.618)

# Argparse Definitions
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', action='store', dest="data_path", type=str, required=True, help="path of the dataset")
parser.add_argument('--size_of_BF', action='store', dest="hash_len", type=int, required=True, help="size of the bloom filter")
parser.add_argument('--c_min', action="store", dest="c_min", type=float, required=True, help="minimum ratio of the keys")
parser.add_argument('--c_max', action="store", dest="c_max", type=float, required=True, help="maximum ratio of the keys")
parser.add_argument('--group_min', action="store", dest="group_min", type=int, required=True, help="minimum number of groups")
parser.add_argument('--group_max', action="store", dest="group_max", type=int, required=True, help="maximum number of groups")
parser.add_argument('--model_path', action='store', dest='model_path', type=str, required=True, help="")

def R_size(count_key, count_nonkey, R0):
  R = [0]*len(count_key)
  R[0] = max(R0, 1)
  for k in range(1, len(count_key)):
    R[k] = max(int(count_key[k] * (np.log(count_nonkey[0] / count_nonkey[k])/OPTIMAL_K_FACTOR + R[0]/count_key[0])), 1)
  return R

def search_best_filter(c_min, c_max, group_min, group_max, hash_len, train_negative, positive_samples):
  FP_opt = train_negative.shape[0]
  c_opt, g_opt = 0, 0

  # Iterate across all combination of groups, ratios
  for g in range(group_min, group_max+1):
    for c in np.arange(c_min, c_max+(10**(-3)), 0.1):
      # Determine thresholds
      thresholds = np.zeros(g + 1)
      thresholds[0], thresholds[-1] = -0.1, 1.1
      num_negative = train_negative.shape[0]

      tau = sum(c ** np.arange(0, g, 1))
      num_piece = int(num_negative / tau)
      score = np.sort(np.array(list(train_negative['score'])))

      for i in range(1, g):
        if thresholds[-i] > 0:
          score_1 = score[score< thresholds[-i]]
          if int(num_piece * c ** (i-1)) <= len(score_1):
            thresholds[-(i+1)] = score_1[-int(num_piece * c ** (i-1))]
          else:
            thresholds[-(i+1)] = 0
        else:
          thresholds[-(i+1)] = 1
      
      count_nonkey = np.zeros(g)
      for j in range(g):
        count_nonkey[j] = sum((score >= thresholds[j]) & (score < thresholds[j+1]))
      
      num_group_1 = sum(count_nonkey > 0)
      count_nonkey = count_nonkey[count_nonkey > 0]
      thresholds = thresholds[-(num_group_1 + 1):]

      # Count keys in each group
      query, score = positive_samples['url'], positive_samples['score']

      count_key = np.zeros(num_group_1)
      query_group = []
      for j in range(num_group_1):
        count_key[j] = sum((score >= thresholds[j]) & (score < thresholds[j + 1]))
        query_group.append(query[(score >= thresholds[j]) & (score < thresholds[j+1])])
      
      # Search bloom filters' size
      R = np.zeros(num_group_1 - 1)
      R[:] = 0.5 * hash_len
      non_empty_ix = min(np.where(count_key > 0)[0])
      if non_empty_ix > 0:
        R[0:non_empty_ix] = 0
      kk = 1
      while abs(sum(R) - hash_len) > 200:
        if (sum(R) > hash_len):
          R[non_empty_ix] -= int((0.5 * hash_len) * (0.5) ** kk + 1)
        else:
          R[non_empty_ix] += int((0.5 * hash_len) * (0.5) ** kk + 1)
        R[non_empty_ix:] = R_size(count_key[non_empty_ix:-1], count_nonkey[non_empty_ix:-1], R[non_empty_ix])
        if int((0.5 * R_sum) * (0.5) ** kk + 1) == 1:
          break
        kk += 1
      
      Bloom_Filters = []
      for j in range(int(num_group_1 - 1)):
        if j < non_empty_ix:
          Bloom_Filters.append([0])
        else:
          Bloom_Filters.append(BloomFilter(count_key[j], int(R[j])))
          Bloom_Filters[j].insert(query_group[j])
      
      # Test queries
      ML_positive = train_negative.loc[(train_negative['score'] >= thresholds[-2]), 'url']
      query_negative = train_negative.loc[(train_negative['score'] < thresholds[-2]), 'url']
      score_negative = train_negative.loc[(train_negative['score'] < thresholds[-2]), 'score']

      test_result = np.zeros(len(query_negative))
      ss = 0
      for score_s, query_s in zip(score_negative, query_negative):
        ix = min(np.where(score_s < thresholds)[0]) - 1
        test_result[ss] = Bloom_Filters[ix].test(query_s, single_key=True) if ix >= non_empty_ix else 0
        ss += 1
      FP_items = sum(test_result) + len(ML_positive)
      
      if FP_items < FP_opt:
        FP_opt = FP_items
        Bloom_Filters_opt = Bloom_Filters
        thresholds_opt = thresholds
        non_empty_ix_opt = non_empty_ix
        c_opt = c
        g_opt = g
  
  print('Optimal FPs: %f, Optimal c: %f, Optimal num_group: %d' % (FP_opt, c_opt, g_opt))
  return Bloom_Filters_opt, thresholds_opt, non_empty_ix_opt

if __name__ == '__main__':
  print('Bloom Filter w/ Size', hash_len)
  results = parser.parse_args()
  DATA_PATH, hash_len = results.data_path, results.hash_len
  c_min, c_max, group_min, group_max = results.c_min, results.c_max, results.group_min, results.group_max
  
  # Determine model size, hash length
  model_size = os.path.getsize(results.model_path)
  R_sum = results.hash_len - model_size * 8

  data = pd.read_csv(DATA_PATH)

  # Grab negative, positive samples from dataset
  negative_samples = data.loc[(data['label'] == -1)]
  positive_samples = data.loc[(data['label'] == 1)]

  # Get negative training data sample to test different thresholds
  train_negative = negative_samples.sample(frac=0.3)

  # Search for optimal bloom filter configuration
  Bloom_Filters_opt, thresholds_opt, non_empty_ix_opt = search_best_filter(c_min, c_max, group_min, group_max, R_sum, train_negative, positive_samples)

  ### Test queries
  ML_positive = negative_samples.loc[(negative_samples['score'] >= thresholds_opt[-2]), 'url']
  query_negative = negative_samples.loc[(negative_samples['score'] < thresholds_opt[-2]), 'url']
  score_negative = negative_samples.loc[(negative_samples['score'] < thresholds_opt[-2]), 'score']
  test_result = np.zeros(len(query_negative))
  ss = 0
  for score_s, query_s in zip(score_negative, query_negative):
      ix = min(np.where(score_s < thresholds_opt)[0]) - 1
      if ix >= non_empty_ix_opt:
          test_result[ss] = Bloom_Filters_opt[ix].test(query_s, single_key=True)
      else:
          test_result[ss] = 0
      ss += 1
  FP_items = sum(test_result) + len(ML_positive)
  FPR = FP_items/len(query_negative)
  print('False positive items: {}; FPR: {}; Size of queries: {}'.format(FP_items, FPR, len(query_negative)))
  print('----------')