"""
A library for generating arbitrary words with Markov chains
"""

import random

class WeightedRandom:
    def setContents(self, items):
        if not items:
            raise ValueError('Items cannot be empty')
        total_weight = sum([ value for key, value in items.items() ])
        self.weights = {}
        for item, weight in items.items():
            self.weights[item] = weight / total_weight

    def randomItem(self):
        target = random.random()
        lower = higher = 0

        for item, weight in self.weights.items():
            higher += weight
            if target >= lower and target <= higher:
                return item
            lower += weight

        raise RuntimeError(f'Unable to find weight that matches {target}')

    @property
    def count(self):
        return len(self.weights)

class WeightedMarkovChain:
    def __init__(self, corpus, ngram_order):
        self.order = ngram_order
        ngrams = self.generateNgrams(corpus)
        self.ngrams = {}
        for ngram in list(ngrams):
            if ngram in self.ngrams:
                self.ngrams[ngram] += 1
            else:
                self.ngrams[ngram] = 1

        self.wrandom = WeightedRandom()
        self.wrandom.setContents(self.ngrams)

    def generateNgrams(self, words):
        ngrams = []
        for word in words:
            for i in range(len(word) - (self.order - 1)):
                ngrams.append(word[i:i+self.order])

        return ngrams

    def randomNgram(self):
        return self.wrandom.randomItem()

    def randomStarterNgram(self):
        starters = [ ngram for ngram, weight in self.ngrams.items() if ngram[:1].isupper() ]
        return random.choice(starters)

    def generate(self, length):
        result = self.randomStarterNgram()
        last_ngram = result

        while len(result) < length:
            next_starts_with = last_ngram[1:self.order]
            next_ngrams = { ngram: count for ngram, count in self.ngrams.items() \
                            if ngram[:self.order-1] == next_starts_with }
            if not next_ngrams:
                break

            self.wrandom.setContents(next_ngrams)
            next_ngram = self.wrandom.randomItem()
            result += next_ngram[-1]
            last_ngram = next_ngram

        return result

    def generateRandom(self, length=20):
        return self.generate(random.randint(self.order, length))

""" PUBLIC API """

# TODO: Speed up chain initialization, if possible
def create_chain(corpus, order=3):
    return WeightedMarkovChain(corpus, order)
