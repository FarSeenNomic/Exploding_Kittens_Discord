# next alphabetical

def nextItemAlphabetical(li, curr):
    """
    Takes a list and returns the items alphabeticlay after the curr
    """
    srot = sorted(li, key=str.lower)
    try:
        ind = 0
        while (srot[ind] <= curr): ind += 1
        return srot[ind]
    except:
        return srot[0]

def lastItemAlphabetical(li, curr):
    """
    Takes a list and returns the items alphabeticlay before the curr
    """
    srot = sorted(li, key=str.lower)
    try:
        ind = 0
        while (srot[ind] < curr): ind += 1
        ind -= 1
        return srot[ind]
    except:
        return srot[-1]
