"""
Simple helper functions
"""

def other_faction(faction):
    if faction == "Light":
        return "Dark"
    elif faction == "Dark":
        return "Light"
    else:
        raise NameError("faction cannot be {}".format(faction))

# used for printing out board state
def display_list(ls):
    return ''.join(['\n  {}'.format(item) for item in ls])
