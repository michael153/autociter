import math
import time

import numpy


class Candidate:

    def __init__(self, string):
        self.string = string
        self.rules = set()

    @property
    def score(self):
        average_weight = numpy.average([rule.weight for rule in self.rules])
        return 1 - pow(2, -math.log(len(self.rules)) * average_weight)

    def add(self, rule):
        self.rules.add(rule)

    def __eq__(self, other):
        if not isinstance(other, Candidate):
            return False
        return self.string == other.string

    def __hash__(self):
        return hash(self.string)

    def __repr__(self):
        return self.string


def execute(string, rules):
    values = {}
    start = time.time()
    for rule in rules:
        value = rule.evaluate(string)
        values[rule] = value
    candidates = set()
    for rule in values:
        for string in values[rule]:
            candidates.add(Candidate(string))
    for candidate in candidates:
        for rule in rules:
            if candidate.string in values[rule]:
                candidate.add(rule)
    best_candidate = max(candidates, key=lambda candidate: candidate.score)
    end = time.time()

    print("Applied", len(rules), "rules in", end-start, "seconds.\n")
    print(best_candidate)
    print("---")
    candidates = sorted(candidates, key=lambda candidate: -candidate.score)
    for candidate in candidates[:100]:
	       print(candidate.score, candidate.string[:150].replace("\n", ""), sep="\t")

    return best_candidate.string