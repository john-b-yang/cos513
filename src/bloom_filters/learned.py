import argparse
import numpy as np
import pandas as pd
from naive import BloomFilter

# Argparse Definitions
parser = argparse.ArgumentParser()
parser.add_argument('--data_path', action='store', dest="data_path", type=str, required=True, help="path of the dataset")
parser.add_argument('--size_of_BF', action='store', dest="size", type=int, required=True, help="size of the bloom filter")
parser.add_argument('--thres_max', action='store', dest="thres_max", type=float, required=True, help="Maximum threshold for positive samples")
parser.add_argument('--thres_min', action='store', dest="thres_min", type=float, required=True, help="Minimum threshold for positive samples")

class LearnedFilter:
  # Create Learned Bloom Filter
  def __init__(self, min_t, max_t, hash_len, neg_data, pos_data):
    # False positive benchmark, initialize to # of rows
    fps_opt = neg_data.shape[0]

    # Iterate through thresholds, find best one
    for threshold in np.arange(min_t, max_t+0.001, 0.01):
      # Get the urls, number of the positive samples
      query = pos_data.loc[(pos_data['score'] <= threshold), 'url']
      n = len(query)

      # Create Bloom Filter
      bloom_filter = BloomFilter(n, hash_len)
      bloom_filter.insert(query)

      # Evaluate Bloom Filter
      neg_above_t = neg_data.loc[(neg_data['score'] > threshold), 'url']
      neg_below_t = neg_data.loc[(neg_data['score'] <= threshold), 'url']

      fp_test = bloom_filter.test(neg_below_t)
      fps = sum(fp_test) + len(neg_above_t)

      # Save the best performing model
      if (fps_opt > fps):
        fps_opt = fps
        thres_opt = threshold
        bloom_filter_opt = bloom_filter

    # Set values
    self.thres_opt = thres_opt
    self.bloom_filter_opt = bloom_filter_opt

if __name__ == '__main__':
  results = parser.parse_args()
  DATA_PATH, size, thres_max, thres_min = results.data_path, results.size, results.thres_max, results.thres_min

  data = pd.read_csv(DATA_PATH)

  # Grab negative, positive samples from dataset
  negative_samples = data.loc[(data['label'] == -1)]
  positive_samples = data.loc[(data['label'] == 1)]

  # Get negative training data sample to test different thresholds
  train_negative = negative_samples.sample(frac=0.3)

  learned_filter = LearnedFilter(thres_min, thres_max, size, train_negative, positive_samples)
  bloom_filter, threshold = learned_filter.bloom_filter_opt, learned_filter.thres_opt

  # Evaluation
  neg_above_t = negative_samples.loc[(negative_samples['score'] > threshold), 'url']
  neg_below_t = negative_samples.loc[(negative_samples['score'] <= threshold), 'url']

  fp_test = bloom_filter.test(neg_below_t)
  fps = sum(fp_test) + len(neg_above_t)
  fpr = fps*100./len(negative_samples)

  print('Bloom Filter w/ Size', size)
  print('False positive items', fps)
  print('False positive rate: ', fpr)
  print('----------')

