import math


class Rule:

    DAMPENING_CONSTANT = 1.00009210765
    MODIFYING_CONSTANT = 2.73

    def __init__(self, left, right):
        assert left or right
        self.left = left
        self.right = right
        self.alpha = 1
        self.beta = 1

    def __repr__(self):
        return "Rule('{0}', '{1}')".format(self.left, self.right)

    def evaluate(self, string):
        values = set()
        while True:
            left_start = string.find(self.left)
            if left_start == -1:
                return values
            left_end = left_start + len(self.left)
            right_start = string.find(self.right, left_end)
            if right_start == -1:
                return values
            right_end = right_start + len(self.right)
            values.add(string[left_end:right_start])
            string = string[right_end:]
        return values

    def train(self, string, expected):
        if self.evaluate(string):
            self.beta += 1
        if expected in self.evaluate(string):
            self.alpha += 1

    @property
    def magnitude(self):
        return len(self.left) + len(self.right)

    @property
    def weight(self):
        accuracy = self.alpha / self.beta
        modifier = math.log(self.magnitude, self.MODIFYING_CONSTANT)
        dampening = 1 - pow(self.DAMPENING_CONSTANT, -self.beta)
        return dampening * modifier * accuracy


def analyze(string, substring, a=1, b=20):
    if substring not in string:
        return []
    start = string.find(substring)
    end = start + len(substring)
    rules = []
    for i in range(a, b):
        for j in range(a, b):
            left = string[start - i:start]
            right = string[end:end + j]
            rules.append(Rule(left, right))
    return rules + analyze(string[end:], substring, a, b)