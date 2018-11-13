import time


def evaluate(rules, titles, num_rules=200):
    rules = remove_duplicates(rules)
    for rule in rules:
        for source_code in titles:
            rule.train(source_code, titles[source_code])
    rules = sorted(rules, key=lambda rule: -rule.weight)

    print("Evaluated", len(rules), "rules")
    print("---")
    for rule in rules[:num_rules]:
	       print(rule.weight, rule, sep="\t")
    print("")

    return rules[:num_rules]


def remove_duplicates(rules):

    def same(rule1, rule2):
        return rule1.left == rule2.left and rule1.right == rule2.right

    i = 0
    while i < len(rules) - 1:
        to_remove = []
        for j in range(i + 1, len(rules)):
            if same(rules[i], rules[j]):
                to_remove.append(rules[j])
        for rule in to_remove:
            rules.remove(rule)
        i += 1
    return rules
