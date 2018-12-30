def count_by(iterable, f):
    res = {}
    for i in iterable:
        x = f(i)
        res[x] = res.get(x, 0) + 1
    return res


def group_by(iterable, f):
    res = {}
    for i in iterable:
        x = f(i)
        l = res.get(x)
        if l is None:
            l = []
            res[x] = l
        l.append(i)
    return res
