# Learned Bloom Filters
Final Project for Foundations of Probabilistic Modeling @ Princeton University SP22

This repository contains the code for the final project I submitted for COS 513. For my final project, I decided to reimplement a number of "learned" bloom filters. An inherently probabilistic data structure, bloom filters have been used as the paradigm for a new research direction called "learned index structures". These systems aim to enhance traditional data structures that provide generalized best-case heuristics by introducing approaches that attempt to learn and take advange of the "nature" of data (i.e. its distribution).

Final Presentation [Link](https://docs.google.com/presentation/d/1hXzI-_khcZVhhcPTZGWZ9fLfI-xjUP2q4fV0p7kKUys/edit?usp=sharing)

### Directory Layout

    .
    ├── abstract.md             # Project Abstract
    ├── journal.md              # Record of progress thru-out semester
    ├── doc/                    # Final project, milestone writeups
    ├── etc/                    # Miscellaneous
    ├── src/                    # Code + Test Data
    │   ├── bloom_filters       # BF Implementations
    │   └── data                # URL dataset for benchmark
    └── README.md