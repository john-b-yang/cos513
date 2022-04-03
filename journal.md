# Journal

**April 2, 2022**
Finished the disjoint adaptive bloom filter implementation. This approach made a slight adjustment to the original adaptive bloom filter implementation. It keeps pretty much the same logic as before, in terms of separating a distribution into `g` groups, each with its own set of hash functions. However, the key difference is that with the vanilla adaptive bloom filter, the outputs of the hash function are aggregated and saved into the same bloom filter. With the disjoint adaptive bloom filter, the results are saved by independent bloom filters. This should yield a lower false positive rate, as independent buckets, instead of a single aggregated bucket, draw more distinct boundaries between which values are in which groups.

The implementation for this code was fairly straightforward, with the exception that the original single bloom filter was changed to a list of bloom filters in the disjoint implementation. This retooling took me a bit more time than I thought it would, but the drop in FPR rate is quite obvious. Something that I'm a little taken aback by is that it seems from initial trials, that the FPR rate goes up with the size of the bloom filter. I believe this is likely because of an issue with the implementation. I'm not sure if there's a rational explanation for why this is the case.

Aside from setting up the bloom filter, I've also finished writing a Google Colab for running experiments on each of the bloom filters. For each bloom filter, I will be running them on the URL dataset at sizes varying from 1 * 10^6 to 5 * 10^6 slots, in increments of 5 * 10^5. So far, the results seem consistent and promising in that the more complex bloom filter implementations have lower FPRs, which also decrease with size. As a second part to the evaluation, I think it'll be interesting to see how the number of groups and ratio of keys affects the FPR for the adaptive and disjoint adaptive bloom filters.

Before I get there, the next thing I'll do is implement the sandwiched bloom filter, which proposes putting the classifier "in-between" two naive bloom filters. I still don't quite understand how that works, but I hope to figure it out soon enough.

**March 29, 2022**

Finished adaptive bloom filter implementation. This approach is described in the Ada-BF [paper](https://openreview.net/pdf?id=rJlNKCNtPB) published in ICLR 2020. It builds upon the learned bloom filter approach. With LBF, we divided the data `X` into two groups that are evaluated as follows (for an individual data sample):
* If score(x) >= threshold, `x` is purported to exist (0 hash functions used)
* If score(x) < threshold, `x`'s membership is evaluated with the bloom filter (K hash functions used)

The improvement by the adaptive bloom filter is that instead of just these 2 groups, `X` is divided into *g* groups by score, where each group uses a different number of hash functions is used to test membership. The threshold ranges that each group cover do not overlap, and by segmenting the data with finer granularity, this newfound flexibility allows the data structure to fine-tune the FPR across smaller regions, which empirically and formally leads to a lower false positive rate. In this sense, Ada-BF is a generalization of the learned bloom filter, where there are only two groups separated by a single threshold, and the hash functions per group are `K` and 0 respectively. Given the same amount of memory, Ada-BF is able to use the storage space with a much greater degree of granularity, leading to much stronger performance that is also more reflective of real world data.

At this point, I think the next two bloom filters I tackle will be the disjoint adaptive bloom filter along with the sandwiched bloom filter, which I hope to be able to complete within the next week or two. After that, I want to begin to put together the final project report that will be a comparison of these different bloom filters, proving how the design choices each one makes translates into better performance and more efficient storage space. Time permitting, I think it'd be fun to explore more learned index structures (I found a paper on learned KNN indexing that was an interesting adoption of learning techniques to data structures. I'll try to find the paper for that and implement it). This week during lecture, we discussed Bayesian neural networks, and the textbook also discussed how the properties of Bayes' Rules and their re-expression of priors or posterior + likelihoods in learning algorithms can bolster performance. I think it'd be worthwhile to learn how to implement the Bayesian version of a traditional learning algorithm, such as Bayesian Principle Component Analysis.

**March 23, 2022**

Finished learned bloom filter implementation. The code was surprisingly not as complex or efficient as I thought it was going to be. The implementaion is based on *The Case for Learned Index Structures (Kraska 2018)* paper, which reframes the problem that index structures try to solve as a learning problem; specifically, the authors discuss how creating such a data structure is quite similar to learning a cumulative distribution function. Once the nature of the dataset's distribution is known, optimizations can be made accordingly.

The learned bloom filter feels like a pretty naive attempt at this. Based on the confidence of a classifier regarding whether a value exists, if the confidence is high enough, then the classifier's answer is used. Otherwise, the model falls back on a vanilla bloom filter. Since the amount of data that the bloom filter would be used for, it can perform effectively for values that the classifier had a harder time discerning.

Instead of re-implementing, which was my initial approach, I just used the naive bloom filter again, and the `LearnedFilter` class mainly contains the iterative logic that tests for the best threshold in increments of 0.01. Although it works correctly and adheres to the description of the original implementation, it is by no means a very complex or intelligent model. Next up is the adaptive bloom filter, which I believe incorporates more learning and should be quite interesting to tackle.

**March 17, 2022**

Began on project. Since the abstract, I've pivoted from reinforcement learning to bloom filters. While I'd like to explore RL at some point, the application of such techniques to games feels like a solved problem. I recently read the [OnRL](https://ml-video-seminar.princeton.systems/papers/onRL.pdf) paper, which got me thinking about RL as a tool for creating learned indices and data structures, which I found interesting.

My end goal would be to find some novelty within the intersection of RL and systems functions. Traditional data structures involve incorporating general heuristics into their design at the cost of expensive edge cases; recent supervised and machine learning approaches have demonstrated significant gains due to their ability to learn the dataset distribution and optimize towards it.

As a starting step, I feel that re-implementing the Learned Index Structures [paper](https://arxiv.org/abs/1712.01208) by Google from a couple years ago would be a good place to start. I think a good scope for the project would be to successfully implement the following kinds of bloom filters:
* Learned Bloom Filter
* Adaptive Bloom Filter
* Disjointed Bloom Filter
* Sandwiched Bloom Filter

The upshot would be writing a benchmark study on the successful implementation of all four, along with the naive version, comparing the impact of different parameters (i.e. size, # of hashing functions) on the false positive rate of the resulting models.