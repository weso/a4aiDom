__author__ = 'guillermo'

import random


def success(data):
    return {"success": True, "data": data}


def error(text=""):
    return {"success": False, "error": text}


def uri(element, element_code, level, url_root=None):
    element["uri"] = "%s%s/%s" % (url_root, level, element[element_code])


def normalize_group_name(original):
    """
    Ite receives a stirng containing a name of a component, subindex or index and returns
    it uppercased and replacing " " by "_"
    :param original:
    :return:
    """
    if original is None:
        return None
    else:
        result = original.upper().replace(" ", "_").replace("-", "_")
        while "__" in result:
            result.replace("__", "_")
        return result


def random_int(first, last):
    return random.randint(first, last)


def random_float(first, last):
    return random.random() * (first - last) + first + 1
