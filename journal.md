# Journal

**March 17, 2021**
Began on project. Since the abstract, I've pivoted from reinforcement learning to bloom filters. While I'd like to explore RL at some point, the application of such techniques to games feels like a solved problem. I recently read the [OnRL](https://ml-video-seminar.princeton.systems/papers/onRL.pdf) paper, which got me thinking about RL as a tool for creating learned indices and data structures, which I found interesting.

My end goal would be to find some novelty within the intersection of RL and systems functions. Traditional data structures involve incorporating general heuristics into their design at the cost of expensive edge cases; recent supervised and machine learning approaches have demonstrated significant gains due to their ability to learn the dataset distribution and optimize towards it.

As a starting step, I feel that re-implementing the Learned Index Structures [paper](https://arxiv.org/abs/1712.01208) by Google from a couple years ago would be a good place to start. I think a good scope for the project would be to successfully implement the following kinds of bloom filters:
* Learned Bloom Filter
* Adaptive Bloom Filter
* Disjointed Bloom Filter
* Sandwiched Bloom Filter

The upshot would be writing a benchmark study on the successful implementation of all four, along with the naive version, comparing the impact of different parameters (i.e. size, # of hashing functions) on the false positive rate of the resulting models.