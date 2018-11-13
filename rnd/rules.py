import math
from unidecode import unidecode


def standardize(string):
    return unidecode(string)


class Rule:

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.α = 1
        self.β = 1

    def __repr__(self):
        return "Rule('{0}', '{1}')".format(self.left, self.right)

    def evaluate(self, string):
        values = set()
        while self.left in string and self.right in string:
            left_start = string.find(self.left)
            left_end = left_start + len(self.left)
            right_start = string.find(self.right)
            right_end = right_start + len(self.right)
            values.add(string[left_end:right_start])
            string = string[right_end:]
        return values

    def train(self, string, expected):
        if self.evaluate(string):
            self.β += 1
        if expected in self.evaluate(string):
            self.α += 1

    @property
    def magnitude(self):
        return len(self.left) + len(self.right)

    @property
    def weight(self):
        accuracy = self.α / self.β
        dampening = math.log(self.magnitude)
        return dampening * accuracy
