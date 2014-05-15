import random
import bisect
import collections

class ProbabilityDistribution(object):
    def __init__(self, iterable):
        self.items = []
        self.cumsums = []
        cumsum = 0
        for weight, item in iterable:
            cumsum += weight
            self.cumsums.append(cumsum)
            self.items.append(item)
        self.total = cumsum
    
    def random_choice(self):
        r = random.random() * self.total
        idx = bisect.bisect(self.cumsums, r)
        return self.items[idx]

