def Diff(li1, li2):
    return (list(set(li1) - set(li2)))

def Intersection(li1, li2):
    set1 = set(li1)
    set2 = set(li2)
    return list(set.intersection(set1,set2))

def flatten(t):
    return [item for sublist in t for item in sublist]

def remove_duplicate(l):
    return list(dict.fromkeys(l))