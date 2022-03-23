# Journal

**March 23, 2021**
Finished learned bloom filter implementation. The code was surprisingly not as complex or efficient as I thought it was going to be. The implementaion is based on *The Case for Learned Index Structures (Kraska 2018)* paper, which reframes the problem that index structures try to solve as a learning problem; specifically, the authors discuss how creating such a data structure is quite similar to learning a cumulative distribution function. Once the nature of the dataset's distribution is known, optimizations can be made accordingly.

The learned bloom filter feels like a pretty naive attempt at this. Based on the confidence of a classifier regarding whether a value exists, if the confidence is high enough, then the classifier's answer is used. Otherwise, the model falls back on a vanilla bloom filter. Since the amount of data that the bloom filter would be used for, it can perform effectively for values that the classifier had a harder time discerning.

Instead of re-implementing, which was my initial approach, I just used the naive bloom filter again, and the `LearnedFilter` class mainly contains the iterative logic that tests for the best threshold in increments of 0.01. Although it works correctly and adheres to the description of the original implementation, it is by no means a very complex or intelligent model. Next up is the adaptive bloom filter, which I believe incorporates more learning and should be quite interesting to tackle.

**March 17, 2021**
Began on project. Since the abstract, I've pivoted from reinforcement learning to bloom filters. While I'd like to explore RL at some point, the application of such techniques to games feels like a solved problem. I recently read the [OnRL](https://ml-video-seminar.princeton.systems/papers/onRL.pdf) paper, which got me thinking about RL as a tool for creating learned indices and data structures, which I found interesting.

My end goal would be to find some novelty within the intersection of RL and systems functions. Traditional data structures involve incorporating general heuristics into their design at the cost of expensive edge cases; recent supervised and machine learning approaches have demonstrated significant gains due to their ability to learn the dataset distribution and optimize towards it.

As a starting step, I feel that re-implementing the Learned Index Structures [paper](https://arxiv.org/abs/1712.01208) by Google from a couple years ago would be a good place to start. I think a good scope for the project would be to successfully implement the following kinds of bloom filters:
* Learned Bloom Filter
* Adaptive Bloom Filter
* Disjointed Bloom Filter
* Sandwiched Bloom Filter

The upshot would be writing a benchmark study on the successful implementation of all four, along with the naive version, comparing the impact of different parameters (i.e. size, # of hashing functions) on the false positive rate of the resulting models.