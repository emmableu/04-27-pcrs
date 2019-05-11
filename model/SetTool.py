import itertools


def getSubSets(s, n):
    return list(itertools.combinations(s, n))

